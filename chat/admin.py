from django.contrib import admin

from .models import (
    Profile,
    ChatRoom,
    ChatMessage,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "display_name",
        "age",
        "gender",
        "looking_for",
        "location",
        "is_active",
    )

    search_fields = (
        "display_name",
        "location",
        "bio",
    )

    list_filter = (
        "gender",
        "looking_for",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    ordering = (
        "-created_on",
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
