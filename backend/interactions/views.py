from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from .models import Review, ReviewReport
from .serializers import ReviewSerializer, ReviewReportSerializer
from enrollments.models import Enrollment

# NOTE: The real-time Q&A feature lives entirely in the `qna` app
# (nested under /api/courses/<id>/qna/). The legacy Question/Answer
# viewsets that used to live here were dead code — unreferenced by the
# frontend and duplicating qna — and broadcast an incompatible payload to
# the shared `course_qa_<id>` channel group. They have been removed. The
# underlying models remain (unused) to avoid a destructive migration.


def _is_admin(user):
    return bool(user and (user.is_staff or getattr(user, 'role', None) == 'ADMIN'))


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_flagged=False)
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.filter(is_flagged=False).select_related('student', 'course')
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not Enrollment.objects.filter(student=self.request.user, course=course).exists():
            raise ValidationError("Only enrolled students can review this course.")
        if Review.objects.filter(student=self.request.user, course=course).exists():
            raise ValidationError("You have already reviewed this course.")
        serializer.save(student=self.request.user)

    def perform_update(self, serializer):
        # Only the review's author (or an admin) may edit it.
        if serializer.instance.student != self.request.user and not _is_admin(self.request.user):
            raise PermissionDenied("You can only edit your own review.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only the review's author (or an admin) may delete it.
        if instance.student != self.request.user and not _is_admin(self.request.user):
            raise PermissionDenied("You can only delete your own review.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def course_ratings(self, request):
        course_id = request.query_params.get('course_id')
        stats = Review.objects.filter(course_id=course_id, is_flagged=False).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        return Response(stats)

class ReviewReportViewSet(viewsets.ModelViewSet):
    queryset = ReviewReport.objects.all()
    serializer_class = ReviewReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Anyone authenticated may file a report; only admins may browse or
        # delete the report queue (it is moderation data).
        if self.action in ('create',):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        report = serializer.save(reported_by=self.request.user)
        report.review.is_flagged = True
        report.review.save(update_fields=['is_flagged'])
