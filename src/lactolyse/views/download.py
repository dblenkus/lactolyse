"""Lactolyse download views."""
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views import View

from lactolyse.models import LactateThresholdAnalyses


class DownloadFileView(View):
    """Download view."""

    analysis_model = None

    def get(self, request, pk):
        """Serve the file specified in Django's session."""
        analysis = get_object_or_404(self.analysis_model, pk=pk)

        if analysis.contributor != request.user and not request.user.is_superuser:
            return HttpResponseBadRequest()

        file_path = os.path.join(settings.MEDIA_ROOT, analysis.report.name)

        with open(file_path, 'rb') as fn:
            response = HttpResponse(fn.read())

        response['Content-Type'] = 'application/pdf'
        response['Content-Length'] = os.path.getsize(file_path)
        response['Content-Disposition'] = 'attachment; filename="Report.pdf"'

        return response


class LactateThresholdAnalysesDownloadView(DownloadFileView):
    """Download view for Lactate Threshold Analysis."""

    analysis_model = LactateThresholdAnalyses
