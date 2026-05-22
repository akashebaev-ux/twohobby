"""Database models for chat, messaging, and call functionality."""

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models


class ChatRoom(models.Model):
    """
    Stores a private chat room related to multiple
    :model:`auth.User` instances.
    """

    users = models.ManyToManyField(
        User,
        related_name="chat_rooms"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable representation of the chat room."""

        return f"ChatRoom {self.id}"


class ChatMessage(models.Model):
    """
    Stores a single chat message related to a
    :model:`chat.ChatRoom` and :model:`auth.User`.
    """

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    message = models.TextField(blank=True)

    image = CloudinaryField(
        "image",
        blank=True,
        null=True
    )

    created_on = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        """Return a readable representation of the chat message."""

        return f"{self.sender.username}: {self.message[:20]}"


class CallLog(models.Model):
    """
    Stores a call activity entry between two
    :model:`auth.User` instances.
    """

    caller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="calls_made"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="calls_received"
    )

    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable representation of the call log."""

        return f"{self.caller} called {self.receiver}"
