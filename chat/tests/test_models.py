from django.test import TestCase
from django.contrib.auth.models import User

from chat.models import (
    ChatRoom,
    ChatMessage,
    CallLog
)


class TestChatModels(TestCase):

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

    def test_chat_room_creation(self):

        self.assertEqual(
            self.room.users.count(),
            2
        )

    def test_chat_room_string_method(self):

        self.assertEqual(
            str(self.room),
            f"ChatRoom {self.room.id}"
        )

    def test_chat_message_creation(self):

        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.user_a,
            message="Hello there"
        )

        self.assertEqual(
            message.room,
            self.room
        )

        self.assertEqual(
            message.sender,
            self.user_a
        )

        self.assertEqual(
            message.message,
            "Hello there"
        )

    def test_chat_message_string_method(self):

        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.user_a,
            message="Hello there"
        )

        self.assertEqual(
            str(message),
            "usera: Hello there"
        )

    def test_call_log_creation(self):

        call = CallLog.objects.create(
            caller=self.user_a,
            receiver=self.user_b
        )

        self.assertEqual(
            call.caller,
            self.user_a
        )

        self.assertEqual(
            call.receiver,
            self.user_b
        )

    def test_call_log_string_method(self):

        call = CallLog.objects.create(
            caller=self.user_a,
            receiver=self.user_b
        )

        self.assertEqual(
            str(call),
            "usera called userb"
        )
