from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, ReplyViewSet

# /api/courses/{course_id}/qna/questions/
# /api/courses/{course_id}/qna/questions/{question_id}/replies/

course_router = routers.SimpleRouter()
course_router.register(r'questions', QuestionViewSet, basename='qna-question')

question_router = routers.NestedSimpleRouter(course_router, r'questions', lookup='question')
question_router.register(r'replies', ReplyViewSet, basename='qna-reply')

urlpatterns = [
    path('', include(course_router.urls)),
    path('', include(question_router.urls)),
]
