"""Admin configuration for the profiles application."""


from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin panel configuration for user profiles."""

    list_display = (
        "display_name",
        "age",
        "gender",
        "looking_for",
        "location",
        "is_active",
    )
    search_fields = ("display_name", "location", "bio")
    list_filter = ("gender", "looking_for", "is_active")
