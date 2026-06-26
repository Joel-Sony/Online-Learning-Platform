from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_to_course(course_id: int, event_type: str, data: dict):
    """
    Send a real-time message to everyone connected to this course's QnA channel.
    Matches the group name format used by existing consumers.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'course_qa_{course_id}',
        {
            'type': 'qa_message',
            'msg_type': event_type,
            'message': data,
        }
    )
