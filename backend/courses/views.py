from django.db import transaction
from django.db.models import Avg, Count, Q, Sum
from rest_framework import viewsets, permissions, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt
from .serializers import (
    CourseSerializer, CourseListSerializer, ModuleSerializer, LessonSerializer,
    QuizSerializer, QuizStudentSerializer, QuizQuestionSerializer, QuizChoiceSerializer, QuizAttemptSerializer
)
from .permissions import IsMentorOrReadOnly, IsOwnerOrAdmin
from .filters import CourseFilter
from .search import CourseSearchBackend
from users.serializers import MentorSearchSerializer

User = get_user_model()

class CoursePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = CoursePagination
    filter_backends = [DjangoFilterBackend, CourseSearchBackend, filters.OrderingFilter]
    filterset_class = CourseFilter
    ordering_fields = ['price', 'created_at', 'enrollment_count', 'avg_rating']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'autocomplete']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsMentorOrReadOnly(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(mentor=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        course = self.get_object()
        # Keep `status` and `is_published` in lockstep — they are two views of
        # the same approval state and must never disagree (see also
        # courses.admin_views.AdminCourseApprovalViewSet).
        course.status = 'PUBLISHED'
        course.is_published = True
        course.save(update_fields=['status', 'is_published'])

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
        reason = request.data.get('reason', 'No reason provided.')

        # A rejected course must not stay published.
        course.status = 'REJECTED'
        course.is_published = False
        course.save(update_fields=['status', 'is_published'])

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
        """Returns up to 7 course title suggestions using full-text search."""
        q = request.query_params.get('q', '').strip()
        if not q or len(q) < 2:
            return Response([])

        base = Course.objects.filter(is_published=True)

        with transaction.atomic():
            try:
                from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
                search_query = SearchQuery(q, config='english')
                vector = SearchVector('title', weight='A') + SearchVector('tags', weight='B') + SearchVector('category', weight='C')
                ranked = base.annotate(rank=SearchRank(vector, search_query)).filter(rank__gte=0.01)
                if ranked.exists():
                    results = ranked.values('id', 'title', 'category').order_by('-rank')[:7]
                    return Response(list(results))
            except Exception:
                pass

        results = base.filter(Q(title__icontains=q) | Q(tags__icontains=q) | Q(category__icontains=q)).values('id', 'title', 'category')[:7]
        return Response(list(results))

    def get_queryset(self):
        queryset = Course.objects.select_related('mentor').annotate(
            avg_rating=Avg('reviews__rating'),
            enrollment_count=Count('enrollments', distinct=True),
            total_duration=Sum('modules__lessons__duration_minutes')
        )

        user = self.request.user
        mine = self.request.query_params.get('mine')

        if mine == 'true' and user.is_authenticated:
            return queryset.filter(mentor=user)

        if user.is_authenticated:
            if user.role == 'ADMIN':
                return queryset
            if user.role == 'MENTOR':
                return queryset.filter(Q(is_published=True) | Q(mentor=user)).distinct()

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

    def get_permissions(self):
        if self.action == 'submit_attempt':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

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
        if not isinstance(submitted_answers, dict):
            return Response({'error': 'Invalid answers format.'}, status=status.HTTP_400_BAD_REQUEST)
            
        questions = quiz.questions.all()
        total_questions = questions.count()
        if total_questions == 0:
            return Response({'error': 'This quiz has no questions.'}, status=status.HTTP_400_BAD_REQUEST)
            
        correct_count = 0
        question_results = []
        
        for q in questions:
            chosen_choice_id = submitted_answers.get(str(q.id)) or submitted_answers.get(q.id)
            is_correct = False
            correct_choice_text = ""
            chosen_choice_text = ""
            
            # Find correct choice
            try:
                correct_choice_obj = QuizChoice.objects.filter(question=q, is_correct=True).first()
                if correct_choice_obj:
                    correct_choice_text = correct_choice_obj.text
            except Exception:
                pass
                
            if chosen_choice_id:
                try:
                    choice = QuizChoice.objects.get(id=chosen_choice_id, question=q)
                    chosen_choice_text = choice.text
                    if choice.is_correct:
                        is_correct = True
                        correct_count += 1
                except QuizChoice.DoesNotExist:
                    pass
            
            question_results.append({
                'question_id': q.id,
                'question_text': q.text,
                'chosen_choice_id': chosen_choice_id,
                'chosen_choice_text': chosen_choice_text,
                'is_correct': is_correct,
                'correct_choice_text': correct_choice_text
            })
                    
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
            
            # Check for course completion
            try:
                from progress.models import LessonProgress, Certificate
                total_lessons = Lesson.objects.filter(module__course=quiz.module.course).count()
                completed_lessons = LessonProgress.objects.filter(student=student, course=quiz.module.course, completed=True).count()
                if total_lessons > 0 and total_lessons == completed_lessons:
                    if not Certificate.objects.filter(student=student, course=quiz.module.course).exists():
                        import uuid
                        Certificate.objects.create(
                            student=student,
                            course=quiz.module.course,
                            certificate_id=f"CERT-{uuid.uuid4().hex[:8].upper()}"
                        )
            except Exception:
                pass
            
        return Response({
            'attempt_id': attempt.id,
            'score': attempt.score,
            'passed': attempt.passed,
            'correct_answers': correct_count,
            'total_questions': total_questions,
            'question_results': question_results
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

