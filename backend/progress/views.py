import uuid
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LessonProgress, Certificate
from .serializers import LessonProgressSerializer, CertificateSerializer
from courses.models import Course, Lesson
from enrollments.models import Enrollment

class ProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return LessonProgress.objects.all()
        if user.role == 'MENTOR':
            return LessonProgress.objects.filter(course__mentor=user)
        return LessonProgress.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user, completed_at=timezone.now())

    @action(detail=False, methods=['post'])
    def mark_complete(self, request):
        lesson_id = request.data.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.module.course
        
        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'error': 'Not enrolled in this course'}, status=status.HTTP_403_FORBIDDEN)

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'course': course, 'completed': True, 'completed_at': timezone.now()}
        )
        
        if not created:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()

        # Check for course completion
        self._check_course_completion(request.user, course)
        
        return Response({'status': 'Lesson completed'})

    def _check_course_completion(self, user, course):
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(student=user, course=course, completed=True).count()
        
        if total_lessons > 0 and total_lessons == completed_lessons:
            # Create certificate if not exists
            if not Certificate.objects.filter(student=user, course=course).exists():
                Certificate.objects.create(
                    student=user,
                    course=course,
                    certificate_id=f"CERT-{uuid.uuid4().hex[:8].upper()}"
                )

    @action(detail=False, methods=['get'])
    def course_progress(self, request):
        course_id = request.query_params.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonProgress.objects.filter(student=request.user, course=course, completed=True).count()
        
        percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return Response({
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'remaining_lessons': total_lessons - completed_lessons,
            'progress_percentage': round(percentage, 2)
        })

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(student=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        certificate = self.get_object()
        # Simulated PDF download - returning text representation as requested to keep it simple
        content = f"CERTIFICATE OF COMPLETION\n\nThis is to certify that\n{certificate.student.username}\n\nhas successfully completed the course\n{certificate.course.title}\n\nIssued on: {certificate.issued_at.date()}\nCertificate ID: {certificate.certificate_id}"
        
        response = Response(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="certificate-{certificate.certificate_id}.txt"'
        return response

class MentorAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        if request.user.role != 'MENTOR' and not request.user.is_staff:
            return Response({'error': 'Unauthorized'}, status=403)
        
        # Simple aggregate stats
        courses = Course.objects.filter(mentor=request.user)
        stats = []
        for course in courses:
            completions = Certificate.objects.filter(course=course).count()
            total_students = Enrollment.objects.filter(course=course).count()
            stats.append({
                'course_id': course.id,
                'course_title': course.title,
                'total_enrolled': total_students,
                'completions': completions
            })
        
        return Response(stats)
