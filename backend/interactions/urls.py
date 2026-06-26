from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewReportViewSet, QuestionViewSet, AnswerViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)
router.register(r'reports', ReviewReportViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'answers', AnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
