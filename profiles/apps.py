"""Application configuration for the profiles app."""


from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """Configuration class for the profiles application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'

    def ready(self):
        """Import signals when the application is ready."""

        import profiles.signals  # noqa
