"""WebSocket consumer handling chat, images, and WebRTC calls."""


import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage, ChatRoom, CallLog


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time chat and call functionality."""

    async def connect(self):
        """Connect a user to the chat room WebSocket."""

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
        """Disconnect a user from the chat room."""

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive and process WebSocket messages."""

        data = json.loads(text_data)

        if data.get("type") == "call_invite":
            can_call = await self.can_make_call()

            if not can_call:
                await self.send(text_data=json.dumps({
                    "type": "call_limit",
                    "message": "You already used your 10 calls for today."
                }))
                return

            await self.save_call_log()
            receiver = await self.get_receiver()

            if receiver:
                await self.channel_layer.group_send(
                    f"user_{receiver.id}",
                    {
                        "type": "incoming_call",
                        "username": self.scope["user"].username,
                        "room_id": self.room_id,
                    }
                )

                return

        if data.get("type") == "call_accept":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "call_accept",
                }
            )

            return

        if data.get("type") in [
            "webrtc_offer",
            "webrtc_answer",
            "ice_candidate",
        ]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": data,
                    "username": self.scope["user"].username,
                }
            )
            return
        message = data.get("message", "")
        username = self.scope["user"].username
        is_voice = data.get("is_voice", False)

        if not is_voice:
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
        """Send chat messages to the WebSocket."""

        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "username": event["username"],
        }))

    async def call_invite(self, event):
        """Send call invitation events to connected users."""

        await self.send(text_data=json.dumps({
            "type": "call_invite",
            "username": event["username"],
        }))

    async def call_accept(self, event):
        await self.send(text_data=json.dumps({
            "type": "call_accept",
        }))

    async def webrtc_signal(self, event):
        """Handle WebRTC signaling events."""

        data = event["data"]
        data["username"] = event["username"]

        await self.send(text_data=json.dumps(data))

    @sync_to_async
    def user_has_access(self, user, room_id):
        """Check whether the user has access to the chat room."""

        return ChatRoom.objects.filter(
            id=room_id,
            users=user
        ).exists()

    @sync_to_async
    def save_message(self, message):
        """Save a chat message to the database."""

        room = ChatRoom.objects.get(id=self.room_id)

        ChatMessage.objects.create(
            room=room,
            sender=self.scope["user"],
            message=message
        )

    async def chat_image(self, event):
        """Send image messages to connected users."""

        await self.send(text_data=json.dumps({
            "type": "image",
            "username": event["username"],
            "image_url": event["image_url"],
        }))

    @sync_to_async
    def can_make_call(self):
        """Allow up to 2 calls per day."""

        from django.utils import timezone

        today = timezone.now().date()

        calls_today = CallLog.objects.filter(
            caller=self.scope["user"],
            started_at__date=today
        ).count()
        return calls_today < 100

    @sync_to_async
    def save_call_log(self):
        """Save a call log entry to the database."""

        room = ChatRoom.objects.get(id=self.room_id)

        receiver = room.users.exclude(
            id=self.scope["user"].id
        ).first()

        if receiver:
            CallLog.objects.create(
                caller=self.scope["user"],
                receiver=receiver
            )

    @sync_to_async
    def get_receiver(self):
        """Get the other participant in the room."""

        room = ChatRoom.objects.get(
            id=self.room_id
        )

        return room.users.exclude(
            id=self.scope["user"].id
        ).first()


class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.user_group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def incoming_call(self, event):
        await self.send(text_data=json.dumps({
            "type": "incoming_call",
            "username": event["username"],
            "room_id": event["room_id"],
        }))
