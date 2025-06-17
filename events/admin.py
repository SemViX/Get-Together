from django.contrib import admin
from .models import Category, Event

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name',)
    search_fields=('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_time', 'creator', 'participants_count')
    list_filter = ('category', 'start_time')
    search_fields = ('title', 'description', 'address')
    filter_horizontal = ('participants',)

    def participants_count(self, obj):
        return obj.participants.count()
    
    participants_count.short_description = 'Кількість учасників'
