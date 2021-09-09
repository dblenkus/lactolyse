"""Django channels consumers."""
import os
import tempfile
from uuid import uuid4

from asgiref.sync import async_to_sync

from django.core.files import File
from django.urls import reverse

from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer

from lactolyse.executors import executor
from lactolyse.models import (
    ConconiTestAnalyses,
    CriticalPowerAnalyses,
    LactateThresholdAnalyses,
    LactateThresholdRunAnalyses,
)
from lactolyse.protocol import GROUP_SESSIONS
from lactolyse.utils import serialize_model_instance


class RunAnalysisConsumer(SyncConsumer):
    """Consumer for running the executor."""

    def lactolyse_lactate_report(self, event):
        """Make report for Lactate Thresold Analysis."""
        analysis = (
            LactateThresholdAnalyses.objects.select_related('athlete')
            .prefetch_related('lactatemeasurement_set')
            .get(pk=event['analysis_pk'])
        )
        measurements = analysis.lactatemeasurement_set.order_by('power').values(
            'power', 'heart_rate', 'lactate'
        )

        inputs = {
            'power': [m['power'] for m in measurements],
            'heart_rate': [m['heart_rate'] for m in measurements],
            'lactate': [float(m['lactate']) for m in measurements],
            'weight': float(analysis.athlete.weight),
        }

        report_dir = tempfile.TemporaryDirectory()
        report_filename = '{}.pdf'.format(uuid4().hex)
        report_path = os.path.join(report_dir.name, report_filename)

        results = executor.run('lactate_threshold', report_path, inputs)

        analysis.result_dmax = results['dmax']
        analysis.result_cross = results['cross']
        analysis.result_at2 = results['at2']
        analysis.result_at4 = results['at4']

        with open(report_path, 'rb') as fn:
            report_file = File(fn)
            analysis.report = report_file

            analysis.save()

        async_to_sync(self.channel_layer.group_send)(
            event['notify_channel'],
            {
                'type': 'websocket_send',
                'download_url': reverse(
                    'download_report',
                    kwargs={'ref': serialize_model_instance(analysis)},
                ),
            },
        )

    def lactolyse_lactate_run_report(self, event):
        """Make report for Lactate Thresold Analysis for runners."""
        analysis = (
            LactateThresholdRunAnalyses.objects.select_related('athlete')
            .prefetch_related('lactaterunmeasurement_set')
            .get(pk=event['analysis_pk'])
        )
        measurements = analysis.lactaterunmeasurement_set.order_by('-pace').values(
            'pace', 'heart_rate', 'lactate'
        )

        inputs = {
            'pace': [m['pace'] for m in measurements],
            'heart_rate': [m['heart_rate'] for m in measurements],
            'lactate': [float(m['lactate']) for m in measurements],
            'weight': float(analysis.athlete.weight),
        }

        report_dir = tempfile.TemporaryDirectory()
        report_filename = '{}.pdf'.format(uuid4().hex)
        report_path = os.path.join(report_dir.name, report_filename)

        results = executor.run('lactate_threshold_run', report_path, inputs)

        analysis.result_dmax = results['dmax']
        analysis.result_cross = results['cross']
        analysis.result_at2 = results['at2']
        analysis.result_at4 = results['at4']

        with open(report_path, 'rb') as fn:
            report_file = File(fn)
            analysis.report = report_file

            analysis.save()

        async_to_sync(self.channel_layer.group_send)(
            event['notify_channel'],
            {
                'type': 'websocket_send',
                'download_url': reverse(
                    'download_report',
                    kwargs={'ref': serialize_model_instance(analysis)},
                ),
            },
        )

    def lactolyse_critical_power_report(self, event):
        """Make report for Conconi Test Analysis."""
        analysis = (
            CriticalPowerAnalyses.objects.select_related('athlete')
            .prefetch_related('criticalpowermeasurement_set')
            .get(pk=event['analysis_pk'])
        )
        measurements = analysis.criticalpowermeasurement_set.order_by('time').values(
            'time', 'power'
        )

        inputs = {
            'time': [m['time'] for m in measurements],
            'power': [m['power'] for m in measurements],
            'weight': float(analysis.athlete.weight),
        }

        report_dir = tempfile.TemporaryDirectory()
        report_filename = '{}.pdf'.format(uuid4().hex)
        report_path = os.path.join(report_dir.name, report_filename)

        results = executor.run('critical_power', report_path, inputs)

        analysis.result = results['result']

        with open(report_path, 'rb') as fn:
            report_file = File(fn)
            analysis.report = report_file

            analysis.save()

        async_to_sync(self.channel_layer.group_send)(
            event['notify_channel'],
            {
                'type': 'websocket_send',
                'download_url': reverse(
                    'download_report',
                    kwargs={'ref': serialize_model_instance(analysis)},
                ),
            },
        )

    def lactolyse_conconi_report(self, event):
        """Make report for Conconi Test Analysis."""
        analysis = (
            ConconiTestAnalyses.objects.select_related('athlete')
            .prefetch_related('conconimeasurement_set')
            .get(pk=event['analysis_pk'])
        )
        measurements = analysis.conconimeasurement_set.order_by('power').values(
            'power', 'heart_rate'
        )

        inputs = {
            'power': [m['power'] for m in measurements],
            'heart_rate': [m['heart_rate'] for m in measurements],
            'weight': float(analysis.athlete.weight),
        }

        report_dir = tempfile.TemporaryDirectory()
        report_filename = '{}.pdf'.format(uuid4().hex)
        report_path = os.path.join(report_dir.name, report_filename)

        results = executor.run('conconi_test', report_path, inputs)

        analysis.result = results['result']

        with open(report_path, 'rb') as fn:
            report_file = File(fn)
            analysis.report = report_file

            analysis.save()

        async_to_sync(self.channel_layer.group_send)(
            event['notify_channel'],
            {
                'type': 'websocket_send',
                'download_url': reverse(
                    'download_report',
                    kwargs={'ref': serialize_model_instance(analysis)},
                ),
            },
        )


class ClientConsumer(JsonWebsocketConsumer):
    """Client websocket consumer."""

    def __init__(self, *args, **kwargs):
        """Initialize client consumer."""
        self.websocket_id = None
        super().__init__(*args, **kwargs)

    def websocket_connect(self, event):
        """Establish websocket."""
        self.websocket_id = self.scope['session'].session_key
        super().websocket_connect(event)

    @property
    def groups(self):
        """Return groups this channel should add itself to."""
        if self.websocket_id is None:
            return []

        return [GROUP_SESSIONS.format(websocket_id=self.websocket_id)]

    def websocket_send(self, event):
        """Send message over websocket."""
        # Strip internal logic.
        event.pop('type')

        self.send_json(event)
