from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Фото користувача")
    bio = models.TextField(blank=True, verbose_name="Біо користувача")

    def __str__(self):
        return self.username
    