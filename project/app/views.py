from django.shortcuts import render, redirect, get_object_or_404

from .models import Post, UserProfile
from .forms import CustomLoginForm, CustomRegistrationForm, PostForm

# Create your views here.


def main(request):
    return render(request, "main.html")


def alert(request, alert_message):
    return render(request, "alert.html", {"alert_message": alert_message})


def chat(request):
    return render(request, "chat.html")


def trade(request):
    return render(request, "trade.html")


def login(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


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
