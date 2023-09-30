from django.http import JsonResponse
from django.contrib import messages
from .models import Post, UserProfile, Oldcar, Chat, ChatRoom, Job
from .forms import CustomLoginForm, CustomRegistrationForm, PostForm, OldcarForm, JobsForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

import openai

from .models import Post, UserProfile, Realty
from django.db.models import Q

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
        chat_room_ids = Chat.objects.filter(user=login_user_info).values_list('chat_room', flat=True).distinct()
        
        chat_rooms = ChatRoom.objects.filter(Q(id__in=chat_room_ids) | Q(post__in=login_post_info))
        post_ids = chat_rooms.values_list('post', flat=True)
        posts = Post.objects.filter(id__in=post_ids)
        
        other_user_chat = Chat.objects.filter(chat_room__in=chat_rooms).exclude(user=login_user_info).distinct()
        other_user = User.objects.get(id=other_user_chat[0].user_id)
    
        chat_room_list =  zip(chat_rooms, posts)
    except Chat.DoesNotExist:
        chat_room_ids = None
    except ChatRoom.DoesNotExist:
        chat_rooms = None
    
    data = {
        "user":login_user,
        "other_user":other_user, 
        "room_name":room_name, 
        "post": post,
        "live_chat_room": live_chat_room,
        "chat_room_list": chat_room_list
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
        chat_messages = Chat.objects.filter(chat_room=chat_room).order_by('timestamp')
        messages = [{'user': chat_message.user.username, 'message': chat_message.message, 'timestamp': chat_message.timestamp} for chat_message in chat_messages]
        return JsonResponse({'messages': messages})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except ChatRoom.DoesNotExist:
        return JsonResponse({'error': 'Chat room not found'}, status=404)

def login_alert(request):
    return render(request, "user/login_alert.html")




def trade(request):
    top_views_posts = Post.objects.filter(product_sold="N").order_by("-view_num")
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
    return render(request,"payments/index.html",{"post":post})


def success(request):
    orderId = request.GET.get("orderId")
    amount = request.GET.get("amount")
    paymentKey = request.GET.get("paymentKey")

    url = "https://api.tosspayments.com/v1/payments/confirm"

    secretKey = secret["TOSS_API_KEY"]
    userpass = secretKey + ":"
    encoded_u = base64.b64encode(userpass.encode()).decode()

    headers = {"Authorization": "Basic %s" % encoded_u, "Content-Type": "application/json"}

    params = {
        "orderId": orderId,
        "amount": amount,
        "paymentKey": paymentKey,
    }

    res = requests.post(url, data=json.dumps(params), headers=headers)
    resjson = res.json()
    pretty = json.dumps(resjson, indent=4)

    respaymentKey = resjson["paymentKey"]
    resorderId = resjson["orderId"]

    return render(
        request,
        "payments/success.html",
        {
            "res": pretty,
            "respaymentKey": respaymentKey,
            "resorderId": resorderId,
        },
    )


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


def oldcar(request):
    top_views_posts = Oldcar.objects.filter(product_sold="N").order_by("-view_num")
    return render(request, "oldcar/oldcar.html", {"odlcars": top_views_posts})


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
    return render(request, "stores/stores.html")


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


def realty(request):
    top_views_posts = Post.objects.filter(product_sold="N").order_by("-view_num")
    return render(request, "realty/realty.html", {"posts": top_views_posts})

openai.api_key = secret['AI_API_KEY']

def chatbot(request):
    try:
        login_user = request.user
        login_user_info = User.objects.get(username=login_user)
        login_post_info = Post.objects.filter(user=login_user_info)
        chat_room_ids = Chat.objects.filter(user=login_user_info).values_list('chat_room', flat=True).distinct()
        
        chat_rooms = ChatRoom.objects.filter(Q(id__in=chat_room_ids) | Q(post__in=login_post_info))
        post_ids = chat_rooms.values_list('post', flat=True)
        posts = Post.objects.filter(id__in=post_ids)
        
        other_user_chat = Chat.objects.filter(chat_room__in=chat_rooms).exclude(user=login_user_info).distinct()
        other_user = User.objects.get(id=other_user_chat[0].user_id)
    
        chat_room_list =  zip(chat_rooms, posts)
    except Chat.DoesNotExist:
        chat_room_ids = None
    except ChatRoom.DoesNotExist:
        chat_rooms = None
    return render(request, "chatbot.html",{"chat_room_list":chat_room_list, "other_user":other_user})

class ChatBot():
    def __init__(self, model='gpt-3.5-turbo'):
        self.model = model
        self.messages = []
        
    def ask(self, question):
        self.messages.append({
            'role': 'user', 
            'content': question
        })
        res = self.__ask__()
        return res
        
    def __ask__(self):
        completion = openai.ChatCompletion.create(
            # model 지정
            model=self.model,
            messages=self.messages
        )
        response = completion.choices[0].message['content']
        self.messages.append({
            'role': 'assistant', 
            'content': response
        })
        return response
    
    def show_messages(self):
        return self.messages
    
    def clear(self):
        self.messages.clear()

def execute_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        question = data.get('question')
        chatbot = ChatBot()
        response = chatbot.ask(question)
        return JsonResponse({"response": response})
    
    


def realty_post(request, pk):
    post = get_object_or_404(Realty, pk=pk)

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