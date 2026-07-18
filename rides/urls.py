from django.urls import path

from . import views


app_name = "rides"

urlpatterns = [
    # Home pages
    path(
        "",
        views.ride_home,
        name="ride_home",
    ),
    path(
        "drivers/",
        views.ride_list,
        name="driver_ride_list",
    ),
    path(
        "clients/",
        views.client_ride_list,
        name="client_ride_list",
    ),

    # Driver rides
    path(
        "create/",
        views.create_ride,
        name="create_ride",
    ),
    path(
        "activity/",
        views.ride_activity,
        name="ride_activity",
    ),
    path(
        "<int:pk>/",
        views.ride_detail,
        name="ride_detail",
    ),
    path(
        "<int:pk>/edit/",
        views.edit_ride,
        name="edit_ride",
    ),
    path(
        "<int:pk>/cancel/",
        views.cancel_ride,
        name="cancel_ride",
    ),
    path(
        "<int:pk>/request/",
        views.request_ride,
        name="request_ride",
    ),

    # Open passenger requests
    path(
        "requests/<int:request_pk>/rides/<int:ride_pk>/accept/",
        views.accept_open_request,
        name="accept_open_request",
    ),
    path(
        "requests/<int:request_pk>/decline/",
        views.decline_open_request,
        name="decline_open_request",
    ),

    # Existing ride requests
    path(
        "requests/<int:pk>/accept/",
        views.accept_request,
        name="accept_request",
    ),
    path(
        "requests/<int:pk>/reject/",
        views.reject_request,
        name="reject_request",
    ),
]
