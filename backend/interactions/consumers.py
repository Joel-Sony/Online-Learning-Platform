import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QAConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'course_qa_{self.course_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def qa_message(self, event):
        message = event['message']
        msg_type = event['msg_type']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'msg_type': msg_type
        }))
