from django.conf import settings
from django.db import models
from django.db.models import Sum


class Ride(models.Model):
    STATUS_PLANNED = "planned"
    STATUS_FULL = "full"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_PLANNED, "Planned"),
        (STATUS_FULL, "Full"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rides_created",
    )

    start_name = models.CharField(max_length=255)
    destination_name = models.CharField(max_length=255)

    start_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    start_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    destination_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    destination_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    departure_time = models.DateTimeField()
    available_seats = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.start_name} to "
            f"{self.destination_name}"
        )

    @property
    def remaining_seats(self):
        reserved = self.requests.filter(
            status=RideRequest.STATUS_ACCEPTED
        ).aggregate(
            total=Sum("seats_requested")
        )["total"] or 0

        return max(
            self.available_seats - reserved,
            0,
        )


class RideRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="requests",
    )

    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ride_requests",
    )

    seats_requested = models.PositiveIntegerField(
        default=1,
    )

    pickup_point = models.CharField(
        max_length=255,
    )

    dropoff_point = models.CharField(
        max_length=255,
    )

    offered_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    message = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "ride",
                    "passenger",
                ],
                name="unique_passenger_ride_request",
            )
        ]

    def __str__(self):
        return (
            f"{self.passenger} - "
            f"{self.ride}"
        )
