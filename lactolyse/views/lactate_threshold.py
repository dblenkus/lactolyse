import os
import tempfile

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import File
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponse
from django.urls import reverse_lazy

from lactolyse.executors import executor
from lactolyse.forms import AthleteForm, LactateMeasurementForm
from lactolyse.models import LactateThresholdAnalyses

from .base import MultiFormView


class LactateThresholdView(LoginRequiredMixin, MultiFormView):
    template_name = os.path.join('lactolyse', 'lactate_threshold.html')
    analyses_name = 'lactate_threshold'
    success_url = reverse_lazy('analyses_success')

    form_classes = {
        'athlete': AthleteForm,
        'measurements': formset_factory(
            LactateMeasurementForm,
            min_num=5,
            extra=4,
            validate_min=True,
        ),
    }

    initial = {
        'athlete': {
            'name': "Domen Blenkuš",
            'age': "28",
            'weight': 79.5,
        },
        'measurements': [
            {
                'power': 80,
                'heart_rate': 125,
                'lactate': 2.4,
            }, {
                'power': 120,
                'heart_rate': 135,
                'lactate': 2.5,
            }, {
                'power': 160,
                'heart_rate': 147,
                'lactate': 1.6,
            }, {
                'power': 200,
                'heart_rate': 160,
                'lactate': 2.2,
            }, {
                'power': 240,
                'heart_rate': 177,
                'lactate': 4.1,
            }, {
                'power': 280,
                'heart_rate': 195,
                'lactate': 12.4,
            }
        ],
    }

    def _save_data(self, forms):
        with transaction.atomic():
            athlete = forms['athlete'].save()

            analyses = LactateThresholdAnalyses.objects.create(  # pylint: disable=no-member
                athlete=athlete
            )

            measurements = []
            for form in forms['measurements']:
                if form.cleaned_data:
                    measurement = form.save(analyses=analyses)
                    measurements.append(measurement)

        return analyses, athlete, measurements

    def _make_report(self, analyses, athlete, measurements):
        inputs = {
            'power': [int(m.power) for m in measurements],
            'heart_rate': [int(m.heart_rate) for m in measurements],
            'lactate': [float(m.lactate) for m in measurements],
            'weight': float(athlete.weight),
        }

        report_dir = tempfile.TemporaryDirectory()
        report_path = os.path.join(report_dir.name, 'report.pdf')

        executor.run(self.analyses_name, report_path, inputs)

        with open(report_path, 'rb') as fn:
            report_file = File(fn)
            analyses.report = report_file
            analyses.save()

    def forms_valid(self, forms):

        analyses, athlete, measurements = self._save_data(forms)
        self._make_report(analyses, athlete, measurements)

        # Set download file for download view.
        self.request.session['download'] = {
            'file_path': analyses.report.name,
            # 'file_name': "Report - {}.pdf".format(athlete.name),
            'file_name': "Report.pdf",
        }

        return super().forms_valid(forms)
