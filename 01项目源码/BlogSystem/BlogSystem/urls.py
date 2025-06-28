from django.urls import path, include
from myBlog.views import *
from django.conf import settings
from django.conf.urls.static import static

# 主路由
urlpatterns = [
                  path('captcha/', include('captcha.urls')),  # 获取生成验证码
                  path('login/', Login.as_view()),  # 登录
                  path('logout/', Loginout.as_view()),  # 退出
                  path('admin/', Admin.as_view()),  # 后台
                  path('welcome/', Welcome.as_view()),  # 首页
                  path('articleOpt/', ArticleOpt.as_view()),
                  path('articleList/', ArticleList.as_view()),
                  path('UploadImg/', Upload_img.as_view()),
                  path('ClassifyAdd/', ClassifyAdd.as_view()),
                  path('ClassifyList/', ClassifyList.as_view()),
                  path('', MyArticle.as_view()),
                  path('MyArticle/', MyArticle.as_view()),
                  path('UpdatePwd/', UpdatePwd.as_view()),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
