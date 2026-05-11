from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

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