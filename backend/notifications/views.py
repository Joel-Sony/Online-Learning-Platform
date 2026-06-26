from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer
from .utils import create_notification
from enrollments.models import Enrollment

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_as_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        announcement = serializer.save(mentor=self.request.user)
        
        # Create notifications for all enrolled students
        enrolled_students = Enrollment.objects.filter(course=announcement.course, status='ACTIVE')
        for enrollment in enrolled_students:
            create_notification(
                recipient=enrollment.student,
                type='ANNOUNCEMENT',
                message=announcement.content,
                course=announcement.course
            )
