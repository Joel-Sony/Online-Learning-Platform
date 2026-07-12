from django.contrib import admin
from .models import Review, ReviewReport, Question, Answer

admin.site.register(Review)
admin.site.register(ReviewReport)
admin.site.register(Question)
admin.site.register(Answer)
