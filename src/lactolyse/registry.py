"""Analyses registry."""
import logging

logger = logging.getLogger(__name__)

__all__ = ('registry',)


class AnalysesRegistry:
    _analyses = {}

    def add(self, analysis):
        self._analyses[analysis.name] = analysis

        logger.info("Registered analysis: %s", analysis.name)

    def get(self, analysis_name):
        if analysis_name not in self._analyses:
            raise ValueError(
                "Unknown analysis '{}', select one of the following: {}".format(
                    analysis_name, ", ".join(self._analyses.keys())
                )
            )

        return self._analyses[analysis_name]


registry = AnalysesRegistry()
