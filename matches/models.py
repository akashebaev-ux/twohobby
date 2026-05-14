from django.db import models
from django.contrib.auth.models import User


class Swipe(models.Model):
    LIKE = "like"
    PASS = "pass"

    ACTION_CHOICES = [
        (LIKE, "Like"),
        (PASS, "Pass"),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="swipes_made"
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="swipes_received"
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user} {self.action} {self.to_user}"
    

class LikePost(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="like_posts"
    )

    body = models.TextField(
        max_length=500
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.author} - {self.body[:30]}"