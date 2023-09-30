from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


# app_name = "app"

urlpatterns = [
    path("", views.main, name="main"),
    path("alert/<str:alert_message>/", views.alert, name="alert"),
    path("login_alert/", views.login_alert, name="login_alert"),
    path("login/", views.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="main"), name="logout"),
    path("register/", views.custom_register, name="register"),
    path("write/", views.write, name="write"),
    path("edit/<int:id>/", views.edit, name="edit"),
    path("delete/<int:id>/", views.delete, name="delete"),
    path("create_form/", views.create_post, name="create_form"),
    path("search/", views.search, name="search"),
    path("trade/", views.trade, name="trade"),
    path("trade_post/<int:pk>/", views.trade_post, name="trade_post"),
    path("location/", views.location, name="location"),
    path("chat/<str:room_name>/<int:pk>/", views.chat, name="chat"),
    path("test/", views.test, name="test"),
    path("set_region/", views.set_region, name="set_region"),
    path("set_region_certification/", views.set_region_certification, name="set_region_certification"),
    path("jobs/", views.jobs, name="jobs"),
    path("stores/", views.stores, name="stores"),
    path("payments/<int:pk>/", views.payments, name="payments"),
    path("success/", views.success, name="success"),
    path("fail/", views.fail, name="fail"),
    path("realty/", views.realty, name="realty"),
    path("realty_post/<int:pk>/", views.realty_post, name="realty_post"),
    path("oldcar/", views.oldcar, name="oldcar"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path('execute_chatbot/', views.execute_chatbot, name='execute_chatbot'),
    path("oldcar_post/<str:pk>/", views.oldcar_post, name="oldcar_post"),
    path("oldcar_write/", views.oldcar_write, name="oldcar_write"),
    path("oldcar_create_form/", views.create_oldcar, name="oldcar_create_form"),
    path("chat_message/", views.chat_message, name="chat_message"),
    path("get_chat_messages/<str:room>/<int:post_id>/", views.get_chat_messages, name="get_chat_messages"),
    path("jobs_write/",views.jobs_write, name="jobs_write"),
    path("jobs_create_form/", views.create_job, name="create_job"),
    path("jobs_post/<int:pk>/", views.jobs_post, name="jobs_post"),
    path("delete_jobs/<int:id>/", views.delete_jobs, name="delete_jobs"),
    path("edit_jobs/<int:id>/", views.edit_jobs, name="edit_jobs"),
]
