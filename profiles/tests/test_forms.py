from django.test import TestCase

from profiles.forms import ProfileForm


class TestProfileForm(TestCase):

    def test_profile_form_is_valid(self):
        form = ProfileForm(data={
            "display_name": "Test User",
            "age": 25,
            "bio": "Test bio",
            "location": "Almaty",
            "gender": "male",
            "looking_for": "everyone",
            "is_active": True,
        })

        self.assertTrue(form.is_valid())

    def test_profile_form_is_invalid_without_display_name(self):
        form = ProfileForm(data={
            "display_name": "",
            "age": 25,
            "bio": "Test bio",
            "location": "Almaty",
            "gender": "male",
            "looking_for": "everyone",
            "is_active": True,
        })

        self.assertTrue(form.is_valid())

    def test_profile_form_is_invalid_without_age(self):
        form = ProfileForm(data={
            "display_name": "Test User",
            "age": "",
            "bio": "Test bio",
            "location": "Almaty",
            "gender": "male",
            "looking_for": "everyone",
            "is_active": True,
        })

        self.assertTrue(form.is_valid())
