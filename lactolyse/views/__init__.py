"""Lactolyse views."""
import os

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .download import LactateThresholdAnalysesDownloadView
from .lactate_threshold import LactateThresholdView

# pylint: disable=invalid-name
select_analyses_view = login_required(
    TemplateView.as_view(template_name=os.path.join('lactolyse', 'select_analyses.html'))
)
analyses_success_view = login_required(
    TemplateView.as_view(template_name=os.path.join('lactolyse', 'analyses_success.html'))
)
lactate_threshold_view = LactateThresholdView.as_view()
lactate_threshold_download_view = LactateThresholdAnalysesDownloadView.as_view()
# pylint: enable=invalid-name
