from django.urls import path
from . import views


app_name = 'User'


urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('settings', views.settings, name='settings'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
]