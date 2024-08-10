from django.db import models


# Create your models here.
class User(models.Model):

    user_name = models.CharField(max_length=20)
    user_password = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255, unique=True)
    online_id = models.IntegerField(max_length=100, default=99)
    user_email = models.EmailField(max_length=255)
    profile = models.ImageField(upload_to='profile_pictures/', null=True, blank=True) #头像
    api = models.CharField(max_length=255)
    bio = models.TextField(max_length=500, blank=True,null=True) #Self-introduction
    last_login = models.DateTimeField(
        verbose_name='last login',
        auto_now=True
    )
    is_authenticated = models.BooleanField(default=False)

    def __str__(self):
        return self.user_name