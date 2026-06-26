from rest_framework import serializers
from .models import Notification, Announcement

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source='course.title')
    
    class Meta:
        model = Announcement
        fields = ('id', 'course', 'course_name', 'mentor', 'title', 'content', 'send_email', 'created_at')
        read_only_fields = ('mentor', 'created_at')
