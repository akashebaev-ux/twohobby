from django.shortcuts import render

def chat_list(request):
    return render(request, "chat/chat_list.html")

def room(request, room_name):
    return render(request, "chat/room.html", {
        "room_name": room_name
    })
