import datetime
import json
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.core import serializers
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from myBlog.form import *
from myBlog.models import *
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin


# 用户登录
class Login(View):
    # get请求
    def get(self, request):
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        login_form = UserForm()
        return render(request, 'login.html', locals())

    # post请求
    def post(self, request):
        yzm = request.POST.get('captcha', '')
        hashkey = request.POST.get('code')
        # 根据key获取验证码对象
        cap = CaptchaStore.objects.filter(hashkey=hashkey).first()
        if cap:  # 存在
            if cap.response == yzm.lower():
                login_form = UserForm(request.POST)
                if login_form.is_valid():
                    username = login_form.cleaned_data.get('username')
                    password = login_form.cleaned_data.get('password')
                    try:
                        user = User_admin.objects.get(username=username)
                    except:
                        message = '用户不存在！'
                        return redirect('/login/')

                    # 使用django自带的密码验证
                    if check_password(password, user.password):
                        login(request, user)
                        return redirect('/admin/')
                    else:
                        message = '密码不正确！'
                        return redirect('/login/')
            else:
                return redirect('/login/')

        else:
            message = '验证码无效！'
            return redirect('/login/')


# 用户退出
class Loginout(View):
    def get(self, request):
        logout(request)
        return redirect('/login/')


# 后台
class Admin(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        username = request.user
        users = User_admin.objects.filter(username=username).values('nickName', 'username').first()
        return render(request, 'index.html', {"users": users})


# 首页
class Welcome(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        print("ok")
        return render(request, 'welcome.html')


# 文章添加
class ArticleOpt(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        id = request.GET.get('id', '')
        if id == '':
            return render(request, 'article-add.html')
        else:
            ArticleData = Article.objects.filter(id=id).first()
            return render(request, 'article-add.html', {'ArticleData': ArticleData})

    def post(self, request):
        id = request.POST.get('id', '')
        title = request.POST.get('title')
        tag = request.POST.get('tag')
        classify_id = request.POST.get('classify_id')
        content = request.POST.get('content')
        status = request.POST.get('status')
        isdelete = request.POST.get('isdelete', False)
        if id == "":
            instance = Article.objects.create(id=uuid.uuid4(), title=title, tag=tag, classify_id=classify_id,
                                              content=content, status=int(status))
            instance.save()
            Result = {
                "code": 2000,
                "msg": "添加成功",
                "count": 0,
                "data": ""
            }

        else:
            if isdelete:
                Article.objects.filter(id=id).delete()
                Result = {
                    "code": 2000,
                    "msg": "删除成功",
                    "count": 0,
                    "data": ""
                }
            else:
                Article.objects.filter(id=id).update(title=title, tag=tag, classify_id=classify_id, content=content,
                                                     status=int(status))
                Result = {
                    "code": 2000,
                    "msg": "修改成功",
                    "count": 0,
                    "data": ""
                }
        return JsonResponse(Result)


# 文章列表
class ArticleList(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        return render(request, 'article-list.html')

    def post(self, request):
        reqData = request.POST
        pageIndex = reqData.get('pageIndex', 1)
        pageSize = reqData.get('pageSize', 10)
        lists = Article.objects.all()
        title = reqData.get('title', None)
        status = reqData.get('status', None)
        updateTime = reqData.get('updateTime', None)
        if title != "":
            lists = Article.objects.filter(title__icontains=title)
        if status != "":
            lists = Article.objects.filter(status=int(status))
        if updateTime != "":
            updateTime = updateTime.split(',')
            start = datetime.datetime.strptime(updateTime[0][:19], '%Y-%m-%d %H:%M:%S')
            end = datetime.datetime.strptime(updateTime[1][1:20], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                days=1).strftime("%Y-%m-%d %H:%M:%S")
            lists = Article.objects.filter(updateTime__gte=start, updateTime__lte=end)
        pageInator = Paginator(lists, pageSize)
        contacts = pageInator.page(pageIndex)
        json_data = serializers.serialize("json", contacts,
                                          fields=('title', 'tag', 'status', 'createTime', 'updateTime',))
        Result = {
            "code": 2000,
            "msg": "成功",
            "count": len(lists),
            "data": json.loads(json_data)
        }
        return JsonResponse(Result)


# 图片上传
class Upload_img(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        data = {
            "success": 0,  # 0 表示上传失败，1 表示上传成功
            "message": "上传失败。",
            "url": ""  # 上传成功时才返回
        }
        return JsonResponse(data)

    def post(self, request):
        imgs = request.FILES.get('editormd-image-file')
        name = str(imgs).split('.')[0]
        data = {
            "name": name,
            "editormdImageFile": imgs
        }
        form = UploadFileForm(request.POST, data)
        if form.is_valid():
            instance = Imgs(name=name, url=request.FILES['editormd-image-file'])  # 保存文件到FileField域
            instance.save()

            if instance.url is not None:
                data = {
                    "success": 1,  # 0 表示上传失败，1 表示上传成功
                    "message": "上传成功",
                    "url": "/media/" + str(instance.url)  # 上传成功时才返回
                }
            else:
                data = {
                    "success": 0,  # 0 表示上传失败，1 表示上传成功
                    "message": "上传失败",
                    "url": ""  # 上传成功时才返回
                }
        else:
            data = {
                "success": 0,  # 0 表示上传失败，1 表示上传成功
                "message": "上传失败。",
                "url": ""  # 上传成功时才返回
            }
        return JsonResponse(data)


# 分类添加
class ClassifyAdd(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        id = request.GET.get('id', '')
        if id == '':
            return render(request, 'classify-add.html')
        else:
            ClassifyData = Classify.objects.filter(id=id).first()
            return render(request, 'classify-add.html', {'Data': ClassifyData})

    def post(self, request):
        id = request.POST.get('id', '')
        name = request.POST.get('name')
        isdelete = request.POST.get('isdelete', False)
        if id == "":
            instance = Classify.objects.create(id=uuid.uuid4(), name=name)
            instance.save()
            Result = {
                "code": 2000,
                "msg": "添加成功",
                "count": 0,
                "data": ""
            }

        else:
            if isdelete:
                Classify.objects.filter(id=id).delete()
                Result = {
                    "code": 2000,
                    "msg": "删除成功",
                    "count": 0,
                    "data": ""
                }
            else:
                Classify.objects.filter(id=id).update(name=name)
                Result = {
                    "code": 2000,
                    "msg": "修改成功",
                    "count": 0,
                    "data": ""
                }
        return JsonResponse(Result)


# 分类获取
class ClassifyList(View):
    def get(self, request):
        return render(request, 'classify.html')

    def post(self, request):

        reqData = request.POST
        pageIndex = reqData.get('pageIndex', 1)
        pageSize = reqData.get('pageSize', 10)
        name = reqData.get('name', '')
        if name != "":
            lists = Classify.objects.filter(name__icontains=name)
        else:
            lists = Classify.objects.all()
        pageInator = Paginator(lists, pageSize)
        contacts = pageInator.page(pageIndex)
        json_data = serializers.serialize("json", contacts)
        Result = {
            "code": 2000,
            "msg": "成功",
            "count": len(lists),
            "data": json.loads(json_data)
        }
        return JsonResponse(Result)


# 前端文章获取
class MyArticle(View):
    def get(self, request):
        id = request.GET.get('id', None)
        classify_id = request.GET.get('classify_id', None)
        if id is None:
            if classify_id is None:
                ArticleList = Article.objects.filter(status=1).all()
            else:
                ArticleList = Article.objects.filter(status=1, classify_id=classify_id).all()
            pageIndex = request.GET.get('pageIndex', 1)
            pageSize = request.GET.get('pageSize', 5)
            pageInator = Paginator(ArticleList, pageSize)
            contacts = pageInator.page(pageIndex)
            # imgs = []
            # for c in contacts.object_list:
            #     imgs.append(re.findall(r'[(](.*)[)]', c.content)[0])
            # print(imgs)
            return render(request, 'frontEnd/index.html',
                          {'ArticleList': contacts, 'CountList': ArticleList.count()})
        else:
            ArticleList = Article.objects.filter(id=id).first()
            return render(request, 'frontEnd/travel.html', {'ArticleList': ArticleList})


# 修改密码
class UpdatePwd(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        username = request.user
        return render(request, 'change-password.html', {"username": username})

    def post(self, request):
        reqData = request.POST
        oldpwd = reqData.get('oldpassword')
        newpwd = reqData.get('newpassword')
        user = User_admin.objects.filter(username=request.user).first()
        Result = dict()
        if check_password(oldpwd, user.password):
            User_admin.objects.filter(username=request.user).update(password=make_password(newpwd))
            Result = {
                "code": 2000,
                "msg": "成功",
                "count": 0,
                "data": ""
            }
        else:
            Result = {
                "code": 2001,
                "msg": "旧密码不正确",
                "count": 0,
                "data": ""
            }
        return JsonResponse(Result)
