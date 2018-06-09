from django.apps import AppConfig


class LactolyseConfig(AppConfig):
    name = 'lactolyse'

    def ready(self):
        """Perform application initialization."""
        from .executors import executor
