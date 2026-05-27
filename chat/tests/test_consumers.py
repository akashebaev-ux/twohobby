from django.test import TransactionTestCase
from django.contrib.auth.models import User

from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from config.asgi import application

from chat.models import ChatRoom, ChatMessage


class TestChatConsumer(TransactionTestCase):

    def setUp(self):

        self.user_a = User.objects.create_user(
            username="usera",
            password="testpassword123"
        )

        self.user_b = User.objects.create_user(
            username="userb",
            password="testpassword123"
        )

        self.room = ChatRoom.objects.create()

        self.room.users.add(
            self.user_a,
            self.user_b
        )

    async def test_websocket_connects(self):

        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )

        communicator.scope["user"] = self.user_a

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_anonymous_user_rejected(self):

        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )

        connected, _ = await communicator.connect()

        self.assertFalse(connected)

    async def test_chat_message_sent(self):

        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )

        communicator.scope["user"] = self.user_a

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.send_json_to({
            "message": "Hello from test"
        })

        response = await communicator.receive_json_from()

        self.assertEqual(
            response["message"],
            "Hello from test"
        )

        self.assertEqual(
            response["type"],
            "chat_message"
        )

        exists = await database_sync_to_async(
            ChatMessage.objects.filter(
                message="Hello from test"
            ).exists
        )()

        self.assertTrue(exists)

        await communicator.disconnect()

    async def test_webrtc_offer_signal(self):

        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{self.room.id}/"
        )

        communicator.scope["user"] = self.user_a

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.send_json_to({
            "type": "webrtc_offer",
            "sdp": "fake_sdp"
        })

        response = await communicator.receive_json_from()

        self.assertEqual(
            response["type"],
            "webrtc_offer"
        )

        self.assertEqual(
            response["sdp"],
            "fake_sdp"
        )

        await communicator.disconnect()
