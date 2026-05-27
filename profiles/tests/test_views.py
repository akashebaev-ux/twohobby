from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from profiles.models import Profile


class TestProfileViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.profile = self.user.profile

    def test_nearby_page_renders_for_logged_in_user(self):
        self.client.login(
            username="testuser",
            password="testpassword123"
        )

        response = self.client.get(reverse("profile_list"))

        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_redirected_from_nearby(self):
        response = self.client.get(reverse("profile_list"))

        self.assertNotEqual(response.status_code, 200)

    def test_profile_detail_page_renders(self):
        self.client.login(
            username="testuser",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("profile_detail", args=[self.profile.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_edit_profile_page_renders(self):
        self.client.login(
            username="testuser",
            password="testpassword123"
        )

        response = self.client.get(reverse("edit_profile"))

        self.assertEqual(response.status_code, 200)

    def test_user_can_update_profile(self):
        self.client.login(
            username="testuser",
            password="testpassword123"
        )

        data = {
            "display_name": "Updated User",
            "age": 26,
            "bio": "Updated bio",
            "location": "Astana",
            "gender": "male",
            "looking_for": "everyone",
            "is_active": True,
        }

        response = self.client.post(
            reverse("edit_profile"),
            data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Profile.objects.filter(display_name="Updated User").exists()
        )
