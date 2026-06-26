from django.db import models
from django.conf import settings
from courses.models import Course


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='qna_questions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qna_questions')
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class Reply(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qna_replies')
    body = models.TextField()
    # True when the reply author is the course mentor — set automatically in the view
    is_mentor_response = models.BooleanField(default=False)
    # One level of threading: a reply can be a child of another top-level reply
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author.username} on Q:{self.question_id}"
