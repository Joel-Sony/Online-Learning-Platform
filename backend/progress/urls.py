from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgressViewSet, CertificateViewSet, MentorAnalyticsViewSet

router = DefaultRouter()
router.register(r'progress', ProgressViewSet)
router.register(r'certificates', CertificateViewSet)
router.register(r'mentor-analytics', MentorAnalyticsViewSet, basename='mentor-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
