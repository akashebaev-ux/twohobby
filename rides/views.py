from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RideForm, RideRequestForm
from .models import Ride, RideRequest
from .services import users_are_trusted


@login_required
def ride_list(request):
    rides = Ride.objects.all().order_by("departure_time")

    return render(
        request,
        "rides/ride_list.html",
        {"rides": rides},
    )


@login_required
def create_ride(request):
    if request.method == "POST":
        form = RideForm(request.POST)

        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()

            return redirect(
                "rides:ride_detail",
                pk=ride.pk,
            )
    else:
        form = RideForm()

    return render(
        request,
        "rides/create_ride.html",
        {"form": form},
    )


@login_required
def ride_detail(request, pk):
    ride = get_object_or_404(
        Ride,
        pk=pk,
    )

    passenger_requests = None

    if ride.driver == request.user:
        passenger_requests = ride.requests.select_related(
            "passenger"
        )

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
            instance=ride,
        )

        if form.is_valid():
            form.save()

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
                > ride.available_seats
            ):
                form.add_error(
                    "seats_requested",
                    (
                        "You cannot request more seats "
                        "than the ride capacity."
                    ),
                )
            else:
                ride_request = form.save(
                    commit=False
                )

                ride_request.ride = ride

                ride_request.passenger = (
                    request.user
                )

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
        form = RideRequestForm()

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

    return redirect(
        "rides:ride_detail",
        pk=ride_request.ride.pk,
    )
