from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
import uuid
# from django.contrib.auth.models import User
from .models import User, LLMsetting
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
            messages.error(request, '用户不存在！')
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
        # 检查用户名是否已存在
        if User.objects.filter(user_name=user_name).exists():
            messages.error(request, "用户名已存在")
            return render(request, "register.html") # 假设注册页面的 URL 名称为 'register'

        # 检查电子邮件是否已存在
        if User.objects.filter(user_email=user_email).exists():
            messages.error(request, "邮箱已注册")
            return render(request, "register.html")  # 假设注册页面的 URL 名称为 'register'

        if user_password == user_password2:
            new_llm = LLMsetting()
            new_llm.save()
            new_user = User(
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                user_password=user_password,
                profile="images/成员1.jpeg",  # 上传的头像文件路径
                bio="添加你的介绍",
                api="添加模型API",
                llm_model=new_llm,
            )
            new_user.save()
        else:
            messages.error(request, '两次输入密码不一致')
            return render(request, "register.html")

        user = authenticate(request, user_id=user_id, user_email=user_email, user_name=user_name, user_password=user_password)
        print(user)

        return redirect('User:login')

    # 填写表单
    elif request.method == 'GET':
        return render(request, 'register.html')
    else:
        return HttpResponse("请使用GET或POST请求数据")


def profile(request):
    user = request.user
    if request.method == 'POST':
        print(request.POST)
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('email')
        user_bio = request.POST.get('bio')
        user_id = request.POST.get('user_id')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        print("change profile")
        print("user_name", user_name)
        print("user_email", user_email)
        print("user_bio", user_bio)

        if user.user_password != old_password:
            print('wrong!')
            messages.error(request, '请输入正确的原密码')
            render(request, 'profile.html', {"user": user})
        elif User.objects.filter(user_email=user_email).exists():
            messages.error(request, '邮箱已经被使用过了')
            render(request, 'profile.html', {"user": user})
        else:
            print('start change')
            if new_password:
                user.user_password = new_password
            if user_email:
                user.user_email = user_email
            if user_name:
                user.user_name = user_name
            if user_bio:
                user.bio = user_bio

            user.save()
            messages.info(request, '更新成功！')

        return render(request, 'profile.html', {"user": user})

    elif request.method == "GET":
        return render(request, 'profile.html', {"user": user})


def settings(request):
    user = request.user
    if request.method == 'POST':
        llm_category = request.POST.get('llm')
        api_key = request.POST.get('api')
        token = request.POST.get('token')
        temperature = request.POST.get('temperature')
        stage1 = request.POST.get('stage1')
        stage2 = request.POST.get('stage2')
        stage3 = request.POST.get('stage3')

        # print(type(llm_category))
        # print("llm_category", llm_category)
        # print("api_key", api_key)
        # print(type(token))
        # print(token)
        #
        # print(type(temperature))
        # print(temperature)
        # print(stage1)

        # 更新模型实例
        user_model = user.llm_model
        print(user_model.llm_category)
        user_model.llm_category = int(llm_category)
        if api_key:
            user_model.llm_api = api_key
        if token:
            user_model.llm_token = token
        if temperature:
            user_model.llm_temp = temperature
        user_model.stage1 = stage1
        user_model.stage2 = stage2
        user_model.stage3 = stage3
        user_model.save()
        user.save()

        messages.success(request, "设置已成功更新。")

        return render(request, 'settings.html', {"user": user})

    elif request.method == "GET":
        return render(request, 'settings.html', {"user": user})


