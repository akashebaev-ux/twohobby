"""URL patterns for profile management and matching features."""


from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('nearby/', views.ProfileListView.as_view(), name='profile_list'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path('profile/<int:id>/', views.profile_detail, name='profile_detail'),
    path("my-profile/", views.my_profile, name="my_profile"),
    path("encounters/", views.encounters, name="encounters"),
    path("save-location/", views.save_location, name="save_location"),
]
