from django.apps import AppConfig


class FtpConfig(AppConfig):
    name = 'ftp'

    def ready(self):
        """Perform application initialization."""
        from .executors import executor
