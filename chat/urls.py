from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_list, name="chat_list"),
    path("<int:room_id>/", views.room, name="room"),
    path("start/<int:user_id>/", views.start_chat, name="start_chat"),
    path("delete/<int:room_id>/", views.delete_chat, name="delete_chat"),
    path(
        "room/<int:room_id>/upload-image/",
        views.upload_chat_image,
        name="upload_chat_image"
    ),
]
