from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
import uuid
# from django.contrib.auth.models import User
from .models import User
import hashlib
# 引入验证登录的装饰器
from django.contrib.auth.decorators import login_required
from captcha.models import CaptchaStore

# 自定义后端
class CustomBackend(ModelBackend):
    def authenticate(self, request, user_email=None, user_password=None, **kwargs):
        try:
            user = User.objects.get(user_email=user_email)
            if user_password == user.user_password:
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# 合并登录 / 退出按钮
def user_login(request):
    user = request.user
    # 退出登录
    if user.is_authenticated:
        logout(request)
        return redirect('HOME:index')

    print("user_login")

    print(user.is_authenticated)
    if request.method == 'POST':
        print("收到 POST")
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')
        user_db = authenticate(request, user_email=user_email, user_password=user_password)
        print(user_db)
        print(user_db.user_password)
        if user_db is not None:
            user_db.is_authenticated = True
            user_db.save()
            login(request, user_db)
            online_id = user.id
            user_db.online_id = online_id
            return redirect('User:profile')  # 重定向到登录后的页面
        else:
            print("not found user!")
            return redirect('User:login')

    elif request.method == 'GET':
        return render(request, 'login.html')
    return HttpResponse("请使用GET或POST请求数据")


def user_register(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('email')
        unique_str = f"{user_name}-{uuid.uuid4()}"
        user_id = hashlib.sha256(unique_str.encode('utf-8')).hexdigest()
        user_password = request.POST.get('password')
        user_password2 = request.POST.get('password2')

        print("user_name", user_name)
        print("user_email", user_email)
        print("user_id", user_id)
        print("user_name", user_name)

        if user_password == user_password2:
            new_user = User(
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                user_password=user_password,
                profile="images/成员1.jpeg",  # 上传的头像文件路径
                bio="添加你的介绍",
                api="添加模型API"
            )
            new_user.save()
        else:
            return render(request, "register.html", {"check": 1})

        user = authenticate(request, user_id=user_id, user_email=user_email, user_name=user_name, user_password=user_password)
        print(user)

        return redirect('User:login')

    # 填写表单
    elif request.method == 'GET':
        return render(request, 'register.html', {"check": 0})
    else:
        return HttpResponse("请使用GET或POST请求数据")


def profile(request):
    user = request.user
    if request.method == 'POST':
        return render(request, 'profile.html', {"user": user})

    elif request.method == "GET":
        return render(request, 'profile.html', {"user": user})


def settings(request):
    user = request.user
    if request.method == 'POST':
        return render(request, 'settings.html', {"user": user})

    elif request.method == "GET":
        return render(request, 'settings.html', {"user": user})


