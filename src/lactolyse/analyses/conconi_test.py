"""Conconi test."""
import logging
import math

import numpy as np

from .base import BaseAnalysis
from .utils import fit_polynomial

logger = logging.getLogger(__name__)


class ConcoinAnalyses(BaseAnalysis):

    name = 'conconi_test'
    template = 'conconi_test.tex'

    def _calculate_conconi_context(self, poly, power, heart_rate):
        # FTP value is normally somewhere around 70% of measured values,
        # so we limit the search interval to 60-80% to simplify the
        # prediction.
        lower_limit = power[math.floor(len(power) * 0.6)]
        upper_limit = power[math.ceil(len(power) * 0.8)]

        lower_pwr_range = list(filter(lambda pwr: pwr <= lower_limit, power))
        upper_pwr_range = list(filter(lambda pwr: lower_limit < pwr, power))

        lower_hr_range = heart_rate[: len(lower_pwr_range)]
        upper_hr_range = heart_rate[-len(upper_pwr_range) :]

        min_error = None
        best_lower_line = None
        best_upper_line = None
        while upper_limit > upper_pwr_range[0]:
            lower_line = np.poly1d(np.polyfit(lower_pwr_range, lower_hr_range, 1))
            upper_line = np.poly1d(np.polyfit(upper_pwr_range, upper_hr_range, 1))

            predicted_lower_hr = lower_line(lower_pwr_range)
            predicted_upper_hr = lower_line(upper_pwr_range)

            lower_error = sum(np.square(predicted_lower_hr - lower_hr_range))
            upper_error = sum(np.square(predicted_upper_hr - upper_hr_range))
            error = lower_error + upper_error

            if min_error is None or error < min_error:
                min_error = error
                best_lower_line = lower_line
                best_upper_line = upper_line

            lower_pwr_range.append(upper_pwr_range.pop(0))
            lower_hr_range.append(upper_hr_range.pop(0))

        ftp = np.roots(best_lower_line - best_upper_line)
        ftp = int(ftp[0])

        return {
            'power': ftp,
            'start_point': [power[0], poly.poly(power[0])],
            'end_point': [power[-1], poly.poly(power[-1])],
            'cross': [ftp, best_lower_line(ftp)],
            'heart_rate': poly.poly(ftp),
        }

    def render_context(self, inputs):
        """Render the context."""
        for attr in ['power', 'heart_rate']:
            if attr not in inputs:
                raise ValueError("Missing input '{}'.".format(attr))

        poly, new_pwr, new_hr = fit_polynomial(
            inputs['power'],
            inputs['heart_rate'],
            exclude_outliers=1,
            return_inputs=True,
        )

        return {
            'inputs': inputs,
            'hr_poly': poly,
            'conconi': self._calculate_conconi_context(poly, new_pwr, new_hr),
        }

    def get_results(self, context):
        """Return the result of the analysis."""
        return {'result': context['conconi']['power']}
