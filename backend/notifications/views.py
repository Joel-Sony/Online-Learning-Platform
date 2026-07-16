from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer
from .utils import create_notification
from enrollments.models import Enrollment


def _is_admin(user):
    return bool(user and (user.is_staff or getattr(user, 'role', None) == 'ADMIN'))

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def perform_create(self, serializer):
        # Only the mentor who owns the target course (or an admin) may post an
        # announcement — otherwise any authenticated user, including a student,
        # could fan out a notification to every enrolled student of any course.
        course = serializer.validated_data.get('course')
        user = self.request.user
        if not _is_admin(user) and not (course and course.mentor_id == user.id):
            raise PermissionDenied("Only the course's mentor can post announcements for it.")

        announcement = serializer.save(mentor=user)

        # Notify all actively-enrolled students of the course.
        enrolled_students = Enrollment.objects.filter(course=announcement.course, status='ACTIVE')
        for enrollment in enrolled_students:
            create_notification(
                recipient=enrollment.student,
                type='ANNOUNCEMENT',
                message=announcement.content,
                course=announcement.course
            )

    def _require_owner_or_admin(self, announcement):
        user = self.request.user
        if not _is_admin(user) and announcement.mentor_id != user.id:
            raise PermissionDenied("You can only modify your own announcements.")

    def perform_update(self, serializer):
        self._require_owner_or_admin(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._require_owner_or_admin(instance)
        instance.delete()
