from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Post(models.Model):
    title               = models.CharField(verbose_name='제목',max_length=200)
    price               = models.IntegerField(verbose_name='가격')
    description         = models.TextField(verbose_name='설명')
    location            = models.CharField(verbose_name='지역',max_length=100)
    images              = models.ImageField(verbose_name='이미지',upload_to='post_images/') 
    user                = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field='username')
    created_at          = models.DateTimeField(verbose_name='작성일자',auto_now_add=True, null=True) 

    product_reserved    = models.CharField(verbose_name='예약여부',max_length=1, default='N')
    product_sold        = models.CharField(verbose_name='판매여부',max_length=1, default='N')

    view_num            = models.PositiveIntegerField(verbose_name='조회수',default=0)
    chat_num            = models.PositiveIntegerField(verbose_name='채팅수',default=0)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    user                = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    region              = models.CharField(max_length=100, null=True)
    region_certification = models.CharField(max_length=1, default='N')

    def __str__(self):
        return f'{self.user.username} Profile'
    
class Chat(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    message             = models.TextField()
    timestamp           = models.DateTimeField(auto_now_add=True)

class Job(models.Model):
    title               = models.CharField(verbose_name='제목',max_length=200)
    price               = models.IntegerField(verbose_name='시급')
    description         = models.TextField(verbose_name='설명')
    location            = models.CharField(verbose_name='지역',max_length=100)
    images              = models.ImageField(verbose_name='이미지',upload_to='post_images/') 
    user                = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field='username')
    working_days        = models.CharField(verbose_name='근무 요일',max_length=100)
    working_time        = models.CharField(verbose_name='근무 시간',max_length=100)
    created_at          = models.DateTimeField(verbose_name='작성일자',auto_now_add=True, null=True) 

    product_sold        = models.CharField(verbose_name='마감여부',max_length=1, default='N')

    view_num            = models.PositiveIntegerField(verbose_name='조회수',default=0)
    chat_num            = models.PositiveIntegerField(verbose_name='채팅수',default=0)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']