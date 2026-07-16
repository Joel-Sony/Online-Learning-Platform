from django.db import models
from django.conf import settings
from courses.models import Course

class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        REFUNDED = 'REFUNDED', 'Refunded'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Payment(models.Model):
    class Provider(models.TextChoices):
        STRIPE = 'STRIPE', 'Stripe'
        PAYPAL = 'PAYPAL', 'PayPal'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUND_REQUESTED = 'REFUND_REQUESTED', 'Refund Requested'
        REFUNDED = 'REFUNDED', 'Refunded'

    # PROTECT, not CASCADE: payment records are a financial audit trail and must
    # survive deletion of the related user or course (deleting a parent with
    # payments now raises ProtectedError instead of silently erasing history).
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='payments')
    provider = models.CharField(max_length=20, choices=Provider.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    provider_payment_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    # Stripe-specific: stores payment_intent ID for refund lookups (not used for PayPal)
    payment_intent_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title} (${self.amount})"
