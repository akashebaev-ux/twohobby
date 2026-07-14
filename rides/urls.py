from django.urls import path
from . import views

app_name = 'rides'

urlpatterns = [
    path("", views.ride_list, name="ride_list"),
    path("create/", views.create_ride, name="create_ride"),
]
