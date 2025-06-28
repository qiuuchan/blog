import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# 用户表
class User_admin(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    nickName = models.CharField(max_length=255, verbose_name="昵称")
    password = models.CharField(max_length=255, verbose_name="密码")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "user_admin"


# 文章表
class Article(models.Model):
    emuns = [
        (0, '草稿'),
        (1, '发布')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    title = models.CharField(max_length=255, verbose_name="标题")
    tag = models.CharField(max_length=255, verbose_name="标签")
    classify_id = models.CharField(max_length=255, verbose_name="文章分类")
    content = models.TextField(verbose_name="内容")
    status = models.IntegerField(default=0, choices=emuns, verbose_name="状态")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updateTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    class Meta:
        db_table = "article"
        ordering = ('createTime',)


# 分类表
class Classify(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    name = models.CharField(max_length=255, verbose_name="分类名")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "classify"
        ordering = ('createTime',)


# 图片表
class Imgs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4())
    name = models.CharField(max_length=255, verbose_name="图片名称")
    url = models.FileField(upload_to='uploads/%Y%m%d/', verbose_name="图片地址")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "imgs"
