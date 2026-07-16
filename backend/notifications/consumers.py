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


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ws://localhost:8001/ws/notifications/?token=ABC...
        token = _extract_token(self.scope['query_string'].decode())

        self.user = await self.get_user(token)
        
        if self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = f'notifications_{self.user.id}'

        # Join room group
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

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def notification_message(self, event):
        notification = event['notification']

        # Send notification to WebSocket
        await self.send(text_data=json.dumps(notification))
