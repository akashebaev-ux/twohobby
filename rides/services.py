from datetime import datetime

from matches.models import Swipe

from .models import TRIP_RECURRING, RideRequest


def users_are_trusted(user_a, user_b):
    user_a_likes_b = Swipe.objects.filter(
        from_user=user_a,
        to_user=user_b,
        action="like",
    ).exists()

    user_b_likes_a = Swipe.objects.filter(
        from_user=user_b,
        to_user=user_a,
        action="like",
    ).exists()

    return (
        user_a_likes_b
        and user_b_likes_a
    )


def comma_separated_days(value):
    if not value:
        return set()

    return {
        day.strip().lower()
        for day in value.split(",")
        if day.strip()
    }


def time_difference_minutes(time_a, time_b):
    today = datetime.today().date()

    datetime_a = datetime.combine(
        today,
        time_a,
    )
    datetime_b = datetime.combine(
        today,
        time_b,
    )

    difference = abs(
        datetime_a - datetime_b
    )

    return difference.total_seconds() / 60


def bid_matches_ride(bid):
    ride = bid.ride

    if bid.seats_requested > ride.remaining_seats:
        return False

    if bid.preferred_time:
        ride_time = ride.departure_time.time()

        difference = time_difference_minutes(
            bid.preferred_time,
            ride_time,
        )

        if difference > 30:
            return False

    if (
        bid.trip_type == TRIP_RECURRING
        and ride.trip_type != TRIP_RECURRING
    ):
        return False

    if (
        bid.trip_type == TRIP_RECURRING
        and ride.trip_type == TRIP_RECURRING
    ):
        bid_days = comma_separated_days(
            bid.recurring_days
        )

        ride_days = comma_separated_days(
            ride.recurring_days
        )

        if not bid_days.intersection(ride_days):
            return False

    return True


def open_request_matches_ride(
    ride_request,
    ride,
):
    if ride_request.status != RideRequest.STATUS_PENDING:
        return False

    if ride_request.ride_id is not None:
        return False

    if (
        ride_request.preferred_date
        != ride.departure_time.date()
    ):
        return False

    request_start = (
        ride_request.pickup_point
        .strip()
        .casefold()
    )

    request_destination = (
        ride_request.dropoff_point
        .strip()
        .casefold()
    )

    ride_start = (
        ride.start_name
        .strip()
        .casefold()
    )

    ride_destination = (
        ride.destination_name
        .strip()
        .casefold()
    )

    if request_start not in ride_start:
        return False

    if request_destination not in ride_destination:
        return False

    difference = time_difference_minutes(
        ride_request.preferred_time,
        ride.departure_time.time(),
    )

    if difference > 30:
        return False

    if (
        ride_request.seats_requested
        > ride.remaining_seats
    ):
        return False

    return True
