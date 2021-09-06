"""Views for Lactate Threshold Analysis."""
import os

from asgiref.sync import async_to_sync

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import formset_factory
from django.urls import reverse_lazy

from channels.layers import get_channel_layer

from lactolyse.forms import AthleteForm, LactateRunMeasurementForm
from lactolyse.models import LactateThresholdRunAnalyses
from lactolyse.protocol import (
    GROUP_SESSIONS,
    LACTATE_REPORT_RUN_TYPE,
    RUN_ANALYSIS_CHANNEL,
)

from .base import MultiFormView


class LactateThresholdRunView(LoginRequiredMixin, MultiFormView):
    """Lactate Threshold Analisys view."""

    template_name = os.path.join('lactolyse', 'lactate_threshold_run.html')
    analyses_name = 'lactate_threshold_run'
    success_url = reverse_lazy('analyses_success')

    form_classes = {
        'athlete': AthleteForm,
        'measurements': formset_factory(
            LactateRunMeasurementForm, min_num=5, extra=10, validate_min=True
        ),
    }

    def get_initial(self):
        """Return initial values if ``DEBUG`` setting is set to ``True``."""
        if not settings.DEBUG:
            return {}

        return {
            'athlete': {'name': "Domen Blenkuš", 'age': "28", 'weight': 79.5},
            'measurements': [
                {'pace': '6:30', 'heart_rate': 135, 'lactate': 0.9},
                {'pace': '6:00', 'heart_rate': 142, 'lactate': 1.0},
                {'pace': '5:30', 'heart_rate': 150, 'lactate': 1.1},
                {'pace': '5:00', 'heart_rate': 156, 'lactate': 1.2},
                {'pace': '4:30', 'heart_rate': 162, 'lactate': 2.2},
                {'pace': '4:00', 'heart_rate': 170, 'lactate': 5.3},
                {'pace': '3:30', 'heart_rate': 176, 'lactate': 10.1},
            ],
        }

    def _save_data(self, forms):
        """Save data."""
        with transaction.atomic():
            athlete = forms['athlete'].save(contributor=self.request.user)

            analyses = LactateThresholdRunAnalyses.objects.create(
                contributor=self.request.user, athlete=athlete
            )

            measurements = []
            for form in forms['measurements']:
                if form.cleaned_data:
                    measurement = form.save(analyses=analyses)
                    measurements.append(measurement)

        return analyses

    def forms_valid(self, forms):
        """Save data, make report and reference it is Django's session for later views."""
        channel_layer = get_channel_layer()

        analysis = self._save_data(forms)

        session_id = self.request.session.session_key
        async_to_sync(channel_layer.send)(
            RUN_ANALYSIS_CHANNEL,
            {
                'type': LACTATE_REPORT_RUN_TYPE,
                'analysis_pk': analysis.pk,
                'notify_channel': GROUP_SESSIONS.format(websocket_id=session_id),
            },
        )

        return super().forms_valid(forms)
