from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Profile

# Create your views here.
class ProfileListView(generic.ListView):
    queryset = Profile.objects.all()
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return Profile.objects.filter(is_active=True)
    

def profile_detail(request, id):
    profile = get_object_or_404(Profile, id=id)
    return render(request, 'profiles/profile_detail.html', {
        'profile': profile
    })