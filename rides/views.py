from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RideForm
from .models import Ride

# Create your views here.


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
