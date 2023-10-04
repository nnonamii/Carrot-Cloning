from django.http import JsonResponse
from django.contrib import messages

from .forms import (
    CustomLoginForm,
    CustomRegistrationForm,
    PostForm,
    OldcarForm,
    StoreForm,
    JobsForm,
    RealtyForm,
)
from .models import Post, UserProfile, Oldcar, Chat, ChatRoom, Job, Store, Realty
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from selenium import webdriver
from selenium.webdriver.common.by import By
import openai

from django.db.models import Q, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Extract
from django.utils import timezone

# Create your views here.
import requests, json, base64, time
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR / ".secrets"
secret = json.load(open(os.path.join(SECRETS_DIR, "secret.json")))


def main(request):
    return render(request, "main.html")


def alert(request, alert_message):
    return render(request, "alert.html", {"alert_message": alert_message})


def chat(request, room_name, pk):
    post = get_object_or_404(Post, pk=pk)
    user = User.objects.get(username=room_name)
    login_user = request.user
    live_chat_room = ChatRoom.objects.get_or_create(user=user, post=post)
    try:
        login_user_info = User.objects.get(username=login_user)
        login_post_info = Post.objects.filter(user=login_user_info)
        chat_room_ids = (
            Chat.objects.filter(user=login_user_info).values_list("chat_room", flat=True).distinct()
        )

        chat_rooms = ChatRoom.objects.filter(Q(id__in=chat_room_ids) | Q(post__in=login_post_info))
        post_ids = chat_rooms.values_list("post", flat=True)
        posts = Post.objects.filter(id__in=post_ids)

        other_user_chat = (
            Chat.objects.filter(chat_room__in=chat_rooms).exclude(user=login_user_info).distinct()
        )
        other_user = User.objects.get(id=other_user_chat[0].user_id)

        chat_room_list = zip(chat_rooms, posts)
    except Chat.DoesNotExist:
        chat_room_ids = None
    except ChatRoom.DoesNotExist:
        chat_rooms = None

    data = {
        "user": login_user,
        "other_user": other_user,
        "room_name": room_name,
        "post": post,
        "live_chat_room": live_chat_room,
        "chat_room_list": chat_room_list,
    }
    return render(request, "chat.html", data)


def chat_message(request):
    if request.method == "POST":
        message = request.POST["message"]
        room_name = request.POST["room_name"]
        post_id = request.POST["post_id"]
        seller = User.objects.get(username=room_name)
        post = Post.objects.get(pk=post_id)
        chat_room = get_object_or_404(ChatRoom, user=seller, post=post)

        chat = Chat.objects.create(chat_room=chat_room, user=request.user, message=message)
        chat.save()

        return JsonResponse({"status": "success", "message": "Message saved successfully."})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)


def get_chat_messages(request, room, post_id):
    try:
        seller = User.objects.get(username=room)
        post = Post.objects.get(pk=post_id)
        chat_room = ChatRoom.objects.get(user=seller, post=post)
        chat_messages = Chat.objects.filter(chat_room=chat_room).order_by("timestamp")
        messages = [
            {
                "user": chat_message.user.username,
                "message": chat_message.message,
                "timestamp": chat_message.timestamp,
            }
            for chat_message in chat_messages
        ]
        return JsonResponse({"messages": messages})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"error": "Chat room not found"}, status=404)


def login_alert(request):
    return render(request, "user/login_alert.html")


def trade(request):
    top_views_posts = (
        Post.objects.filter(product_sold="N")
        .annotate(
            view_rank=ExpressionWrapper(-F("view_num"), output_field=IntegerField()),
            creation_year=Extract("created_at", "year"),
            creation_month=Extract("created_at", "month"),
            creation_day=Extract("created_at", "day"),
            creation_hour=Extract("created_at", "hour"),
            creation_minute=Extract("created_at", "minute"),
        )
        .order_by(
            "view_rank",
            "-creation_year",
            "-creation_month",
            "-creation_day",
            "-creation_hour",
            "-creation_minute",
        )
    )
    return render(request, "trade/trade.html", {"posts": top_views_posts})


