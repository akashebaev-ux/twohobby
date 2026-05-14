from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm
from matches.models import Swipe
import json
from django.http import JsonResponse

# Create your views here.
class ProfileListView(generic.ListView):
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        queryset = Profile.objects.filter(is_active=True)

        if self.request.user.is_authenticated:
            queryset = queryset.exclude(user=self.request.user)

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

    profile = Profile.objects.filter(
        is_active=True
    ).exclude(
        user=request.user
    ).exclude(
        user__id__in=swiped_users
    ).first()

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