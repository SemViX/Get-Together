from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Фото користувача")
    bio = models.TextField(blank=True, verbose_name="Біо користувача")
    telegram_id = models.BigIntegerField(blank=True, null=True, unique=True)
    is_creator = models.BooleanField(default=False, verbose_name="Автор подій")

    def __str__(self):
        return self.username
    