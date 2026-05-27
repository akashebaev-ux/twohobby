from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from matches.models import BlockedUser


class TestMatchViews(TestCase):

    def setUp(self):

        self.user_a = User.objects.create_user(
            username="usera",
            password="testpassword123"
        )

        self.user_b = User.objects.create_user(
            username="userb",
            password="testpassword123"
        )

    def test_logged_in_user_can_block_user(self):

        self.client.login(
            username="usera",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("block_user", args=[self.user_b.id]),
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            BlockedUser.objects.filter(
                blocker=self.user_a,
                blocked=self.user_b
            ).exists()
        )

    def test_logged_out_user_redirected_from_block_user(self):

        response = self.client.get(
            reverse("block_user", args=[self.user_b.id])
        )

        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_user_can_unblock_user(self):

        BlockedUser.objects.create(
            blocker=self.user_a,
            blocked=self.user_b
        )

        self.client.login(
            username="usera",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("unblock_user", args=[self.user_b.id]) + "?room=1"
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            BlockedUser.objects.filter(
                blocker=self.user_a,
                blocked=self.user_b
            ).exists()
        )
