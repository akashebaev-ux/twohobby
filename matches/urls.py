from django.urls import path
from . import views

urlpatterns = [
    path(
        "swipe/<int:user_id>/<str:action>/",
        views.swipe_user,
        name="swipe_user"
    ),
    path("likes/", views.likes, name="likes"),
    path(
    "post/<int:post_id>/like/",
    views.toggle_like_post,
    name="toggle_like_post"
    ),
    path(
        "post/<int:post_id>/delete/",
        views.delete_like_post,
        name="delete_like_post"
    ),

    path(
        "post/<int:post_id>/share/",
        views.share_like_post,
        name="share_like_post"
    ),
]