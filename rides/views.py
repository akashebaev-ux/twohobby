from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required
def ride_list(request):
    return render(request, "rides/ride_list.html")
