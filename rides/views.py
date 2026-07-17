from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    ClientRideSearchForm,
    RideForm,
    RideRequestForm,
)
from .models import Ride, RideRequest
from .services import (
    bid_matches_ride,
    time_difference_minutes,
    users_are_trusted,
)


@login_required
def ride_list(request):
    rides = (
        Ride.objects
        .filter(
            status=Ride.STATUS_PLANNED,
        )
        .select_related("driver")
        .order_by("departure_time")
    )

    map_rides = []

    for ride in rides:
        if (
            ride.start_latitude is not None
            and ride.start_longitude is not None
            and ride.destination_latitude is not None
            and ride.destination_longitude is not None
        ):
            map_rides.append(
                {
                    "id": ride.pk,
                    "start_name": ride.start_name,
                    "destination_name": (
                        ride.destination_name
                    ),
                    "start_latitude": float(
                        ride.start_latitude
                    ),
                    "start_longitude": float(
                        ride.start_longitude
                    ),
                    "destination_latitude": float(
                        ride.destination_latitude
                    ),
                    "destination_longitude": float(
                        ride.destination_longitude
                    ),
                    "remaining_seats": (
                        ride.remaining_seats
                    ),
                    "departure_time": (
                        ride.departure_time.isoformat()
                    ),
                    "detail_url": reverse(
                        "rides:ride_detail",
                        kwargs={
                            "pk": ride.pk,
                        },
                    ),
                }
            )

    return render(
        request,
        "rides/ride_list.html",
        {
            "rides": rides,
            "map_rides": map_rides,
        },
    )


@login_required
def create_ride(request):
    if request.method == "POST":
        form = RideForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()

            messages.success(
                request,
                "Your driving plan has been created.",
            )

            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )
    else:
        form = RideForm()

    return render(
        request,
        "rides/create_ride.html",
        {
            "form": form,
        },
    )


@login_required
def ride_detail(request, pk):
    ride = get_object_or_404(
        Ride,
        pk=pk,
    )

    passenger_requests = None

    if ride.driver == request.user:
        passenger_requests = (
            ride.requests
            .select_related(
                "passenger",
                "passenger__profile",
            )
            .order_by("-created_at")
        )

        for bid in passenger_requests:
            bid.matches = bid_matches_ride(bid)

    return render(
        request,
        "rides/ride_detail.html",
        {
            "ride": ride,
            "passenger_requests": passenger_requests,
        },
    )


@login_required
def edit_ride(request, pk):
    ride = get_object_or_404(
        Ride,
        pk=pk,
        driver=request.user,
    )

    if request.method == "POST":
        form = RideForm(
            request.POST,
            request.FILES,
            instance=ride,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Your driving plan has been updated.",
            )

            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )
    else:
        form = RideForm(instance=ride)

    return render(
        request,
        "rides/edit_ride.html",
        {
            "form": form,
            "ride": ride,
        },
    )


@login_required
@require_POST
def cancel_ride(request, pk):
    ride = get_object_or_404(
        Ride,
        pk=pk,
        driver=request.user,
    )

    ride.status = Ride.STATUS_CANCELLED
    ride.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        "Your driving plan has been cancelled.",
    )

    return redirect(
        "rides:ride_detail",
        pk=ride.pk,
    )


@login_required
def request_ride(request, pk):
    ride = get_object_or_404(
        Ride,
        pk=pk,
    )

    if ride.driver == request.user:
        messages.error(
            request,
            "You cannot request to join your own ride.",
        )

        return redirect(
            "rides:ride_detail",
            pk=ride.pk,
        )

    if ride.status != Ride.STATUS_PLANNED:
        messages.error(
            request,
            "This ride is not accepting requests.",
        )

        return redirect(
            "rides:ride_detail",
            pk=ride.pk,
        )

    if not users_are_trusted(
        request.user,
        ride.driver,
    ):
        return HttpResponseForbidden(
            "You cannot request this ride."
        )

    if request.method == "POST":
        form = RideRequestForm(request.POST)

        if form.is_valid():
            if (
                form.cleaned_data["seats_requested"]
                > ride.remaining_seats
            ):
                form.add_error(
                    "seats_requested",
                    (
                        "You cannot request more seats "
                        "than are currently available."
                    ),
                )
            else:
                ride_request = form.save(
                    commit=False
                )

                ride_request.ride = ride
                ride_request.passenger = request.user

                ride_request.save()

                messages.success(
                    request,
                    "Your ride request has been sent.",
                )

                return redirect(
                    "rides:ride_detail",
                    pk=ride.pk,
                )
    else:
        form = RideRequestForm(
            initial={
                "pickup_point": request.GET.get(
                    "pickup_point",
                    "",
                ),
                "dropoff_point": request.GET.get(
                    "dropoff_point",
                    "",
                ),
                "preferred_time": request.GET.get(
                    "preferred_time",
                    "",
                ),
                "seats_requested": request.GET.get(
                    "seats_requested",
                    1,
                ),
                "offered_price": request.GET.get(
                    "offered_price",
                    "",
                ),
                "trip_type": request.GET.get(
                    "trip_type",
                    "",
                ),
            }
        )

    return render(
        request,
        "rides/request_ride.html",
        {
            "form": form,
            "ride": ride,
        },
    )


