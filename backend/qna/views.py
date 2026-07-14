from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from courses.models import Course
from enrollments.models import Enrollment
from notifications.utils import create_notification
from .models import Question, Reply
from .permissions import IsEnrolledOrMentorOrAdmin
from .serializers import QuestionSerializer, ReplySerializer
from .utils import broadcast_to_course


def _get_course_or_404(course_id):
    return get_object_or_404(Course, pk=course_id)


def _is_enrolled(user, course):
    return Enrollment.objects.filter(student=user, course=course, status='ACTIVE').exists()


def _check_can_write(user, course):
    """Students must be enrolled. Mentors and Admins always pass."""
    if user.role == 'ADMIN':
        return
    if user.role == 'MENTOR':
        return
    if not _is_enrolled(user, course):
        raise PermissionDenied("You must be enrolled in this course to participate in the Q&A.")


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Question.objects.filter(course_id=course_id)

    def perform_create(self, serializer):
        course = _get_course_or_404(self.kwargs['course_id'])
        _check_can_write(self.request.user, course)
        question = serializer.save(author=self.request.user, course=course)
        broadcast_to_course(course.id, 'new_question', QuestionSerializer(question).data)

    def perform_update(self, serializer):
        question = self.get_object()
        # Allow any enrolled user to flag
        if 'is_flagged' in serializer.validated_data:
            if not _is_enrolled(self.request.user, question.course) and self.request.user.role != 'ADMIN':
                raise PermissionDenied("You must be enrolled to flag questions.")
            serializer.save()
            return
        # Only the author or an admin can edit
        if self.request.user != question.author and self.request.user.role != 'ADMIN':
            raise PermissionDenied("You can only edit your own questions.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        # Author, course mentor, or admin can delete
        if user != instance.author and user != instance.course.mentor and user.role != 'ADMIN':
            raise PermissionDenied("You do not have permission to delete this question.")
        instance.delete()

    @action(detail=True, methods=['post'])
    def pin(self, request, course_id=None, pk=None):
        question = self.get_object()
        if question.course.mentor != request.user and request.user.role != 'ADMIN':
            raise PermissionDenied("Only the course mentor or admin can pin questions.")
        question.is_pinned = not question.is_pinned
        question.save(update_fields=['is_pinned'])
        return Response({'is_pinned': question.is_pinned})


class ReplyViewSet(viewsets.ModelViewSet):
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reply.objects.filter(question_id=self.kwargs['question_pk'])

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        question_id = self.kwargs['question_pk']
        course = _get_course_or_404(course_id)
        question = get_object_or_404(Question, pk=question_id, course=course)

        _check_can_write(self.request.user, course)

        # Validate parent belongs to the same question (one level only)
        parent = serializer.validated_data.get('parent')
        if parent:
            if parent.question_id != question.id:
                raise ValidationError("Parent reply does not belong to this question.")
            if parent.parent_id is not None:
                raise ValidationError("Only one level of threading is supported.")

        is_mentor = self.request.user == course.mentor
        reply = serializer.save(
            author=self.request.user,
            question=question,
            is_mentor_response=is_mentor,
        )

        broadcast_to_course(course.id, 'new_reply', ReplySerializer(reply).data)

        # Notify the question author if a mentor replied (and it's not to themselves)
        if is_mentor and self.request.user != question.author:
            create_notification(
                recipient=question.author,
                type='NEW_ANSWER',
                message=f"Mentor {self.request.user.username} replied to your question in {course.title}.",
                course=course,
            )

    def perform_update(self, serializer):
        reply = self.get_object()
        # Allow any enrolled user to flag
        if 'is_flagged' in serializer.validated_data:
            course = reply.question.course
            if not _is_enrolled(self.request.user, course) and self.request.user.role != 'ADMIN':
                raise PermissionDenied("You must be enrolled to flag replies.")
            serializer.save()
            return
        # Only the author or an admin can edit
        if self.request.user != reply.author and self.request.user.role != 'ADMIN':
            raise PermissionDenied("You can only edit your own replies.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        course = instance.question.course
        if user != instance.author and user != course.mentor and user.role != 'ADMIN':
            raise PermissionDenied("You do not have permission to delete this reply.")
        instance.delete()
