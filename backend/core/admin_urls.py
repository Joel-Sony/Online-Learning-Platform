from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.admin_views import AdminUserViewSet, AdminMentorApprovalViewSet
from courses.admin_views import AdminCourseApprovalViewSet, AdminReportsView
from interactions.admin_views import AdminReviewModerationViewSet
from qna.admin_views import AdminQnAModerationViewSet
from enrollments.admin_views import AdminRefundViewSet

router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'mentors', AdminMentorApprovalViewSet, basename='admin-mentors')
router.register(r'courses', AdminCourseApprovalViewSet, basename='admin-courses')
router.register(r'reviews', AdminReviewModerationViewSet, basename='admin-reviews')
router.register(r'qna', AdminQnAModerationViewSet, basename='admin-qna')
router.register(r'refunds', AdminRefundViewSet, basename='admin-refunds')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/', AdminReportsView.as_view(), name='admin-reports'),
]
