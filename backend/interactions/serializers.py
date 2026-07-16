from rest_framework import serializers
from .models import Review, ReviewReport

# Q&A serializers live in the `qna` app. The legacy Question/Answer
# serializers that used to be here backed dead viewsets and were removed.

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
