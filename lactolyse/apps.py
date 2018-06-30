"""Lactolyse configuration."""
from django.apps import AppConfig


class LactolyseConfig(AppConfig):
    """Lactolyse AppConfig."""

    name = 'lactolyse'

    def ready(self):
        """Perform application initialization."""
        from .executors import executor  # pylint: disable=unused-variable
