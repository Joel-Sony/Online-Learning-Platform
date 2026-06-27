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

    def get_permissions(self):
        if self.action == 'download':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Certificate.objects.none()
        return Certificate.objects.filter(student=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        if not request.user or not request.user.is_authenticated:
            token = request.query_params.get('token')
            if token:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                from rest_framework_simplejwt.authentication import JWTAuthentication
                try:
                    validated_token = JWTAuthentication().get_validated_token(token)
                    request.user = JWTAuthentication().get_user(validated_token)
                except (InvalidToken, TokenError):
                    pass

        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        certificate = self.get_object()
        student_name = certificate.student.get_full_name() or certificate.student.username
        course_title = certificate.course.title
        issued_date = certificate.issued_at.strftime("%B %d, %Y")
        cert_id = certificate.certificate_id

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Certificate of Completion — {course_title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #f4f1eb; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: 'Inter', sans-serif; }}
    .cert {{ background: #fff; width: 860px; min-height: 600px; padding: 60px 80px; border: 2px solid #111; position: relative; box-shadow: 0 20px 60px rgba(0,0,0,0.12); }}
    .cert::before {{ content: ''; position: absolute; inset: 10px; border: 1px solid #c8b97a; pointer-events: none; }}
    .header {{ text-align: center; margin-bottom: 40px; }}
    .logo {{ font-family: 'Cormorant', serif; font-size: 1.1rem; letter-spacing: 0.25em; color: #555; text-transform: uppercase; margin-bottom: 6px; }}
    .divider {{ width: 60px; height: 2px; background: #c8b97a; margin: 0 auto 32px; }}
    .title {{ font-family: 'Cormorant', serif; font-size: 3.2rem; font-weight: 400; color: #111; line-height: 1; margin-bottom: 8px; }}
    .subtitle {{ font-size: 0.8rem; letter-spacing: 0.15em; color: #888; text-transform: uppercase; }}
    .body {{ text-align: center; margin: 40px 0; }}
    .certify-text {{ font-size: 0.9rem; color: #666; margin-bottom: 16px; letter-spacing: 0.05em; }}
    .student-name {{ font-family: 'Cormorant', serif; font-size: 3rem; font-weight: 600; color: #111; font-style: italic; margin: 8px 0 24px; }}
    .completion-text {{ font-size: 0.9rem; color: #666; margin-bottom: 12px; letter-spacing: 0.05em; }}
    .course-title {{ font-family: 'Cormorant', serif; font-size: 1.8rem; font-weight: 600; color: #111; margin-bottom: 8px; }}
    .footer {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 60px; border-top: 1px solid #eee; padding-top: 28px; }}
    .footer-item {{ text-align: center; }}
    .footer-label {{ font-size: 0.7rem; letter-spacing: 0.1em; color: #aaa; text-transform: uppercase; margin-top: 6px; }}
    .footer-value {{ font-size: 0.85rem; color: #333; font-weight: 500; }}
    .cert-id {{ font-size: 0.65rem; color: #bbb; margin-top: 4px; font-family: monospace; }}
    @media print {{
      body {{ background: white; }}
      .cert {{ box-shadow: none; border: 2px solid #111; }}
      .no-print {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="cert">
    <div class="header">
      <div class="logo">LearningPlatform</div>
      <div class="divider"></div>
      <div class="title">Certificate</div>
      <div class="subtitle">of Completion</div>
    </div>
    <div class="body">
      <div class="certify-text">This is to proudly certify that</div>
      <div class="student-name">{student_name}</div>
      <div class="completion-text">has successfully completed the course</div>
      <div class="course-title">{course_title}</div>
    </div>
    <div class="footer">
      <div class="footer-item">
        <div class="footer-value">{issued_date}</div>
        <div class="footer-label">Date Issued</div>
      </div>
      <div class="footer-item">
        <div class="footer-value">LearningPlatform</div>
        <div class="footer-label">Issuing Authority</div>
      </div>
      <div class="footer-item">
        <div class="footer-value">{cert_id}</div>
        <div class="footer-label">Certificate ID</div>
        <div class="cert-id">Verifiable credential</div>
      </div>
    </div>
  </div>
  <script>window.onload = function() {{ window.print(); }}</script>
</body>
</html>"""
        from django.http import HttpResponse
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'inline; filename="certificate-{cert_id}.html"'
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
