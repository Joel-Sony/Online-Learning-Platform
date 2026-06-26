from rest_framework import serializers
from .models import LessonProgress, Certificate
from courses.models import Course, Lesson

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ('id', 'student', 'course', 'lesson', 'completed', 'completed_at')
        read_only_fields = ('student', 'completed_at')

class CourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    progress_percentage = serializers.FloatField()

class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')
    student_name = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Certificate
        fields = ('id', 'student', 'student_name', 'course', 'course_title', 'issued_at', 'certificate_id')
