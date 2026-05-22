"""Forms for creating and updating user profiles."""


from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    class Meta:
        model = Profile
        fields = [
            "display_name",
            "age",
            "bio",
            "location",
            "gender",
            "looking_for",
            "profile_image",
        ]
