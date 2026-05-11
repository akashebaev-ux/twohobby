import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage, ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        has_access = await self.user_has_access(user, self.room_id)

        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = self.scope["user"].username

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
        }))

    @sync_to_async
    def user_has_access(self, user, room_id):
        return ChatRoom.objects.filter(
            id=room_id,
            users=user
        ).exists()

    @sync_to_async
    def save_message(self, message):
        room = ChatRoom.objects.get(id=self.room_id)

        ChatMessage.objects.create(
            room=room,
            sender=self.scope["user"],
            message=message
        )