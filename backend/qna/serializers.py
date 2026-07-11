from rest_framework import serializers
from .models import Question, Reply


class ReplySerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    children = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            'id', 'question', 'author', 'author_name',
            'body', 'is_mentor_response', 'is_flagged', 'parent', 'children', 'created_at'
        )
        read_only_fields = ('author', 'question', 'is_mentor_response', 'is_flagged')

    def get_children(self, obj):
        # Only top-level replies have children; don't recurse deeper
        if obj.parent is None:
            return ReplySerializer(obj.children.all(), many=True).data
        return []


class QuestionSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = Question
        fields = (
            'id', 'course', 'author', 'author_name',
            'title', 'body', 'is_pinned', 'is_flagged', 'reply_count', 'replies', 'created_at'
        )
        read_only_fields = ('author', 'is_pinned', 'is_flagged', 'course')

    def get_replies(self, obj):
        # Only return top-level replies; children are nested inside each reply
        top_level = obj.replies.filter(parent=None)
        return ReplySerializer(top_level, many=True).data
