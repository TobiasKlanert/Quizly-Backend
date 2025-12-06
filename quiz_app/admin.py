from django.contrib import admin
from .models import Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ['title','video_url', 'user']
    list_filter = ['user']


admin.site.register(Quiz, QuizAdmin)