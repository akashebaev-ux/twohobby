"""Application configuration for the matches app."""


from django.apps import AppConfig


class MatchesConfig(AppConfig):
    """Configuration class for the matches application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "matches"
