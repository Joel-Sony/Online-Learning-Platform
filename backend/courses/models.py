from django.db import models
from django.conf import settings

class Course(models.Model):
    LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PUBLISHED', 'Published'),
        ('REJECTED', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='BEGINNER')
    language = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentored_courses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_published = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    TYPE_CHOICES = [
        ('VIDEO', 'Video'),
        ('PDF', 'PDF'),
        ('DOCUMENT', 'Document'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    video_url = models.URLField(max_length=500, null=True, blank=True)
    content = models.TextField(blank=True, default='', help_text="Textual lesson content / notes")
    file = models.FileField(upload_to='courses/lessons/', null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=60, help_text="Percentage score required to pass")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz: {self.title} ({self.module.course.title})"


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q: {self.text[:50]} (Quiz: {self.quiz.title})"


class QuizChoice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_correct:
            # Set all other choices for this question to False
            if self.pk:
                QuizChoice.objects.filter(question=self.question).exclude(pk=self.pk).update(is_correct=False)
            else:
                # If not saved yet, we can't exclude pk, but we can do it after super().save() or just clear all
                QuizChoice.objects.filter(question=self.question).update(is_correct=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Choice: {self.text[:30]} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField(help_text="Percentage score obtained by the student")
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}% - {'PASSED' if self.passed else 'FAILED'})"

