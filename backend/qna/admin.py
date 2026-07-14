from django.contrib import admin
from .models import Question, Reply

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'author', 'is_flagged', 'created_at']
    list_filter = ['is_flagged', 'course']
    search_fields = ['title', 'body']

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['body', 'question', 'author', 'is_mentor_response', 'is_flagged', 'created_at']
    list_filter = ['is_flagged', 'is_mentor_response']
    search_fields = ['body']
