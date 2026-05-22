"""Database models for matching, posts, comments, and blocking users."""


from django.contrib.auth.models import User
from django.db import models


class Swipe(models.Model):
    """
    Stores a swipe action between two
    :model:`auth.User` instances.
    """

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
        # Prevent duplicate swipes between users
        unique_together = ("from_user", "to_user")

    def __str__(self):
        """Return a readable representation of the swipe."""

        return f"{self.from_user} {self.action} {self.to_user}"


class LikePost(models.Model):
    """
    Stores a single post created by a
    :model:`auth.User`.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="like_posts"
    )

    body = models.TextField(
        max_length=500
    )

    liked_by = models.ManyToManyField(
        User,
        related_name="liked_like_posts",
        blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        # Show newest posts first
        ordering = ["-created_on"]

    def __str__(self):
        """Return a readable representation of the post."""

        return f"{self.author} - {self.body[:30]}"


class LikeComment(models.Model):
    """
    Stores a single comment related to a
    :model:`matches.LikePost`.
    """

    post = models.ForeignKey(
        LikePost,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    body = models.TextField(
        max_length=300
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """Return a readable representation of the comment."""

        return f"{self.author} comment"


class BlockedUser(models.Model):
    """
    Stores a blocked relationship between two
    :model:`auth.User` instances.
    """

    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blocked_users"
    )

    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blocked_by_users"
    )

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")

    def __str__(self):
        """Return a readable representation of the blocked user."""

        return f"{self.blocker} blocked {self.blocked}"
