from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ModuleViewSet, LessonViewSet, MentorSearchView

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('mentors/search/', MentorSearchView.as_view(), name='mentor-search'),
    path('', include(router.urls)),
]
