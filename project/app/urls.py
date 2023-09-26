from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('write/', views.write, name='write'),
    path('search/', views.search, name='search'),
    path('trade/', views.trade, name='trade'),
    path('trade_post/', views.trade_post, name='trade_post'),
    path('location/', views.location, name='location'),
    path('chat/', views.chat, name='chat'),
    path('chat_post/', views.chat_post, name='chat_post'),
    path('test/', views.test, name='test'),
    path('set_region/', views.set_region, name='set_region'),
]