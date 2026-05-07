from . import views
from django.urls import path

urlpatterns = [
    path('', views.ProfileListView.as_view(), name='profile_list'),
    path('profile/<int:id>/', views.profile_detail, name='profile_detail'),
]