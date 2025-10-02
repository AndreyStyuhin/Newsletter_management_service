from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = None  # убираем поле username
    email = models.EmailField(unique=True, verbose_name="Email")

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"   # логинимся по email
    REQUIRED_FIELDS = []       # обязательных полей кроме email нет

    def __str__(self):
        return self.email
