from django import forms
from .models import Ride, RideRequest


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


class RideRequestForm(forms.ModelForm):
    class Meta:
        model = RideRequest
        fields = [
            "seats_requested",
            "pickup_point",
            "dropoff_point",
            "offered_price",
            "message",
        ]

    def clean_offered_price(self):
        offered_price = self.cleaned_data[
            "offered_price"
        ]

        if offered_price <= 0:
            raise forms.ValidationError(
                "The offered price must be greater than zero."
            )

        return offered_price
