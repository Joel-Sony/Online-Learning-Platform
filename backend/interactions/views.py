from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Review, ReviewReport, Question, Answer
from .serializers import ReviewSerializer, ReviewReportSerializer, QuestionSerializer, AnswerSerializer
from enrollments.models import Enrollment

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_flagged=False)
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Review.objects.filter(is_flagged=False)
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not Enrollment.objects.filter(student=self.request.user, course=course).exists():
            raise ValidationError("Only enrolled students can review this course.")
        if Review.objects.filter(student=self.request.user, course=course).exists():
            raise ValidationError("You have already reviewed this course.")
        serializer.save(student=self.request.user)

    @action(detail=False, methods=['get'])
    def course_ratings(self, request):
        course_id = request.query_params.get('course_id')
        stats = Review.objects.filter(course_id=course_id, is_flagged=False).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        return Response(stats)

class ReviewReportViewSet(viewsets.ModelViewSet):
    queryset = ReviewReport.objects.all()
    serializer_class = ReviewReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        report = serializer.save(reported_by=self.request.user)
        report.review.is_flagged = True
        report.review.save(update_fields=['is_flagged'])

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        question = serializer.save(author=self.request.user)
        self._broadcast(question.course.id, 'new_question', QuestionSerializer(question).data)

    def _broadcast(self, course_id, msg_type, data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'course_qa_{course_id}',
            {
                'type': 'qa_message',
                'msg_type': msg_type,
                'message': data
            }
        )

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        answer = serializer.save(author=self.request.user)
        self._broadcast(answer.question.course.id, 'new_answer', AnswerSerializer(answer).data)
        
        # Phase 7: Notify question author
        if answer.author != answer.question.author:
            from notifications.utils import create_notification
            create_notification(
                recipient=answer.question.author,
                type='NEW_ANSWER',
                message=f"{answer.author.username} answered your question in {answer.question.course.title}.",
                course=answer.question.course
            )
        


    def _broadcast(self, course_id, msg_type, data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'course_qa_{course_id}',
            {
                'type': 'qa_message',
                'msg_type': msg_type,
                'message': data
            }
        )
