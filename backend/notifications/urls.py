from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
