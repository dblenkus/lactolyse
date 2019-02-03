"""Views for Lactate Threshold Analysis."""
import os

from asgiref.sync import async_to_sync

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import formset_factory
from django.urls import reverse_lazy

from channels.layers import get_channel_layer

from lactolyse.forms import AthleteForm, ConconiMeasurementForm
from lactolyse.models import ConconiTestAnalyses
from lactolyse.protocol import CONCONI_REPORT_TYPE, GROUP_SESSIONS, RUN_ANALYSIS_CHANNEL

from .base import MultiFormView


class ConconiTestView(LoginRequiredMixin, MultiFormView):
    """Conconi Test view."""

    template_name = os.path.join('lactolyse', 'conconi_test.html')
    analyses_name = 'conconi_test'
    success_url = reverse_lazy('analyses_success')

    form_classes = {
        'athlete': AthleteForm,
        'measurements': formset_factory(
            ConconiMeasurementForm, min_num=7, extra=20, validate_min=True
        ),
    }

    def get_initial(self):
        """Return initial values if ``DEBUG`` setting is set to ``True``."""
        if not settings.DEBUG:
            return {}

        return {
            'athlete': {'name': "Domen Blenkuš", 'age': "28", 'weight': 74.5},
            'measurements': [
                {'power': 120, 'heart_rate': 128},
                {'power': 140, 'heart_rate': 135},
                {'power': 160, 'heart_rate': 145},
                {'power': 180, 'heart_rate': 143},
                {'power': 200, 'heart_rate': 147},
                {'power': 220, 'heart_rate': 157},
                {'power': 240, 'heart_rate': 159},
                {'power': 260, 'heart_rate': 163},
                {'power': 280, 'heart_rate': 167},
                {'power': 300, 'heart_rate': 170},
                {'power': 320, 'heart_rate': 172},
                {'power': 340, 'heart_rate': 175},
                {'power': 360, 'heart_rate': 177},
                {'power': 380, 'heart_rate': 180},
            ],
        }

    def _save_data(self, forms):
        """Save data."""
        with transaction.atomic():
            athlete = forms['athlete'].save(contributor=self.request.user)

            analyses = ConconiTestAnalyses.objects.create(
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
                'type': CONCONI_REPORT_TYPE,
                'analysis_pk': analysis.pk,
                'notify_channel': GROUP_SESSIONS.format(websocket_id=session_id),
            },
        )

        return super().forms_valid(forms)
