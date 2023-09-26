from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from .models import Post, UserProfile
from django.db.models import Q
# Create your views here.

def main(request):
    return render(request, 'main.html')

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
    query = request.GET.get('search')
    if query:
        results = Post.objects.filter(Q(title__icontains=query) | Q(location__icontains=query))
    else:
        results = Post.objects.all()
    
    return render(request, 'search.html', {'posts': results})

def trade_post(request):
    return render(request, 'trade_post.html')

def location(request):
    return render(request, 'location.html')

def chat_post(request):
    return render(request, 'chat_post.html')

def test(request):
    return render(request, 'test.html')

def set_region(request):
    if request.method == "POST":
        region = request.POST.get('region-setting')

        if region:
            try:
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                user_profile.region = region
                user_profile.save()

                return redirect('location')
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})
        else:
            return JsonResponse({"status": "error", "message": "Region cannot be empty"})
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)