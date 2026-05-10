from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from .models import Profile

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