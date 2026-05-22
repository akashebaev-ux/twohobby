"""Views for chat rooms, messages, and image uploads."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from matches.models import BlockedUser
from .models import ChatRoom, ChatMessage


@login_required
def chat_list(request):
    """
    Renders all chat rooms related to the logged-in
    :model:`auth.User` instance.
    """

    rooms = request.user.chat_rooms.all()

    return render(request, "chat/chat_list.html", {
        "rooms": rooms
    })


@login_required
def room(request, room_id):
    """
    Renders an individual chat room and its messages.

    Displays an individual instance of :model:`chat.ChatRoom`
    and related instances of :model:`chat.ChatMessage`.
    """

    room = get_object_or_404(
        ChatRoom,
        id=room_id,
        users=request.user
    )

    messages = room.messages.all()

    other_user = room.users.exclude(
        id=request.user.id
    ).first()

    is_blocked = False

    if other_user:
        is_blocked = BlockedUser.objects.filter(
            blocker=request.user,
            blocked=other_user
        ).exists()

    return render(request, "chat/room.html", {
        "room": room,
        "messages": messages,
        "other_user": other_user,
        "is_blocked": is_blocked,
    })


@login_required
def start_chat(request, user_id):
    """
    Creates a new chat room or redirects to an existing one.

    Connects the logged-in :model:`auth.User` with another
    :model:`auth.User`.
    """

    other_user = get_object_or_404(User, id=user_id)

    existing_room = ChatRoom.objects.filter(
        users=request.user
    ).filter(
        users=other_user
    ).first()

    if existing_room:
        return redirect("room", room_id=existing_room.id)

    room = ChatRoom.objects.create()
    room.users.add(request.user, other_user)

    return redirect("room", room_id=room.id)


@login_required
def delete_chat(request, room_id):
    """
    Deletes an individual chat room after a POST request.

    Deletes an instance of :model:`chat.ChatRoom`.
    """

    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    if request.method == "POST":
        room.delete()
        return redirect("chat_list")

    return redirect("room", room_id=room.id)


@login_required
def upload_chat_image(request, room_id):
    """
    Uploads an image message and broadcasts it to the chat room.

    Creates an instance of :model:`chat.ChatMessage`.
    """

    room = get_object_or_404(
        ChatRoom,
        id=room_id,
        users=request.user
    )

    if request.method == "POST":
        image = request.FILES.get("image")

        if image:
            message = ChatMessage.objects.create(
                room=room,
                sender=request.user,
                message="",
                image=image
            )

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f"chat_{room.id}",
                {
                    "type": "chat_image",
                    "username": request.user.username,
                    "image_url": message.image.url,
                }
            )

    return redirect("room", room_id=room.id)
