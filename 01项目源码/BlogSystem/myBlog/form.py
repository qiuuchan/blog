from django import forms


# 用户登录验证
class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=255)
    password = forms.CharField(label="密码", max_length=255, widget=forms.PasswordInput)


# 文件上传
class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)
    editormdImageFile = forms.FileField()


# 文章分类
class ClassifyForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)


# 文章
class ArticleForm(forms.Form):
    title = forms.CharField(max_length=255, required=True)
    tag = forms.CharField(max_length=255, required=True)
    classify_id = forms.CharField(max_length=255, required=True)
    content = forms.CharField(max_length=None)
    status = forms.IntegerField()
