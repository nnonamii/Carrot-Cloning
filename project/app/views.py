from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages

from .models import Post, UserProfile
from django.db.models import Q
# Create your views here.
import requests, json, base64, time
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR / '.secrets'
secret = json.load(open(os.path.join(SECRETS_DIR, 'secret.json')))

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

def payments(request):
  return render(request,'payments/index.html',)

def success(request):
  orderId = request.GET.get('orderId')
  amount = request.GET.get('amount')
  paymentKey = request.GET.get('paymentKey')
  
  url = "https://api.tosspayments.com/v1/payments/confirm"

  secretKey = secret["TOSS_API_KEY"]
  userpass = secretKey + ':'
  encoded_u = base64.b64encode(userpass.encode()).decode()
  
  headers = {"Authorization" : "Basic %s" % encoded_u,"Content-Type": "application/json"}
  
  params = {
    "orderId" : orderId,
    "amount" : amount,
    "paymentKey": paymentKey,
  }
  
  res = requests.post(url, data=json.dumps(params), headers=headers)
  resjson = res.json()
  pretty = json.dumps(resjson, indent=4)

  respaymentKey = resjson["paymentKey"]
  resorderId = resjson["orderId"]
  

  return render(request,"payments/success.html",{"res" : pretty,"respaymentKey" : respaymentKey,"resorderId" : resorderId,})

def fail(request):
  code = request.GET.get('code')
  message = request.GET.get('message')
  
  return render(request,"payments/fail.html",{"code" : code,"message" : message,})
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

def jobs(request):
    return render(request, 'jobs.html')

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