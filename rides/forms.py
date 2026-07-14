from django import forms
from .models import Ride


class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            "start_name",
            "destination_name",
            "departure_time",
            "available_seats",
            "description",
        ]

        widgets = {
            "departure_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 3}
            ),
        }
