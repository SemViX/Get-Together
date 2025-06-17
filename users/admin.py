from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_active', "is_staff")
    search_fields = ('username', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Додаткові поля', {'fields': ('avatar', 'bio')}),
    )
