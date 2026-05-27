from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from chat.models import ChatRoom, ChatMessage


class TestChatViews(TestCase):

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

    def test_chat_list_page_renders(self):

        self.client.login(
            username="usera",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("chat_list")
        )

        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_redirected_from_chat_list(self):

        response = self.client.get(
            reverse("chat_list")
        )

        self.assertNotEqual(response.status_code, 200)

    def test_room_page_renders(self):

        self.client.login(
            username="usera",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("room", args=[self.room.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_start_chat_creates_room(self):

        self.client.login(
            username="usera",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("start_chat", args=[self.user_b.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_delete_chat(self):

        self.client.login(
            username="usera",
            password="testpassword123"
        )

        response = self.client.post(
            reverse("delete_chat", args=[self.room.id]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            ChatRoom.objects.filter(
                id=self.room.id
            ).exists()
        )

    def test_message_creation(self):

        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.user_a,
            message="Hello test"
        )

        self.assertEqual(
            message.message,
            "Hello test"
        )