def trade_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user.is_authenticated:
        if request.user != post.user:
            post.view_num += 1
            post.save()
    else:
        post.view_num += 1
        post.save()

    try:
        user_profile = UserProfile.objects.get(user=post.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    context = {
        "post": post,
        "user_profile": user_profile,
    }

    return render(request, "trade/trade_post.html", context)


def bump_trade(request, pk):
    # 게시물 조회
    post = get_object_or_404(Post, pk=pk)

    # 게시물의 created_at 필드를 현재 일시로 업데이트
    post.created_at = timezone.now()
    post.save()

    # 업데이트 후, 해당 게시물의 상세 페이지로 리디렉션
    return redirect("trade_post", pk=pk)


def custom_login(request):
    if request.user.is_authenticated:  # 이미 로그인 했으면
        return redirect("main")

    else:
        form = CustomLoginForm(data=request.POST or None)  # forms.py에서 생성한 폼 가져오기
        if request.method == "POST":  # post 요청 보내면
            if form.is_valid():
                username = form.cleaned_data[
                    "username"
                ]  # cleaned_data는 사용자가 제출한 아이디(또는 다른 필드)의 정제된(cleaned) 값에 접근
                password = form.cleaned_data["password"]

                user = authenticate(request, username=username, password=password)

                if user is not None:  # 회원일 때
                    login(request, user)
                    return redirect("main")
        return render(request, "user/login.html", {"form": form})


def custom_register(request):
    error_message = ""
    # 회원 가입 버튼을 눌렀을 때
    if request.method == "POST":
        form = CustomRegistrationForm(request.POST)  # 회원 가입 폼 데이터 가져오기
        username = request.POST.get("username")
        # 아이디가 이미 존재하는 지를 따진다
        if User.objects.filter(username=username).exists():
            error_message = "이미 존재하는 아이디입니다."
        # 존재하는 회원이 없을 때
        elif form.is_valid():
            # cleaned_data는 사용자가 제출한 데이터의 정제된 것을 가져온다
            password = form.cleaned_data["password"]
            check_password = form.cleaned_data["check_password"]

            # 비밀번호 일치 여부를 확인
            if password == check_password:
                # 새로운 유저를 생성
                user = User.objects.create_user(username=username, password=password)

                # 유저를 로그인 상태로 만듦
                login(request, user)

                return redirect("login")
            else:
                form.add_error("check_password", "Passwords do not match")
    else:
        form = CustomRegistrationForm()

    return render(request, "user/register.html", {"form": form, "error_message": error_message})


# @login_required
def write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.region_certification == "Y":
            return render(request, "trade/write.html")
        else:
            return redirect("alert", alert_message="동네인증이 필요합니다.")
    except UserProfile.DoesNotExist:
        return redirect("alert", alert_message="동네인증이 필요합니다.")
    except:
        return redirect("login_alert")


def edit(request, id):
    post = get_object_or_404(Post, id=id)
    if post:
        post.description = post.description.strip()
    if request.method == "POST":
        post.title = request.POST["title"]
        post.price = request.POST["price"]
        post.description = request.POST["description"]
        post.location = request.POST["location"]
        if "images" in request.FILES:
            post.images = request.FILES["images"]
        post.save()
        return redirect("trade_post", pk=id)
    return render(request, "trade/write.html", {"post": post})


def delete(request, id):
    try:
        post = Post.objects.get(id=id)
        post.delete()
        messages.success(request, "삭제되었습니다.")
    except Post.DoesNotExist:
        messages.error(request, "포스팅을 찾을 수 없습니다.")
    return redirect("trade")


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("trade_post", pk=post.pk)
        else:
            form = PostForm()
    return render(request, "trade/trade_post.html", {"form": form})


def payments(request, pk):
    post = get_object_or_404(Post, id=pk)
    return render(request, "payments/index.html", {"post": post})


def success(request):
    orderId = request.GET.get("orderId")
    amount = request.GET.get("amount")
    paymentKey = request.GET.get("paymentKey")
    orderName = request.GET.get("orderName")
    url = "https://api.tosspayments.com/v1/payments/confirm"

    secretKey = secret["TOSS_API_KEY"]
    userpass = secretKey + ":"
    encoded_u = base64.b64encode(userpass.encode()).decode()

    headers = {"Authorization": "Basic %s" % encoded_u, "Content-Type": "application/json"}

    params = {
        "orderId": orderId,
        "amount": amount,
        "paymentKey": paymentKey,
        "orderName": orderName,
    }

    res = requests.post(url, data=json.dumps(params), headers=headers)
    resjson = res.json()
    pretty = json.dumps(resjson, indent=4)

    respaymentKey = resjson["paymentKey"]
    resorderId = resjson["orderId"]
    resorderName = resjson["orderName"].split("|")[1]
    post = get_object_or_404(Post, pk=resorderName)
    user = post.user_id
    post.product_sold = "Y"
    post.save()

    return redirect("chat", room_name=user, pk=resorderName)


def fail(request):
    code = request.GET.get("code")
    message = request.GET.get("message")

    return render(
        request,
        "payments/fail.html",
        {
            "code": code,
            "message": message,
        },
    )


def search(request):
    query = request.GET.get("search")
    if query:
        results = Post.objects.filter(Q(title__icontains=query) | Q(location__icontains=query))
    else:
        results = Post.objects.all()

    return render(request, "trade/search.html", {"posts": results})


def location(request):
    try:
        user_profile = UserProfile.objects.get(user_id=request.user)
        region = user_profile.region
    except UserProfile.DoesNotExist:
        region = None

    return render(request, "location.html", {"region": region})


def test(request):
    return render(request, "test.html")


def jobs(request):
    top_views_jobs = Job.objects.filter(product_sold="N").order_by("-view_num")
    return render(request, "jobs/jobs.html", {"jobs": top_views_jobs})


# def oldcar(request):
#     top_views_posts = Oldcar.objects.filter(product_sold="N").order_by("-view_num")
#     return render(request, "oldcar/oldcar.html", {"oldcars": top_views_posts})


def oldcar(request):
    top_views_oldcar = (
        Oldcar.objects.filter(product_sold="N")
        .annotate(
            view_rank=ExpressionWrapper(-F("view_num"), output_field=IntegerField()),
            creation_year=Extract("created_at", "year"),
            creation_month=Extract("created_at", "month"),
            creation_day=Extract("created_at", "day"),
            creation_hour=Extract("created_at", "hour"),
            creation_minute=Extract("created_at", "minute"),
        )
        .order_by(
            "view_rank",
            "-creation_year",
            "-creation_month",
            "-creation_day",
            "-creation_hour",
            "-creation_minute",
        )
    )
    return render(request, "oldcar/oldcar.html", {"oldcars": top_views_oldcar})


def oldcar_post(request, pk):
    oldcar = Oldcar.objects.get(id=pk)

    if request.user.is_authenticated:
        if request.user != oldcar.user:
            oldcar.view_num += 1
            oldcar.save()
    else:
        oldcar.view_num += 1
        oldcar.save()

    try:
        user_profile = UserProfile.objects.get(user=oldcar.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    context = {
        "oldcar": oldcar,
        "user_profile": user_profile,
    }

    return render(request, "oldcar/oldcar_post.html", context)


def oldcar_write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.region_certification == "Y":
            return render(request, "oldcar/oldcar_write.html")
        else:
            return redirect("alert", alert_message="동네인증이 필요합니다.")
    except UserProfile.DoesNotExist:
        return redirect("alert", alert_message="동네인증이 필요합니다.")


def create_oldcar(request):
    if request.method == "POST":
        form = OldcarForm(request.POST, request.FILES)
        if form.is_valid():
            oldcar = form.save(commit=False)
            oldcar.user = request.user
            oldcar.save()
            return redirect("oldcar_post", pk=oldcar.pk)
    else:
        form = OldcarForm()
    return render(request, "oldcar/oldcar_post.html", {"form": form})


def stores(request):
    top_views_stores = Store.objects.order_by("-connexion")
    return render(request, "stores/stores.html", {"stores": top_views_stores})


def stores_post(request, pk):
    store = get_object_or_404(Store, pk=pk)

    if request.user.is_authenticated:
        if request.user != store.user:
            store.save()
    else:
        store.save()

    try:
        user_profile = UserProfile.objects.get(user=store.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    context = {
        "store": store,
        "user_profile": user_profile,
    }

    return render(request, "stores/stores_post.html", context)


def oldcar_edit(request, id):
    oldcar = get_object_or_404(Oldcar, id=id)
    if oldcar:
        oldcar.description = oldcar.description.strip()
    if request.method == "POST":
        oldcar.title = request.POST["title"]
        oldcar.price = request.POST["price"]
        oldcar.description = request.POST["description"]
        oldcar.car_info = request.POST["car_info"]
        oldcar.insurance_history = request.POST["insurance_history"]
        oldcar.location = request.POST["location"]
        if "images" in request.FILES:
            oldcar.images = request.FILES["images"]
        oldcar.save()
        return redirect("oldcar_post", pk=id)
    return render(request, "oldcar/oldcar_write.html", {"oldcar": oldcar})

def oldcar_delete(request, id):
    try:
        oldcar = Oldcar.objects.get(id=id)
        oldcar.delete()
        messages.success(request, "삭제되었습니다.")
    except Oldcar.DoesNotExist:
        messages.error(request, "포스팅을 찾을 수 없습니다.")
    return redirect("oldcar")



def bump_oldcar(request, pk):
    # 게시물 조회
    oldcar = get_object_or_404(Oldcar, pk=pk)

    # 게시물의 created_at 필드를 현재 일시로 업데이트
    oldcar.created_at = timezone.now()
    oldcar.save()

    # 업데이트 후, 해당 게시물의 상세 페이지로 리디렉션
    return redirect("oldcar_post", pk=pk)


def stores_write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.region_certification == "Y":
            return render(request, "stores/stores_write.html")
        else:
            return redirect("alert", alert_message="동네인증이 필요합니다.")
    except UserProfile.DoesNotExist:
        return redirect("alert", alert_message="동네인증이 필요합니다.")
    except:
        return redirect("login_alert")


@login_required
def create_stores(request):
    if request.method == "POST":
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()
            return redirect("stores_post", pk=store.pk)
        else:
            print(form.errors)
    else:
        form = StoreForm()
    return render(request, "stores/stores_post.html", {"form": form})


def stores_edit(request, id):
    store = get_object_or_404(Store, id=id)
    if store:
        store.greetings = store.greetings.strip()
    if request.method == "POST":
        store.store_name = request.POST["store_name"]
        store.location = request.POST["location"]
        store.semi_location = request.POST["semi_location"]
        store.greetings = request.POST["greetings"]
        store.category = request.POST["category"]
        store.days = request.POST["days"]
        store.open_time = request.POST["open_time"]
        store.close_time = request.POST["close_time"]
        if "images" in request.FILES:
            store.images = request.FILES["images"]
        if "menu_items" in request.FILES:
            store.menu_items = request.FILES["menu_items"]
        store.save()
        return redirect("stores_post", pk=id)
    return render(request, "stores/stores_write.html", {"store": store})


def stores_delete(request, id):
    try:
        store = Store.objects.get(id=id)
        store.delete()
        messages.success(request, "삭제되었습니다.")
    except store.DoesNotExist:
        messages.error(request, "포스팅을 찾을 수 없습니다.")
    return redirect("stores")


def bump_stores(request, pk):
    # 게시물 조회
    stores = get_object_or_404(Store, pk=pk)

    # 게시물의 created_at 필드를 현재 일시로 업데이트
    stores.created_at = timezone.now()
    stores.save()

    # 업데이트 후, 해당 게시물의 상세 페이지로 리디렉션
    return redirect("stores_post", pk=pk)
  
def make_connexion_store(request, pk):
    store = get_object_or_404(Store, pk=pk)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if store not in user_profile.favorite_stores.all():
        store.connexion += 1
        store.save()
        user_profile.favorite_stores.add(store)
    
    return redirect('stores_post', pk=pk)  # 가게 상세 페이지로 리다이렉트

def remove_connexion_store(request, pk):
    store = get_object_or_404(Store, pk=pk)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if store in user_profile.favorite_stores.all():
        store.connexion -= 1
        store.save()
        user_profile.favorite_stores.remove(store)
    
    return redirect('stores_post', pk=pk)  # 가게 상세 페이지로 리다이렉트

def set_region(request):
    if request.method == "POST":
        region = request.POST.get("region-setting")

        if region:
            try:
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                user_profile.region = region
                user_profile.save()

                return redirect("location")
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})
        else:
            return JsonResponse({"status": "error", "message": "Region cannot be empty"})
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


def set_region_certification(request):
    if request.method == "POST":
        request.user.profile.region_certification = "Y"
        request.user.profile.save()
        messages.success(request, "인증되었습니다")
        return redirect("location")


openai.api_key = secret["AI_API_KEY"]


def realty_write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.region_certification == "Y":
            return render(request, "realty/realty_write.html")
        else:
            return redirect("alert", alert_message="동네인증이 필요합니다.")
    except UserProfile.DoesNotExist:
        return redirect("alert", alert_message="동네인증이 필요합니다.")
    except:
        return redirect("login_alert")


@login_required
def create_realty(request):
    if request.method == "POST":
        form = RealtyForm(request.POST, request.FILES)
        if form.is_valid():
            realty = form.save(commit=False)
            realty.user = request.user
            realty.save()
            return redirect("realty_post", pk=realty.pk)
        else:
            form = RealtyForm()
    return render(request, "realty/realty_post.html", {"form": form})


def delete_realty(request, id):
    try:
        realty = Realty.objects.get(id=id)
        realty.delete()
        messages.success(request, "삭제되었습니다.")
    except Realty.DoesNotExist:
        messages.error(request, "포스팅을 찾을 수 없습니다.")
    return redirect("realty")


def edit_realty(request, id):
    realty = get_object_or_404(Realty, id=id)
    if realty:
        realty.description = realty.description.strip()
    if request.method == "POST":
        realty.title = request.POST["title"]
        realty.property_type = request.POST["property_type"]
        realty.deposit = request.POST["deposit"]
        realty.monthly_rent = request.POST["monthly_rent"]
        realty.area = request.POST["area"]
        realty.rooms = request.POST["rooms"]
        realty.floor = request.POST["floor"]
        realty.description = request.POST["description"]
        realty.location = request.POST["location"]
        if "images" in request.FILES:
            realty.images = request.FILES["images"]
        realty.save()
        return redirect("realty_post", pk=id)
    return render(request, "realty/realty_write.html", {"realty": realty})


def bump_realty(request, pk):
    # 게시물 조회
    realty = get_object_or_404(Realty, pk=pk)

    # 게시물의 created_at 필드를 현재 일시로 업데이트
    realty.created_at = timezone.now()
    realty.save()

    # 업데이트 후, 해당 게시물의 상세 페이지로 리디렉션
    return redirect("realty_post", pk=pk)


def chatbot(request):
    try:
        login_user = request.user
        login_user_info = User.objects.get(username=login_user)
        login_post_info = Post.objects.filter(user=login_user_info)
        chat_room_ids = (
            Chat.objects.filter(user=login_user_info).values_list("chat_room", flat=True).distinct()
        )

        chat_rooms = ChatRoom.objects.filter(Q(id__in=chat_room_ids) | Q(post__in=login_post_info))
        post_ids = chat_rooms.values_list("post", flat=True)
        posts = Post.objects.filter(id__in=post_ids)

        other_user_chat = (
            Chat.objects.filter(chat_room__in=chat_rooms).exclude(user=login_user_info).distinct()
        )
        other_user = User.objects.get(id=other_user_chat[0].user_id)

        chat_room_list = zip(chat_rooms, posts)
    except Chat.DoesNotExist:
        chat_room_ids = None
    except ChatRoom.DoesNotExist:
        chat_rooms = None
    return render(
        request, "chatbot.html", {"chat_room_list": chat_room_list, "other_user": other_user}
    )


class ChatBot:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.messages = []

    def ask(self, question):
        self.messages.append({"role": "user", "content": question})
        res = self.__ask__()
        return res

    def __ask__(self):
        completion = openai.ChatCompletion.create(
            # model 지정
            model=self.model,
            messages=self.messages,
        )
        response = completion.choices[0].message["content"]
        self.messages.append({"role": "assistant", "content": response})
        return response

    def show_messages(self):
        return self.messages

    def clear(self):
        self.messages.clear()


def execute_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        question = data.get("question")
        chatbot = ChatBot()
        response = chatbot.ask(question)
        return JsonResponse({"response": response})


def realty(request):
    # 게시물을 조회수와 작성일자에 따라 정렬합니다.
    top_views_realty = (
        Realty.objects.filter(product_sold="N")
        .annotate(
            view_rank=ExpressionWrapper(-F("view_num"), output_field=IntegerField()),
            creation_year=Extract("created_at", "year"),
            creation_month=Extract("created_at", "month"),
            creation_day=Extract("created_at", "day"),
            creation_hour=Extract("created_at", "hour"),
            creation_minute=Extract("created_at", "minute"),
        )
        .order_by(
            "view_rank",
            "-creation_year",
            "-creation_month",
            "-creation_day",
            "-creation_hour",
            "-creation_minute",
        )
    )

    return render(request, "realty/realty.html", {"realty": top_views_realty})


def realty_post(request, pk):
    realty = get_object_or_404(Realty, pk=pk)

    if request.user.is_authenticated:
        if request.user != realty.user:
            realty.view_num += 1
            realty.save()
    else:
        realty.view_num += 1
        realty.save()

    try:
        user_profile = UserProfile.objects.get(user=realty.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    context = {
        "realty": realty,
        "user_profile": user_profile,
    }

    return render(request, "realty/realty_post.html", context)


def jobs_write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)

        if user_profile.region_certification == "Y":
            return render(request, "jobs/jobs_write.html")
        else:
            return redirect("alert", alert_message="동네인증이 필요합니다.")
    except UserProfile.DoesNotExist:
        return redirect("alert", alert_message="동네인증이 필요합니다.")
    except:
        return redirect("login_alert")


@login_required
def create_job(request):
    if request.method == "POST":
        form = JobsForm(request.POST, request.FILES)
        if form.is_valid():
            jobs = form.save(commit=False)
            jobs.user = request.user
            jobs.save()
            return redirect("jobs_post", pk=jobs.pk)
        else:
            print(form.errors)
    else:
        form = JobsForm()
    return render(request, "jobs/jobs_post.html", {"form": form})


def jobs_post(request, pk):
    jobs = get_object_or_404(Job, pk=pk)

    if request.user.is_authenticated:
        if request.user != jobs.user:
            jobs.view_num += 1
            jobs.save()
    else:
        jobs.view_num += 1
        jobs.save()

    try:
        user_profile = UserProfile.objects.get(user=jobs.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    context = {
        "jobs": jobs,
        "user_profile": user_profile,
    }

    return render(request, "jobs/jobs_post.html", context)


def delete_jobs(request, id):
    try:
        jobs = Job.objects.get(id=id)
        jobs.delete()
        messages.success(request, "삭제되었습니다.")
    except Job.DoesNotExist:
        messages.error(request, "포스팅을 찾을 수 없습니다.")
    return redirect("jobs")


def edit_jobs(request, id):
    jobs = get_object_or_404(Job, id=id)
    if jobs:
        jobs.description = jobs.description.strip()
    if request.method == "POST":
        jobs.title = request.POST["title"]
        jobs.price = request.POST["price"]
        jobs.description = request.POST["description"]
        jobs.location = request.POST["location"]
        jobs.working_days = request.POST["working_days"]
        jobs.working_time = request.POST["working_time"]
        if "images" in request.FILES:
            jobs.images = request.FILES["images"]
        jobs.save()
        return redirect("jobs_post", pk=id)
    return render(request, "jobs/jobs_write.html", {"jobs": jobs})


def bump_jobs(request, pk):
    # 게시물 조회
    jobs = get_object_or_404(Job, pk=pk)

    # 게시물의 created_at 필드를 현재 일시로 업데이트
    jobs.created_at = timezone.now()
    jobs.save()

    # 업데이트 후, 해당 게시물의 상세 페이지로 리디렉션
    return redirect("jobs_post", pk=pk)


def coupang(request):
    try:
        login_user = request.user
        login_user_info = User.objects.get(username=login_user)
        login_post_info = Post.objects.filter(user=login_user_info)
        chat_room_ids = (
            Chat.objects.filter(user=login_user_info).values_list("chat_room", flat=True).distinct()
        )

        chat_rooms = ChatRoom.objects.filter(Q(id__in=chat_room_ids) | Q(post__in=login_post_info))
        post_ids = chat_rooms.values_list("post", flat=True)
        posts = Post.objects.filter(id__in=post_ids)

        other_user_chat = (
            Chat.objects.filter(chat_room__in=chat_rooms).exclude(user=login_user_info).distinct()
        )
        other_user = User.objects.get(id=other_user_chat[0].user_id)

        chat_room_list = zip(chat_rooms, posts)
    except Chat.DoesNotExist:
        chat_room_ids = None
    except ChatRoom.DoesNotExist:
        chat_rooms = None
    return render(
        request, "coupang.html", {"chat_room_list": chat_room_list, "other_user": other_user}
    )


def execute_coupang(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        question = data.get("question")
        driver = webdriver.Chrome()
        url = "https://www.coupang.com/np/search?component=&q={}&channel=user".format(question)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, 300);")
        driver.implicitly_wait(5)
        name_element = driver.find_element(By.CSS_SELECTOR, "div.name")
        name = name_element.text
        price_element = driver.find_element(By.CSS_SELECTOR, "strong.price-value")
        price = price_element.text
        response = f"상품정보 : {name}<br>----------------<br> 가격 : {price}원"
        driver.quit()
        return JsonResponse({"response": response})
