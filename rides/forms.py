from django import forms

from .models import (
    Ride,
    RideRequest,
    TRIP_RECURRING,
)


DAY_CHOICES = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
]


class RideForm(forms.ModelForm):
    recurring_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Ride
        fields = [
            "start_name",
            "destination_name",
            "departure_time",
            "available_seats",
            "car_brand",
            "car_model",
            "car_year",
            "car_image",
            "trip_type",
            "recurring_days",
            "description",
        ]

        widgets = {
            "departure_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if (
            self.instance.pk
            and self.instance.recurring_days
        ):
            self.initial["recurring_days"] = (
                self.instance.recurring_days.split(",")
            )

    def clean(self):
        cleaned_data = super().clean()

        trip_type = cleaned_data.get("trip_type")
        recurring_days = cleaned_data.get(
            "recurring_days"
        )

        if (
            trip_type == TRIP_RECURRING
            and not recurring_days
        ):
            self.add_error(
                "recurring_days",
                "Select at least one recurring day.",
            )

        return cleaned_data

    def save(self, commit=True):
        ride = super().save(commit=False)

        days = self.cleaned_data.get(
            "recurring_days",
            [],
        )

        if ride.trip_type == TRIP_RECURRING:
            ride.recurring_days = ",".join(days)
        else:
            ride.recurring_days = ""

        if commit:
            ride.save()

        return ride


class RideRequestForm(forms.ModelForm):
    recurring_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = RideRequest
        fields = [
            "pickup_point",
            "dropoff_point",
            "preferred_time",
            "seats_requested",
            "offered_price",
            "trip_type",
            "recurring_days",
            "message",
        ]

        widgets = {
            "preferred_time": forms.TimeInput(
                attrs={
                    "type": "time",
                },
            ),
            "seats_requested": forms.NumberInput(
                attrs={
                    "min": "1",
                },
            ),
            "offered_price": forms.NumberInput(
                attrs={
                    "min": "1",
                    "step": "100",
                },
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 3,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if (
            self.instance.pk
            and self.instance.recurring_days
        ):
            self.initial["recurring_days"] = (
                self.instance.recurring_days.split(",")
            )

    def clean(self):
        cleaned_data = super().clean()

        pickup = cleaned_data.get("pickup_point")
        dropoff = cleaned_data.get("dropoff_point")
        trip_type = cleaned_data.get("trip_type")
        recurring_days = cleaned_data.get(
            "recurring_days"
        )

        if (
            pickup
            and dropoff
            and pickup.strip().lower()
            == dropoff.strip().lower()
        ):
            self.add_error(
                "dropoff_point",
                "Pickup and drop-off must be different.",
            )

        if (
            trip_type == TRIP_RECURRING
            and not recurring_days
        ):
            self.add_error(
                "recurring_days",
                "Select at least one recurring day.",
            )

        return cleaned_data

    def clean_seats_requested(self):
        seats_requested = self.cleaned_data[
            "seats_requested"
        ]

        if seats_requested < 1:
            raise forms.ValidationError(
                "You must request at least one seat."
            )

        return seats_requested

    def clean_offered_price(self):
        offered_price = self.cleaned_data[
            "offered_price"
        ]

        if offered_price <= 0:
            raise forms.ValidationError(
                "The offered price must be greater than zero."
            )

        return offered_price

    def save(self, commit=True):
        bid = super().save(commit=False)

        days = self.cleaned_data.get(
            "recurring_days",
            [],
        )

        if bid.trip_type == TRIP_RECURRING:
            bid.recurring_days = ",".join(days)
        else:
            bid.recurring_days = ""

        if commit:
            bid.save()

        return bid
