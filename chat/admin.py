from django.contrib import admin

from .models import (
    ChatRoom,
    ChatMessage,
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):

    list_display = (
        "id",
    )

    filter_horizontal = (
        "users",
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        "sender",
        "room",
        "created_on",
    )

    search_fields = (
        "sender__username",
        "message",
    )

    list_filter = (
        "created_on",
    )

    readonly_fields = (
        "created_on",
    )

    ordering = (
        "-created_on",
    )
