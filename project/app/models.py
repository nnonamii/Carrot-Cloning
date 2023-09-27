from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(verbose_name="제목", max_length=200)
    price = models.IntegerField(verbose_name="가격")
    description = models.TextField(verbose_name="설명")
    location = models.CharField(verbose_name="지역", max_length=100)
    images = models.ImageField(verbose_name="이미지", upload_to="post_images/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field="username")
    created_at = models.DateTimeField(verbose_name="작성일자", auto_now_add=True, null=True)

    product_reserved = models.CharField(verbose_name="예약여부", max_length=1, default="N")
    product_sold = models.CharField(verbose_name="판매여부", max_length=1, default="N")

    view_num = models.PositiveIntegerField(verbose_name="조회수", default=0)
    chat_num = models.PositiveIntegerField(verbose_name="채팅수", default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    region = models.CharField(max_length=100, null=True)
    region_certification = models.CharField(max_length=1, default="N")

    def __str__(self):
        return f"{self.user.username} Profile"
    
    
class ChatRoom(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_name")
    created_dt = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_dt']

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_name")
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="chat_room")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    



class Job(models.Model):
    title               = models.CharField(verbose_name='제목',max_length=200)
    price               = models.IntegerField(verbose_name='시급')
    description         = models.TextField(verbose_name='설명')
    location            = models.CharField(verbose_name='지역',max_length=100)
    images              = models.ImageField(verbose_name='이미지',upload_to='jobs_images/') 
    user                = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field='username')
    working_days        = models.CharField(verbose_name='근무 요일',max_length=100)
    working_time        = models.CharField(verbose_name='근무 시간',max_length=100)
    created_at          = models.DateTimeField(verbose_name='작성일자',auto_now_add=True, null=True) 

    product_sold = models.CharField(verbose_name="마감여부", max_length=1, default="N")

    view_num = models.PositiveIntegerField(verbose_name="조회수", default=0)
    chat_num = models.PositiveIntegerField(verbose_name="채팅수", default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class Realty(models.Model):
    title = models.CharField(verbose_name="제목", max_length=200)
    property_type = models.CharField(verbose_name="매물종류", max_length=50, default="아파트")
    deposit = models.IntegerField(verbose_name="보증금")
    monthly_rent = models.IntegerField(verbose_name="월세")
    area = models.IntegerField(verbose_name="면적")
    rooms = models.IntegerField(verbose_name="방개수")
    floor = models.IntegerField(verbose_name="층")
    available_date = models.DateTimeField(verbose_name="입주가능일", auto_now_add=True, null=True)
    pet = models.CharField(verbose_name="반려동물", max_length=1, default="N")
    parking = models.CharField(verbose_name="주차", max_length=1, default="N")
    elevator = models.CharField(verbose_name="엘리베이터", max_length=1, default="N")
    description = models.TextField(verbose_name="설명")
    location = models.CharField(verbose_name="지역", max_length=100)
    images = models.ImageField(verbose_name="이미지", upload_to="post_images/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field="username")

    created_at = models.DateTimeField(verbose_name="작성일자", auto_now_add=True, null=True)

    product_sold = models.CharField(verbose_name="거래여부", max_length=1, default="N")

    view_num = models.PositiveIntegerField(verbose_name="조회수", default=0)
    chat_num = models.PositiveIntegerField(verbose_name="채팅수", default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]

class Oldcar(models.Model):
    title = models.CharField(verbose_name="제목", max_length=200)
    price = models.IntegerField(verbose_name="가격")
    car_info = models.TextField(verbose_name="차량 정보")
    insurance_history = models.TextField(verbose_name="보험 이력")
    description = models.TextField(verbose_name="설명")
    location = models.CharField(verbose_name="지역", max_length=100)
    images = models.ImageField(verbose_name="이미지", upload_to="oldcar_images/")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field="username")
    created_at = models.DateTimeField(verbose_name="작성일자", auto_now_add=True, null=True)
    product_sold = models.CharField(verbose_name="마감여부", max_length=1, default="N")
    view_num = models.PositiveIntegerField(verbose_name="조회수", default=0)
    chat_num = models.PositiveIntegerField(verbose_name="채팅수", default=0)

