from django.db import models

# Create your models here.
class Post(models.Model):
    title       = models.CharField(verbose_name="제목", max_length=100)
    location    = models.CharField(verbose_name="지역",max_length=100)
    img         = models.CharField(verbose_name="이미지",max_length=100)
    description = models.TextField(verbose_name="설명")   
    user_id     = models.IntegerField(verbose_name="작성자 ID")
    price       = models.IntegerField(verbose_name="가격")
    view_num    = models.IntegerField(verbose_name="조회수",default=0)
    chat_num    = models.IntegerField(verbose_name="채팅수",default=0)
    created_dt  = models.DateTimeField(verbose_name="생성일자",auto_now_add=True)
    
class ChatRoom(models.Model):
    post_id     = models.CharField(verbose_name="상품 ID", max_length=100)
    user_id     = models.IntegerField(verbose_name="수신자 ID")
    created_dt  = models.DateTimeField(verbose_name="생성일자",auto_now_add=True)

class ChatMessage(models.Model):
    chat_room   = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user_id     = models.IntegerField(verbose_name="발신자 ID")
    message     = models.TextField(verbose_name="내용")
    read_or_not = models.BooleanField(verbose_name="읽기 여부", default=False)
    created_dt  = models.DateTimeField(verbose_name="생성일자",auto_now_add=True)    