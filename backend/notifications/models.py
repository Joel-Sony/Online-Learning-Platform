from django.db import models
from django.conf import settings
from courses.models import Course

class Notification(models.Model):
    TYPES = (
        ('ENROLLMENT', 'Enrollment'),
        ('NEW_LESSON', 'New Lesson'),
        ('NEW_ANSWER', 'New Answer'),
        ('REFUND', 'Refund'),
        ('ANNOUNCEMENT', 'Announcement'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.type} - {self.message[:20]}"

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    send_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Announcement for {self.course.title}: {self.title}"
