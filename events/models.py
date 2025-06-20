from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва категорії")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = "Категорії"

class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок', unique=True)
    description = models.TextField(verbose_name="Опис")
    start_time = models.DateTimeField(verbose_name="Дата початку")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='created_events'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        verbose_name='Учасники',
        blank=True
    )
    address = models.CharField(max_length=255, verbose_name="Адреса")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE, 
        verbose_name="Категорія",
        related_name='participated_events'
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Подія'
        verbose_name_plural = 'Події'
