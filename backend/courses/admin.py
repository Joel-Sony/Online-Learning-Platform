from django.contrib import admin
from .models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizChoice)
admin.site.register(QuizAttempt)
