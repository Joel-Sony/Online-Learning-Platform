from rest_framework import serializers
from django.db.models import Avg
from .models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice, QuizAttempt

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class QuizChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated or request.user.role == 'STUDENT':
            rep.pop('is_correct', None)
        return rep

class QuizQuestionSerializer(serializers.ModelSerializer):
    choices = QuizChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = QuizQuestion
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    course_id = serializers.ReadOnlyField(source='module.course.id')
    class Meta:
        model = Quiz
        fields = '__all__'

class QuizChoiceStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ('id', 'text')

class QuizQuestionStudentSerializer(serializers.ModelSerializer):
    choices = QuizChoiceStudentSerializer(many=True, read_only=True)
    class Meta:
        model = QuizQuestion
        fields = ('id', 'text', 'order', 'choices')

class QuizStudentSerializer(serializers.ModelSerializer):
    questions = QuizQuestionStudentSerializer(many=True, read_only=True)
    course_id = serializers.ReadOnlyField(source='module.course.id')
    class Meta:
        model = Quiz
        fields = ('id', 'module', 'title', 'description', 'passing_score', 'questions', 'course_id')

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = '__all__'
        read_only_fields = ('student', 'score', 'passed', 'completed_at')

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    quizzes = QuizSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    mentor_name = serializers.ReadOnlyField(source='mentor.username')
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('mentor', 'created_at', 'updated_at')

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        url = obj.thumbnail.url
        request = self.context.get('request')
        if request:
            absolute = request.build_absolute_uri(url)
            forwarded = request.META.get('HTTP_X_FORWARDED_PROTO', '')
            if forwarded:
                scheme = forwarded.split(',')[0].strip()
                absolute = f'{scheme}://{absolute.split("://")[-1]}'
            return absolute
        return url

class CourseListSerializer(serializers.ModelSerializer):
    mentor_name = serializers.ReadOnlyField(source='mentor.username')
    avg_rating = serializers.FloatField(read_only=True)
    enrollment_count = serializers.IntegerField(read_only=True)
    total_duration = serializers.IntegerField(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'thumbnail', 'category', 'level', 'price', 'mentor_name', 'is_published', 'status', 'avg_rating', 'enrollment_count', 'total_duration')

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        url = obj.thumbnail.url
        request = self.context.get('request')
        if request:
            absolute = request.build_absolute_uri(url)
            forwarded = request.META.get('HTTP_X_FORWARDED_PROTO', '')
            if forwarded:
                scheme = forwarded.split(',')[0].strip()
                absolute = f'{scheme}://{absolute.split("://")[-1]}'
            return absolute
        return url

