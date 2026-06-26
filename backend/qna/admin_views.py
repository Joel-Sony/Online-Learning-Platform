from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Question, Reply
from .serializers import QuestionSerializer, ReplySerializer

class AdminQnAModerationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def flagged(self, request):
        questions = Question.objects.filter(is_flagged=True)
        replies = Reply.objects.filter(is_flagged=True)
        
        return Response({
            'questions': QuestionSerializer(questions, many=True).data,
            'replies': ReplySerializer(replies, many=True).data
        })

    @action(detail=True, methods=['delete'])
    def delete_question(self, request, pk=None):
        question = get_object_or_404(Question, pk=pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'])
    def delete_reply(self, request, pk=None):
        reply = get_object_or_404(Reply, pk=pk)
        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
