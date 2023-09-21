from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.html')

def chat(request):
    return render(request, 'chat.html')

def trade(request):
    return render(request, 'trade.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def write(request):
    return render(request, 'write.html')

def search(request):
    return render(request, 'search.html')

def trade_post(request):
    return render(request, 'trade_post.html')

def location(request):
    return render(request, 'location.html')

def chat_post(request):
    return render(request, 'chat_post.html')

def test(request):
    return render(request, 'test.html')