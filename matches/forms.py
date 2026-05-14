from django import forms
from .models import LikePost


class LikePostForm(forms.ModelForm):
    class Meta:
        model = LikePost
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "Share something with liked people...",
                "rows": 3,
            })
        }