"""Signals for automatically creating user profiles."""


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile automatically when a new user is created."""

    if created:
        Profile.objects.create(
            user=instance,
            display_name=instance.username,
            bio="",
            location="",
            gender="other",
            looking_for="everyone",
        )
