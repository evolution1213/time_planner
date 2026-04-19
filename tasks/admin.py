from django.contrib import admin

from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'priority', 'deadline', 'progress_indicator')
    list_filter = ('status', 'priority', 'category', 'deadline')
    search_fields = ('title', 'description', 'category__name')
    ordering = ('deadline', 'priority', 'title')

    def progress_indicator(self, obj):
        if obj.duration.total_seconds() <= 0:
            return 'N/A'
        percent = min(100, int((obj.actual_duration.total_seconds() / obj.duration.total_seconds()) * 100))
        return f'{percent}%'

    progress_indicator.short_description = 'Прогрес'
