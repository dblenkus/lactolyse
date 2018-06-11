""".. Ignore pydocstyle D400.
==================
List Docker images
==================
"""
from django.core.management.base import BaseCommand

from lactolyse.executors import executor


class Command(BaseCommand):
    """List Docker images used by the app."""

    help = "List Docker images used by the app"

    def handle(self, *args, **options):
        """Handle command listdockerimages."""

        images = executor.get_docker_images()
        self.stdout.write('\n'.join(images))
