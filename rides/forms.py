from django import forms

from .models import (
    Ride,
    RideRequest,
    TRIP_RECURRING,
)

CAR_MODELS = {
    "Toyota": [
        "Camry",
        "Corolla",
        "RAV4",
        "Land Cruiser",
        "Highlander",
        "Prius",
    ],
    "Hyundai": [
        "Accent",
        "Elantra",
        "Sonata",
        "Tucson",
        "Santa Fe",
    ],
    "Kia": [
        "Rio",
        "Cerato",
        "K5",
        "Sportage",
        "Sorento",
    ],
    "Chevrolet": [
        "Cobalt",
        "Nexia",
        "Malibu",
        "Tracker",
        "Tahoe",
    ],
    "Lexus": [
        "ES",
        "RX",
        "NX",
        "GX",
        "LX",
    ],
    "Mercedes-Benz": [
        "A-Class",
        "C-Class",
        "E-Class",
        "S-Class",
        "GLC",
        "GLE",
    ],
    "BMW": [
        "3 Series",
        "5 Series",
        "7 Series",
        "X3",
        "X5",
        "X7",
    ],
    "Audi": [
        "A3",
        "A4",
        "A6",
        "Q3",
        "Q5",
        "Q7",
    ],
    "Volkswagen": [
        "Polo",
        "Jetta",
        "Passat",
        "Tiguan",
        "Touareg",
    ],
    "Nissan": [
        "Almera",
        "Qashqai",
        "X-Trail",
        "Patrol",
    ],
    "Honda": [
        "Civic",
        "Accord",
        "CR-V",
        "Pilot",
    ],
    "Skoda": [
        "Rapid",
        "Octavia",
        "Superb",
        "Kodiaq",
    ],
    "Renault": [
        "Logan",
        "Duster",
        "Kaptur",
        "Arkana",
    ],
    "Other": [
        "Other",
    ],
}


CAR_BRAND_CHOICES = [
    ("", "Choose car brand"),
] + [
    (brand, brand)
    for brand in CAR_MODELS
]

DAY_CHOICES = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
]


class ClientRideSearchForm(forms.Form):
    start_name = forms.CharField(
        label="From",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "ride-search-input",
                "placeholder": "Pickup location",
                "autocomplete": "off",
            },
        ),
    )

    destination_name = forms.CharField(
        label="To",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "ride-search-input",
                "placeholder": "Destination",
                "autocomplete": "off",
            },
        ),
    )

    preferred_date = forms.DateField(
        label="Date",
        widget=forms.DateInput(
            attrs={
                "class": "ride-search-input",
                "type": "date",
            },
        ),
    )

    preferred_time = forms.TimeField(
        label="Time",
        widget=forms.TimeInput(
            attrs={
                "class": "ride-search-input",
                "type": "time",
            },
        ),
    )

    seats_requested = forms.IntegerField(
        label="Passengers",
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                "class": "ride-search-input",
                "min": "1",
            },
        ),
    )

    offered_price = forms.DecimalField(
        label="Your offer",
        min_value=1,
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "ride-search-input",
                "placeholder": "Price in ₸",
                "min": "1",
                "step": "100",
            },
        ),
    )


class RideForm(forms.ModelForm):
    recurring_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    car_brand = forms.ChoiceField(
        choices=CAR_BRAND_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "driver-form-input",
                "id": "id_car_brand",
            }
        ),
    )

    car_model = forms.ChoiceField(
        choices=[
            ("", "Choose car model"),
        ],
        widget=forms.Select(
            attrs={
                "class": "driver-form-input",
                "id": "id_car_model",
            }
        ),
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
            "start_name": forms.TextInput(
                attrs={
                    "class": "driver-form-input",
                    "placeholder": "Starting point",
                }
            ),
            "destination_name": forms.TextInput(
                attrs={
                    "class": "driver-form-input",
                    "placeholder": "Destination",
                }
            ),
            "departure_time": forms.DateTimeInput(
                attrs={
                    "class": "driver-form-input",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "available_seats": forms.NumberInput(
                attrs={
                    "class": "driver-form-input",
                    "min": 1,
                    "max": 8,
                }
            ),
            "car_year": forms.NumberInput(
                attrs={
                    "class": "driver-form-input",
                    "min": 1980,
                    "max": 2030,
                    "placeholder": "Car year",
                }
            ),
            "car_image": forms.ClearableFileInput(
                attrs={
                    "class": "driver-file-input",
                    "accept": "image/*",
                }
            ),
            "trip_type": forms.Select(
                attrs={
                    "class": "driver-form-input",
                    "id": "id_trip_type",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "driver-form-input",
                    "rows": 4,
                    "placeholder": (
                        "Additional information about your trip"
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["departure_time"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

        selected_brand = ""

        if self.is_bound:
            selected_brand = self.data.get(
                "car_brand",
                "",
            )
        elif self.instance and self.instance.pk:
            selected_brand = self.instance.car_brand

        if selected_brand in CAR_MODELS:
            self.fields["car_model"].choices = [
                ("", "Choose car model"),
            ] + [
                (model, model)
                for model in CAR_MODELS[selected_brand]
            ]

        selected_days = []

        if self.instance and self.instance.pk:
            if self.instance.recurring_days:
                selected_days = [
                    day.strip()
                    for day in (
                        self.instance.recurring_days.split(",")
                    )
                    if day.strip()
                ]

        self.initial["recurring_days"] = selected_days

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
                (
                    "Choose at least one day "
                    "for a recurring trip."
                ),
            )

        return cleaned_data

    def save(self, commit=True):
        ride = super().save(commit=False)

        recurring_days = self.cleaned_data.get(
            "recurring_days",
            [],
        )

        ride.recurring_days = ",".join(
            recurring_days
        )

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
            "pickup_point": forms.TextInput(
                attrs={
                    "class": "ride-search-input",
                    "placeholder": "Pickup location",
                    "autocomplete": "off",
                },
            ),
            "dropoff_point": forms.TextInput(
                attrs={
                    "class": "ride-search-input",
                    "placeholder": "Destination",
                    "autocomplete": "off",
                },
            ),
            "preferred_time": forms.TimeInput(
                attrs={
                    "class": "ride-search-input",
                    "type": "time",
                },
            ),
            "seats_requested": forms.NumberInput(
                attrs={
                    "class": "ride-search-input",
                    "min": "1",
                },
            ),
            "offered_price": forms.NumberInput(
                attrs={
                    "class": "ride-search-input",
                    "min": "1",
                    "step": "100",
                    "placeholder": "Price in ₸",
                },
            ),
            "trip_type": forms.Select(
                attrs={
                    "class": "ride-search-input",
                },
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "ride-search-input",
                    "rows": 3,
                    "placeholder": (
                        "Add a message for the driver"
                    ),
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
