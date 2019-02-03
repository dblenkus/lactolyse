"""Views for Lactate Threshold Analysis."""
import os

from asgiref.sync import async_to_sync

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import formset_factory
from django.urls import reverse_lazy

from channels.layers import get_channel_layer

from lactolyse.forms import AthleteForm, LactateMeasurementForm
from lactolyse.models import LactateThresholdAnalyses
from lactolyse.protocol import GROUP_SESSIONS, LACTATE_REPORT_TYPE, RUN_ANALYSIS_CHANNEL

from .base import MultiFormView


class LactateThresholdView(LoginRequiredMixin, MultiFormView):
    """Lactate Threshold Analisys view."""

    template_name = os.path.join('lactolyse', 'lactate_threshold.html')
    analyses_name = 'lactate_threshold'
    success_url = reverse_lazy('analyses_success')

    form_classes = {
        'athlete': AthleteForm,
        'measurements': formset_factory(
            LactateMeasurementForm, min_num=5, extra=10, validate_min=True
        ),
    }

    def get_initial(self):
        """Return initial values if ``DEBUG`` setting is set to ``True``."""
        if not settings.DEBUG:
            return {}

        return {
            'athlete': {'name': "Domen Blenkuš", 'age': "28", 'weight': 79.5},
            'measurements': [
                {'power': 80, 'heart_rate': 125, 'lactate': 2.4},
                {'power': 120, 'heart_rate': 135, 'lactate': 2.5},
                {'power': 160, 'heart_rate': 147, 'lactate': 1.6},
                {'power': 200, 'heart_rate': 160, 'lactate': 2.2},
                {'power': 240, 'heart_rate': 177, 'lactate': 4.1},
                {'power': 280, 'heart_rate': 195, 'lactate': 12.4},
            ],
        }

    def _save_data(self, forms):
        """Save data."""
        with transaction.atomic():
            athlete = forms['athlete'].save(contributor=self.request.user)

            analyses = LactateThresholdAnalyses.objects.create(
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
                'type': LACTATE_REPORT_TYPE,
                'analysis_pk': analysis.pk,
                'notify_channel': GROUP_SESSIONS.format(websocket_id=session_id),
            },
        )

        return super().forms_valid(forms)
