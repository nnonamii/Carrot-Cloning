from .models import Post, UserProfile
from .forms import CustomLoginForm, CustomRegistrationForm, PostForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# Create your views here.


def main(request):
    return render(request, "main.html")


def alert(request, alert_message):
    return render(request, "alert.html", {"alert_message": alert_message})


def chat(request):
    return render(request, "chat.html")


def trade(request):
    return render(request, "trade.html")


def custom_login(request):
    if request.user.is_authenticated: #이미 로그인 했으면
        return redirect('main')
    
    else:
        form = CustomLoginForm(data=request.POST or None) # forms.py에서 생성한 폼 가져오기
        if request.method == "POST": # post 요청 보내면

            if form.is_valid():
                username = form.cleaned_data['username'] # cleaned_data는 사용자가 제출한 아이디(또는 다른 필드)의 정제된(cleaned) 값에 접근
                password = form.cleaned_data['password']

                user = authenticate(request, username=username, password=password)

                if user is not None: # 회원일 때
                    login(request, user) 
                    return redirect('main')  
        return render(request, 'login.html', {'form': form}) 

def custom_register(request):
    error_message = ''
    # 회원 가입 버튼을 눌렀을 때
    if request.method == 'POST': 
        form = CustomRegistrationForm(request.POST) # 회원 가입 폼 데이터 가져오기
        username = request.POST.get('username')
        # 아이디가 이미 존재하는 지를 따진다
        if User.objects.filter(username=username).exists():
            error_message = "이미 존재하는 아이디입니다."
        # 존재하는 회원이 없을 때
        elif form.is_valid():
            #cleaned_data는 사용자가 제출한 데이터의 정제된 것을 가져온다
            password = form.cleaned_data['password']
            check_password = form.cleaned_data['check_password']
            
            # 비밀번호 일치 여부를 확인
            if password == check_password:
                # 새로운 유저를 생성
                user = User.objects.create_user(username=username, password=password)
                
                # 유저를 로그인 상태로 만듦
                login(request, user)
            
            
                return redirect('login')
            else:
                form.add_error('check_password', 'Passwords do not match')
    else:
        form = CustomRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'error_message': error_message})


def write(request):
    # try:
    #     user_profile = UserProfile.objects.get(user=request.user)

    #     if user_profile.region_certification == "Y":
    #         return render(request, "write.html")
    #     else:
    #         return redirect("alert", alert_message="동네인증이 필요합니다.")
    # except UserProfile.DoesNotExist:
    #     return redirect("alert", alert_message="동네인증이 필요합니다.")
    return render(request, "write.html")


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
    return render(request, "write.html", {"post": post})


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
    return render(request, "trade_post.html", {"form": form})


def search(request):
    return render(request, "search.html")


def trade_post(request):
    return render(request, "trade_post.html")


def location(request):
    return render(request, "location.html")


def chat_post(request):
    return render(request, "chat_post.html")


def test(request):
    return render(request, "test.html")


def realty(request):
    return render(request, "realty.html")
