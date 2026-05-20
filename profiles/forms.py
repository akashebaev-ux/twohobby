from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
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
