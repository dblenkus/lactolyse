"""Lactolyse download views."""
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from lactolyse.models import LactateThresholdAnalyses
from lactolyse.utils import deserialize_model_instance


class ReportDownloadView(View):
    """Download view."""

    def get(self, request, ref):
        """Serve the file specified in Django's session."""
        analysis = deserialize_model_instance(ref)

        if analysis.contributor != request.user and not request.user.is_superuser:
            return HttpResponseBadRequest()

        file_path = os.path.join(settings.MEDIA_ROOT, analysis.report.name)

        with open(file_path, 'rb') as fn:
            response = HttpResponse(fn.read())

        response['Content-Type'] = 'application/pdf'
        response['Content-Length'] = os.path.getsize(file_path)
        response['Content-Disposition'] = 'attachment; filename="Report.pdf"'

        return response
