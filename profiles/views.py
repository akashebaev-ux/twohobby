from django.shortcuts import render
from django.views import generic
from .models import Profile

# Create your views here.
class ProfileListView(generic.ListView):
    queryset = Profile.objects.all()
    template_name = 'profiles/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return Profile.objects.filter(is_active=True)