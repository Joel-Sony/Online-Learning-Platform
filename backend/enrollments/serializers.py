from rest_framework import serializers
from .models import Enrollment, Payment
from courses.serializers import CourseListSerializer

class EnrollmentSerializer(serializers.ModelSerializer):
    course_details = CourseListSerializer(source='course', read_only=True)
    student_name = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'student_name', 'course', 'course_details', 'enrolled_at', 'status')
        # 'status' is server-controlled (set on payment/refund). A student must not be
        # able to PATCH themselves to ACTIVE or tamper with enrollment lifecycle state.
        read_only_fields = ('student', 'enrolled_at', 'status')

class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Payment
        fields = ('id', 'user', 'user_name', 'course', 'course_title', 'provider', 'amount', 'currency', 'status', 'provider_payment_id', 'created_at')
        read_only_fields = ('user', 'created_at', 'provider_payment_id', 'status')
