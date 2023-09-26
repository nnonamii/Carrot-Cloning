from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.main, name='main'),
    path("alert/<str:alert_message>/", views.alert, name="alert"),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),
    path('register/', views.custom_register, name='register'),
    path('write/', views.write, name='write'),
    path("edit/<int:id>/", views.edit, name="edit"),
    path("create_form/", views.create_post, name="create_form"),
    path('search/', views.search, name='search'),
    path('trade/', views.trade, name='trade'),
    path('trade_post/', views.trade_post, name='trade_post'),
    path('location/', views.location, name='location'),
    path('chat/', views.chat, name='chat'),
    path('chat_post/', views.chat_post, name='chat_post'),
    path('test/', views.test, name='test'),
    path('set_region/', views.set_region, name='set_region'),
    path('set_region_certification/', views.set_region_certification, name='set_region_certification'),
    path('jobs/', views.jobs, name='jobs'),
    path('payments/', views.payments, name='payments'),
    path('success/', views.success, name='success'),
    path('fail/', views.fail, name='fail'),
    path("realty/", views.realty, name="realty"),
]