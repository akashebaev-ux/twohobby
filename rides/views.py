from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    CAR_MODELS,
    ClientRideSearchForm,
    RideForm,
    RideRequestForm,
)
from .models import Ride, RideRequest
from .services import (
    bid_matches_ride,
    open_request_matches_ride,
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
            "car_models": CAR_MODELS,
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
        ride_request = get_object_or_404(
            RideRequest.objects
            .select_for_update()
            .select_related("ride"),
            pk=pk,
            ride__isnull=False,
            ride__driver=request.user,
            status=RideRequest.STATUS_PENDING,
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
        ride__isnull=False,
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
        .select_related(
            "driver",
            "driver__profile",
        )
        .order_by("-departure_time")
    )

    open_requests = (
        RideRequest.objects
        .filter(
            ride__isnull=True,
            status=RideRequest.STATUS_PENDING,
        )
        .exclude(
            passenger=request.user,
        )
        .exclude(
            rejected_by=request.user,
        )
        .select_related(
            "passenger",
            "passenger__profile",
        )
        .prefetch_related("rejected_by")
        .order_by("-created_at")
    )

    for ride in created_rides:
        incoming_requests = []

        for ride_request in open_requests:
            if not users_are_trusted(
                request.user,
                ride_request.passenger,
            ):
                continue

            incoming_requests.append(
                {
                    "request": ride_request,
                    "matches_schedule": (
                        open_request_matches_ride(
                            ride_request,
                            ride,
                        )
                    ),
                }
            )

        ride.incoming_requests = incoming_requests

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
    submitted_request = None

    if request.method == "POST":
        form = ClientRideSearchForm(request.POST)

        if form.is_valid():
            search_performed = True

            start_name = form.cleaned_data[
                "start_name"
            ].strip()

            destination_name = form.cleaned_data[
                "destination_name"
            ].strip()

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

            submitted_request = (
                RideRequest.objects.create(
                    passenger=request.user,
                    ride=None,
                    pickup_point=start_name,
                    dropoff_point=destination_name,
                    preferred_date=preferred_date,
                    preferred_time=preferred_time,
                    seats_requested=seats_requested,
                    offered_price=offered_price,
                    status=RideRequest.STATUS_PENDING,
                )
            )

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

                difference = time_difference_minutes(
                    preferred_time,
                    ride_time,
                )

                if difference > 30:
                    continue

                if not users_are_trusted(
                    request.user,
                    ride.driver,
                ):
                    continue

                ride.open_request = submitted_request
                matching_rides.append(ride)

            messages.success(
                request,
                (
                    "Your ride request has been saved "
                    "and published to compatible drivers."
                ),
            )
    else:
        form = ClientRideSearchForm()

    my_saved_requests = (
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
        "rides/client_ride_list.html",
        {
            "form": form,
            "rides": matching_rides,
            "search_performed": search_performed,
            "submitted_request": submitted_request,
            "my_saved_requests": my_saved_requests,
        },
    )


@login_required
@require_POST
def accept_open_request(
    request,
    request_pk,
    ride_pk,
):
    with transaction.atomic():
        ride_request = get_object_or_404(
            RideRequest.objects
            .select_for_update()
            .select_related("passenger"),
            pk=request_pk,
        )

        ride = get_object_or_404(
            Ride.objects.select_for_update(),
            pk=ride_pk,
            driver=request.user,
        )

        if (
            ride_request.status
            != RideRequest.STATUS_PENDING
            or ride_request.ride_id is not None
        ):
            messages.error(
                request,
                (
                    "This passenger request is no "
                    "longer available."
                ),
            )

            return redirect(
                "rides:ride_activity"
            )

        if not users_are_trusted(
            request.user,
            ride_request.passenger,
        ):
            return HttpResponseForbidden(
                "You cannot accept this request."
            )

        if not open_request_matches_ride(
            ride_request,
            ride,
        ):
            messages.error(
                request,
                (
                    "This request does not match "
                    "your driving plan."
                ),
            )

            return redirect(
                "rides:ride_activity"
            )

        ride_request.ride = ride
        ride_request.status = (
            RideRequest.STATUS_ACCEPTED
        )

        ride_request.save(
            update_fields=[
                "ride",
                "status",
            ]
        )

        if ride.remaining_seats == 0:
            ride.status = Ride.STATUS_FULL

            ride.save(
                update_fields=["status"]
            )

    messages.success(
        request,
        "The passenger request was accepted.",
    )

    return redirect(
        "rides:ride_activity"
    )


@login_required
@require_POST
def decline_open_request(
    request,
    request_pk,
):
    ride_request = get_object_or_404(
        RideRequest,
        pk=request_pk,
        ride__isnull=True,
        status=RideRequest.STATUS_PENDING,
    )

    if ride_request.passenger == request.user:
        return HttpResponseForbidden()

    ride_request.rejected_by.add(
        request.user
    )

    messages.success(
        request,
        (
            "The request was removed from "
            "your driver dashboard."
        ),
    )

    return redirect(
        "rides:ride_activity"
    )
