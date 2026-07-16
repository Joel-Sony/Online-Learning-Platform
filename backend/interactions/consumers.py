import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


def _extract_token(query_string):
    """Parse the `token` query param robustly (a naive split('token=') also
    matches params like `refresh_token=` and slices the wrong value)."""
    params = parse_qs(query_string)
    values = params.get('token')
    return values[0] if values else None


class QAConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'course_qa_{self.course_id}'

        token = _extract_token(self.scope['query_string'].decode())
        self.user = await self.get_user(token)
        if self.user.is_anonymous:
            await self.close()
            return

        # Authorize: the real-time feed must enforce the same access rule as the
        # REST Q&A endpoints (qna._can_read). Otherwise any authenticated user
        # could subscribe to any course's Q&A stream they aren't enrolled in.
        if not await self.can_read_course_qa(self.user, self.course_id):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def get_user(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except Exception:
            return AnonymousUser()

    @database_sync_to_async
    def can_read_course_qa(self, user, course_id):
        if getattr(user, 'role', None) in ('ADMIN', 'MENTOR'):
            return True
        from enrollments.models import Enrollment
        return Enrollment.objects.filter(
            student=user, course_id=course_id, status='ACTIVE'
        ).exists()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def qa_message(self, event):
        message = event['message']
        msg_type = event['msg_type']

        await self.send(text_data=json.dumps({
            'message': message,
            'msg_type': msg_type
        }))
