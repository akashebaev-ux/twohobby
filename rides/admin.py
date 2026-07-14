from django.contrib import admin
from .models import Ride

# Register your models here.


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "driver",
        "start_name",
        "destination_name",
        "departure_time",
        "available_seats",
        "status",
    )

    list_filter = (
        "status",
        "departure_time",
    )

    search_fields = (
        "driver__username",
        "start_name",
        "destination_name",
    )
