from django.db.models import Avg, Count, Q, Sum
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt
from .serializers import (
    CourseSerializer, CourseListSerializer, ModuleSerializer, LessonSerializer,
    QuizSerializer, QuizStudentSerializer, QuizQuestionSerializer, QuizChoiceSerializer, QuizAttemptSerializer
)
from .permissions import IsMentorOrReadOnly, IsOwnerOrAdmin
from .filters import CourseFilter
from users.serializers import MentorSearchSerializer

User = get_user_model()

class CourseViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description', 'mentor__username']
    ordering_fields = ['price', 'created_at', 'enrollment_count', 'avg_rating']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsMentorOrReadOnly(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(mentor=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        course = self.get_object()
        course.is_published = True # Assuming approval means publishing for now
        course.save()
        
        from notifications.utils import create_notification
        create_notification(
            recipient=course.mentor,
            type='ANNOUNCEMENT',
            message=f"Your course '{course.title}' has been approved and published.",
            course=course
        )
        return Response({'status': 'Course approved'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        course = self.get_object()
        # You might want a reason field in the request
        reason = request.data.get('reason', 'No reason provided.')
        
        from notifications.utils import create_notification
        create_notification(
            recipient=course.mentor,
            type='ANNOUNCEMENT',
            message=f"Your course '{course.title}' was not approved. Reason: {reason}",
            course=course
        )
        return Response({'status': 'Course rejected'})


    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def autocomplete(self, request):
        """Returns up to 7 course title suggestions for a search query."""
        q = request.query_params.get('q', '').strip()
        if not q or len(q) < 2:
            return Response([])
        results = (
            Course.objects
            .filter(is_published=True)
            .filter(Q(title__icontains=q) | Q(tags__icontains=q) | Q(category__icontains=q))
            .values('id', 'title', 'category')[:7]
        )
        return Response(list(results))

    def get_queryset(self):
        queryset = Course.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            enrollment_count=Count('enrollments', distinct=True),
            total_duration=Sum('modules__lessons__duration_minutes')
        )
        
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'ADMIN':
                return queryset
            if user.role == 'MENTOR':
                # Show published courses + mentor's own courses
                return queryset.filter(Q(is_published=True) | Q(mentor=user)).distinct()
        
        # Unauthenticated users or Students see only published courses
        return queryset.filter(is_published=True)

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(course_id=course_id)
        return Module.objects.all()

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        lesson = serializer.save()
        course = lesson.module.course
        
        # Phase 7: Notify enrolled students
        from enrollments.models import Enrollment
        from notifications.utils import create_notification
        
        enrolled_students = Enrollment.objects.filter(course=course, status='ACTIVE')
        for enrollment in enrolled_students:
            create_notification(
                recipient=enrollment.student,
                type='NEW_LESSON',
                message=f"A new lesson '{lesson.title}' has been added to {course.title}.",
                course=course
            )

    def get_queryset(self):

        module_id = self.request.query_params.get('module_id')
        if module_id:
            return Lesson.objects.filter(module_id=module_id)
        return Lesson.objects.all()

class MentorSearchView(generics.ListAPIView):
    serializer_class = MentorSearchSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'bio']

    def get_queryset(self):
        return User.objects.filter(role='MENTOR').annotate(
            course_count=Count('mentored_courses', distinct=True),
            avg_rating=Avg('mentored_courses__reviews__rating')
        )


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        if user.role == 'STUDENT':
            return QuizStudentSerializer
        return QuizSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Quiz.objects.all()
        
        if user.role == 'STUDENT':
            from enrollments.models import Enrollment
            enrolled_courses = Enrollment.objects.filter(student=user, status='ACTIVE').values_list('course_id', flat=True)
            return queryset.filter(module__course_id__in=enrolled_courses)
        elif user.role == 'MENTOR':
            return queryset.filter(module__course__mentor=user)
        return queryset

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_attempt(self, request, pk=None):
        quiz = self.get_object()
        student = request.user
        
        from enrollments.models import Enrollment
        if not Enrollment.objects.filter(student=student, course=quiz.module.course, status='ACTIVE').exists():
            return Response({'error': 'You are not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN)
            
        submitted_answers = request.data.get('answers', {})
        if not submitted_answers:
            return Response({'error': 'No answers submitted.'}, status=status.HTTP_400_BAD_REQUEST)
            
        questions = quiz.questions.all()
        total_questions = questions.count()
        if total_questions == 0:
            return Response({'error': 'This quiz has no questions.'}, status=status.HTTP_400_BAD_REQUEST)
            
        correct_count = 0
        for q in questions:
            chosen_choice_id = submitted_answers.get(str(q.id)) or submitted_answers.get(q.id)
            if chosen_choice_id:
                try:
                    choice = QuizChoice.objects.get(id=chosen_choice_id, question=q)
                    if choice.is_correct:
                        correct_count += 1
                except QuizChoice.DoesNotExist:
                    pass
                    
        score_percentage = (correct_count / total_questions) * 100
        passed = score_percentage >= quiz.passing_score
        
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            score=round(score_percentage, 2),
            passed=passed
        )
        
        if passed:
            from notifications.utils import create_notification
            create_notification(
                recipient=student,
                type='ANNOUNCEMENT',
                message=f"Congratulations! You passed the quiz '{quiz.title}' with {attempt.score}%.",
                course=quiz.module.course
            )
            
        return Response({
            'attempt_id': attempt.id,
            'score': attempt.score,
            'passed': attempt.passed,
            'correct_answers': correct_count,
            'total_questions': total_questions
        }, status=status.HTTP_201_CREATED)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            return QuizQuestion.objects.filter(quiz_id=quiz_id)
        return QuizQuestion.objects.all()


class QuizChoiceViewSet(viewsets.ModelViewSet):
    queryset = QuizChoice.objects.all()
    serializer_class = QuizChoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        question_id = self.request.query_params.get('question_id')
        if question_id:
            return QuizChoice.objects.filter(question_id=question_id)
        return QuizChoice.objects.all()


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return QuizAttempt.objects.all()
        elif user.role == 'MENTOR':
            return QuizAttempt.objects.filter(quiz__module__course__mentor=user)
        return QuizAttempt.objects.filter(student=user)

