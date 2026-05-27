from django.test import TestCase
from django.contrib.auth.models import User


class TestProfileModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

    def test_profile_creation(self):
        profile = self.user.profile

        self.assertEqual(profile.user.username, "testuser")

    def test_profile_string_method(self):
        profile = self.user.profile
        profile.display_name = "Test User"
        profile.save()

        self.assertEqual(str(profile), "Test User")
