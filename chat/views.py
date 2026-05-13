from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatRoom


@login_required
def chat_list(request):
    rooms = request.user.chat_rooms.all()

    return render(request, "chat/chat_list.html", {
        "rooms": rooms
    })


@login_required
def room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    messages = room.messages.all()

    return render(request, "chat/room.html", {
        "room": room,
        "messages": messages,
    })


@login_required
def start_chat(request, user_id):
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
    room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    if request.method == "POST":
        room.delete()
        return redirect("chat_list")

    return redirect("room", room_id=room.id)