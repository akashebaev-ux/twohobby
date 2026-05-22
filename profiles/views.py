import json
from math import radians, sin, cos, sqrt, atan2
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from matches.models import Swipe, BlockedUser
from .forms import ProfileForm
from .models import Profile


def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(earth_radius * c, 1)

# Create your views here.


class ProfileListView(LoginRequiredMixin, generic.ListView):
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        queryset = Profile.objects.filter(is_active=True)

        blocked_users = BlockedUser.objects.filter(
            blocker=self.request.user
        ).values_list("blocked", flat=True)

        queryset = queryset.exclude(user__id__in=blocked_users)

        gender = self.request.GET.get("gender")
        min_age = self.request.GET.get("min_age")
        max_age = self.request.GET.get("max_age")

        if gender:
            queryset = queryset.filter(gender=gender)

        if min_age:
            queryset = queryset.filter(age__gte=min_age)

        if max_age:
            queryset = queryset.filter(age__lte=max_age)

        if self.request.user.is_authenticated:
            queryset = queryset.exclude(user=self.request.user)

            user_profile = self.request.user.profile

            if user_profile.latitude and user_profile.longitude:
                for profile in queryset:
                    if profile.latitude and profile.longitude:
                        profile.distance = calculate_distance(
                            user_profile.latitude,
                            user_profile.longitude,
                            profile.latitude,
                            profile.longitude
                        )
                    else:
                        profile.distance = None

        return queryset


def profile_detail(request, id):
    profile = get_object_or_404(Profile, id=id)
    return render(request, 'profiles/profile_detail.html', {
        'profile': profile
    })


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('profile_list')
    return render(request, 'landing.html')


@login_required
def my_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "display_name": request.user.username,
        }
    )

    return render(request, "profiles/my_profile.html", {
        "profile": profile
    })


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("my_profile")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "profiles/edit_profile.html",
        {"form": form}
    )


@login_required
def encounters(request):
    swiped_users = Swipe.objects.filter(
        from_user=request.user
    ).values_list("to_user", flat=True)

    blocked_users = BlockedUser.objects.filter(
        blocker=request.user
    ).values_list("blocked", flat=True)

    queryset = Profile.objects.filter(
        is_active=True
    ).exclude(
        user=request.user
    ).exclude(
        user__id__in=swiped_users
    ).exclude(
        user__id__in=blocked_users
    )

    gender = request.GET.get("gender")
    min_age = request.GET.get("min_age")
    max_age = request.GET.get("max_age")

    if gender:
        queryset = queryset.filter(gender=gender)

    if min_age:
        queryset = queryset.filter(age__gte=min_age)

    if max_age:
        queryset = queryset.filter(age__lte=max_age)

    profile = queryset.first()

    return render(request, "profiles/encounters.html", {
        "profile": profile
    })


@login_required
def save_location(request):
    if request.method == "POST":
        data = json.loads(request.body)

        profile = request.user.profile
        profile.latitude = data.get("latitude")
        profile.longitude = data.get("longitude")
        profile.save()

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)
