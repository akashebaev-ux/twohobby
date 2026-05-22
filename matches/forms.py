"""Forms for creating posts and comments in the matches app."""


from django import forms
from .models import LikePost, LikeComment


class LikePostForm(forms.ModelForm):
    """Form for creating a like post."""

    class Meta:
        model = LikePost
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "Share something with liked people...",
                "rows": 3,
            })
        }


class LikeCommentForm(forms.ModelForm):
    """Form for creating comments on like posts."""

    class Meta:
        model = LikeComment
        fields = ["body"]

        widgets = {
            "body": forms.TextInput(attrs={
                "placeholder": "Reply...",
            })
        }
