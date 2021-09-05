"""Lactolyse configuration."""
from django.apps import AppConfig


class LactolyseConfig(AppConfig):
    """Lactolyse AppConfig."""

    name = 'lactolyse'

    def ready(self):
        """Perform application initialization."""
        # Register Analyses.
        from lactolyse.analyses.lactate_threshold import LactateThresholdAnalyses
        from lactolyse.analyses.lactate_threshold_run import LactateThresholdRunAnalyses
        from lactolyse.analyses.critical_power import CriticalPowerAnalyses
        from lactolyse.analyses.conconi_test import ConcoinAnalyses

        # Start executor.
        from .executors import executor
