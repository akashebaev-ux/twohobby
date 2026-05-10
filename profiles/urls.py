from . import views
from django.urls import path

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('nearby/', views.ProfileListView.as_view(), name='profile_list'),
    path('profile/<int:id>/', views.profile_detail, name='profile_detail'),
    path("my-profile/", views.my_profile, name="my_profile"),
]