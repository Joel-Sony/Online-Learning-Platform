from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer

def create_notification(recipient, type, message, course=None):
    # Save to DB
    notification = Notification.objects.create(
        recipient=recipient,
        type=type,
        message=message,
        course=course
    )

    # Broadcast via WebSocket
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notifications_{recipient.id}',
            {
                'type': 'notification_message',
                'notification': NotificationSerializer(notification).data
            }
        )
    
    # Send Email
    try:
        subject = f"Antigravity: {type.replace('_', ' ').title()}"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient.email],
            fail_silently=False,
        )
        print(f"Email sent successfully to {recipient.email}")
    except Exception as e:
        print(f"CRITICAL: Error sending email to {recipient.email}: {str(e)}")
    
    return notification
