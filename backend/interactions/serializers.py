from rest_framework import serializers
from .models import Review, ReviewReport, Question, Answer

class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Review
        fields = ('id', 'student', 'student_name', 'course', 'rating', 'review_text', 'is_flagged', 'created_at', 'updated_at')
        read_only_fields = ('student', 'is_flagged')

class ReviewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReport
        fields = '__all__'
        read_only_fields = ('reported_by',)

class AnswerSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Answer
        fields = ('id', 'question', 'author', 'author_name', 'content', 'created_at')
        read_only_fields = ('author',)

class QuestionSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'course', 'author', 'author_name', 'title', 'content', 'created_at', 'answers')
        read_only_fields = ('author',)
