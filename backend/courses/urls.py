from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, ModuleViewSet, LessonViewSet, MentorSearchView,
    QuizViewSet, QuizQuestionViewSet, QuizChoiceViewSet, QuizAttemptViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'quiz-questions', QuizQuestionViewSet)
router.register(r'quiz-choices', QuizChoiceViewSet)
router.register(r'quiz-attempts', QuizAttemptViewSet)


urlpatterns = [
    path('mentors/search/', MentorSearchView.as_view(), name='mentor-search'),
    path('', include(router.urls)),
]
