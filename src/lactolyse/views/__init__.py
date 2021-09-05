"""Lactolyse views."""
import os

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .conconi_test import ConconiTestView
from .critical_power import CriticalPowerTestView
from .download import ReportDownloadView
from .lactate_threshold import LactateThresholdView
from .lactate_threshold_run import LactateThresholdRunView

select_analyses_view = login_required(
    TemplateView.as_view(
        template_name=os.path.join('lactolyse', 'select_analyses.html')
    )
)
analyses_success_view = login_required(
    TemplateView.as_view(
        template_name=os.path.join('lactolyse', 'analyses_success.html')
    )
)
lactate_threshold_view = LactateThresholdView.as_view()
lactate_threshold_run_view = LactateThresholdRunView.as_view()
critical_power_test_view = CriticalPowerTestView.as_view()
conconi_test_view = ConconiTestView.as_view()
report_download_view = ReportDownloadView.as_view()
