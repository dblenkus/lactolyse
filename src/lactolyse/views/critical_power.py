"""Views for Lactate Threshold Analysis."""
import os

from asgiref.sync import async_to_sync

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import formset_factory
from django.urls import reverse_lazy

from channels.layers import get_channel_layer

from lactolyse.forms import AthleteForm, CriticalPowerMeasurementForm
from lactolyse.models import CriticalPowerAnalyses
from lactolyse.protocol import (
    CRITICAL_POWER_REPORT_TYPE,
    GROUP_SESSIONS,
    RUN_ANALYSIS_CHANNEL,
)

from .base import MultiFormView


class CriticalPowerTestView(LoginRequiredMixin, MultiFormView):
    """Critical Power Test view."""

    template_name = os.path.join('lactolyse', 'critical_power.html')
    analyses_name = 'critical_power'
    success_url = reverse_lazy('analyses_success')

    form_classes = {
        'athlete': AthleteForm,
        'measurements': formset_factory(
            CriticalPowerMeasurementForm, min_num=3, extra=2, validate_min=True
        ),
    }

    def get_initial(self):
        """Return initial values if ``DEBUG`` setting is set to ``True``."""
        if not settings.DEBUG:
            return {}

        return {
            'athlete': {'name': "Domen Blenkuš", 'age': "28", 'weight': 74.5},
            'measurements': [
                {'time': 180, 'power': 443},
                {'time': 300, 'power': 386},
                {'time': 720, 'power': 347},
            ],
        }

    def _save_data(self, forms):
        """Save data."""
        with transaction.atomic():
            athlete = forms['athlete'].save(contributor=self.request.user)

            analyses = CriticalPowerAnalyses.objects.create(
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
                'type': CRITICAL_POWER_REPORT_TYPE,
                'analysis_pk': analysis.pk,
                'notify_channel': GROUP_SESSIONS.format(websocket_id=session_id),
            },
        )

        return super().forms_valid(forms)
