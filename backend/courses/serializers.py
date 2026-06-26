from rest_framework import serializers
from django.db.models import Avg
from .models import Course, Module, Lesson



class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    mentor_name = serializers.ReadOnlyField(source='mentor.username')

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('mentor', 'created_at', 'updated_at')

class CourseListSerializer(serializers.ModelSerializer):
    mentor_name = serializers.ReadOnlyField(source='mentor.username')
    avg_rating = serializers.FloatField(read_only=True)
    enrollment_count = serializers.IntegerField(read_only=True)
    total_duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'thumbnail', 'category', 'level', 'price', 'mentor_name', 'is_published', 'status', 'avg_rating', 'enrollment_count', 'total_duration')

