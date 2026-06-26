from django.db.models import Count, Sum, Avg
from rest_framework import viewsets, permissions, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Course
from .serializers import CourseListSerializer
from notifications.utils import create_notification
from enrollments.models import Payment, Enrollment

User = get_user_model()

class AdminCourseApprovalViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def pending(self, request):
        courses = Course.objects.filter(status='PENDING').order_by('-created_at')
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        course.status = 'PUBLISHED'
        course.is_published = True
        course.save()
        
        create_notification(
            recipient=course.mentor,
            type='ANNOUNCEMENT',
            message=f"Your course '{course.title}' has been approved and is now live!",
            course=course
        )
        return Response({'status': 'Course approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
        course.status = 'REJECTED'
        course.is_published = False
        course.save()
        
        reason = request.data.get('reason', 'No specific reason provided.')
        create_notification(
            recipient=course.mentor,
            type='ANNOUNCEMENT',
            message=f"Your course '{course.title}' was not approved. Reason: {reason}",
            course=course
        )
        return Response({'status': 'Course rejected'})

class AdminReportsView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_mentors = User.objects.filter(role='MENTOR').count()
        total_students = User.objects.filter(role='STUDENT').count()
        
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        total_revenue = Payment.objects.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0
        
        top_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5]
        
        top_mentors = User.objects.filter(role='MENTOR').annotate(
            avg_rating=Avg('mentored_courses__reviews__rating')
        ).order_by('-avg_rating')[:5]
        
        return Response({
            'stats': {
                'total_users': total_users,
                'total_mentors': total_mentors,
                'total_students': total_students,
                'total_courses': total_courses,
                'total_enrollments': total_enrollments,
                'total_revenue': total_revenue,
            },
            'top_courses': CourseListSerializer(top_courses, many=True).data,
            'top_mentors': [
                {
                    'id': m.id,
                    'username': m.username,
                    'avg_rating': m.avg_rating or 0
                } for m in top_mentors
            ]
        })
