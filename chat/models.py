from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models


class ChatRoom(models.Model):
    users = models.ManyToManyField(
        User,
        related_name="chat_rooms"
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom {self.id}"


class ChatMessage(models.Model):
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
        return f"{self.sender.username}: {self.message[:20]}"


class CallLog(models.Model):
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
