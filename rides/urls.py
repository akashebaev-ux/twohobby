from django.urls import path

from . import views


app_name = "rides"

urlpatterns = [
    path(
        "",
        views.ride_list,
        name="ride_list",
    ),
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
        "requests/<int:pk>/accept/",
        views.accept_request,
        name="accept_request",
    ),
    path(
        "requests/<int:pk>/reject/",
        views.reject_request,
        name="reject_request",
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
]