@login_required
@require_POST
def accept_request(request, pk):
    with transaction.atomic():
        ride_request = (
            RideRequest.objects
            .select_for_update()
            .select_related("ride")
            .get(pk=pk)
        )

        ride = (
            Ride.objects
            .select_for_update()
            .get(pk=ride_request.ride_id)
        )

        if ride.driver != request.user:
            return HttpResponseForbidden()

        if (
            ride_request.status
            != RideRequest.STATUS_PENDING
        ):
            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )

        if ride.status != Ride.STATUS_PLANNED:
            messages.error(
                request,
                "This ride is not accepting requests.",
            )

            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )

        if not bid_matches_ride(ride_request):
            messages.error(
                request,
                (
                    "This bid does not match "
                    "your driving plan."
                ),
            )

            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )

        if (
            ride_request.seats_requested
            > ride.remaining_seats
        ):
            messages.error(
                request,
                "Not enough remaining seats.",
            )

            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )

        ride_request.status = (
            RideRequest.STATUS_ACCEPTED
        )

        ride_request.save(
            update_fields=["status"]
        )

        if ride.remaining_seats == 0:
            ride.status = Ride.STATUS_FULL

            ride.save(
                update_fields=["status"]
            )

    messages.success(
        request,
        "The client bid has been accepted.",
    )

    return redirect(
        "rides:ride_detail",
        pk=ride.pk,
    )


@login_required
@require_POST
def reject_request(request, pk):
    ride_request = get_object_or_404(
        RideRequest,
        pk=pk,
        ride__driver=request.user,
        status=RideRequest.STATUS_PENDING,
    )

    ride_request.status = (
        RideRequest.STATUS_REJECTED
    )

    ride_request.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        "The client bid has been rejected.",
    )

    return redirect(
        "rides:ride_detail",
        pk=ride_request.ride.pk,
    )


@login_required
def ride_activity(request):
    created_rides = (
        Ride.objects
        .filter(driver=request.user)
        .order_by("-departure_time")
    )

    passenger_requests = (
        RideRequest.objects
        .filter(passenger=request.user)
        .select_related(
            "ride",
            "ride__driver",
            "ride__driver__profile",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "rides/ride_activity.html",
        {
            "created_rides": created_rides,
            "passenger_requests": passenger_requests,
        },
    )


@login_required
def ride_home(request):
    return render(
        request,
        "rides/ride_home.html",
    )


@login_required
def client_ride_list(request):
    matching_rides = []
    search_performed = False

    if request.method == "POST":
        form = ClientRideSearchForm(request.POST)

        if form.is_valid():
            search_performed = True

            start_name = form.cleaned_data[
                "start_name"
            ]

            destination_name = form.cleaned_data[
                "destination_name"
            ]

            preferred_date = form.cleaned_data[
                "preferred_date"
            ]

            preferred_time = form.cleaned_data[
                "preferred_time"
            ]

            seats_requested = form.cleaned_data[
                "seats_requested"
            ]

            offered_price = form.cleaned_data[
                "offered_price"
            ]

            possible_rides = (
                Ride.objects
                .filter(
                    status=Ride.STATUS_PLANNED,
                    start_name__icontains=start_name,
                    destination_name__icontains=(
                        destination_name
                    ),
                    departure_time__date=preferred_date,
                )
                .exclude(driver=request.user)
                .select_related(
                    "driver",
                    "driver__profile",
                )
                .order_by("departure_time")
            )

            for ride in possible_rides:
                if (
                    ride.remaining_seats
                    < seats_requested
                ):
                    continue

                ride_time = ride.departure_time.time()

                time_difference = (
                    time_difference_minutes(
                        preferred_time,
                        ride_time,
                    )
                )

                if time_difference > 30:
                    continue

                if not users_are_trusted(
                    request.user,
                    ride.driver,
                ):
                    continue

                query_string = urlencode(
                    {
                        "pickup_point": start_name,
                        "dropoff_point": (
                            destination_name
                        ),
                        "preferred_time": (
                            preferred_time.strftime(
                                "%H:%M"
                            )
                        ),
                        "seats_requested": (
                            seats_requested
                        ),
                        "offered_price": (
                            str(offered_price)
                        ),
                        "trip_type": ride.trip_type,
                    }
                )

                ride.bid_url = (
                    reverse(
                        "rides:request_ride",
                        kwargs={
                            "pk": ride.pk,
                        },
                    )
                    + "?"
                    + query_string
                )

                matching_rides.append(ride)
    else:
        form = ClientRideSearchForm()

    return render(
        request,
        "rides/client_ride_list.html",
        {
            "form": form,
            "rides": matching_rides,
            "search_performed": search_performed,
        },
    )
