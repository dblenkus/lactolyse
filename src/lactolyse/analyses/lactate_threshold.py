"""Lactate threshold analysis."""
import logging

import numpy as np

from .base import BaseAnalysis
from .utils import FittedPolynomial

logger = logging.getLogger(__name__)


class LactateThresholdAnalyses(BaseAnalysis):
    """Lactate threshold analysis."""

    name = 'lactate_threshold'
    template = 'lactate_treshold.tex'

    def _calculate_dmax_context(self, inputs, lac_poly, hr_poly):
        """Calculate context for d-max method."""
        # If polynomial has a local minimum on the interval (of
        # measurments), take it as a minimum value.
        if lac_poly.deriv_roots.size:
            # If there are two roots, we know (based on the shape of the
            # polynomial) that first one is maximum and second one is
            # minimum.
            min_x = max(lac_poly.deriv_roots)

        # If the minimum is not on the interval (or it doesn't exist),
        # we check for the inflection point and take it if it exists.
        elif lac_poly.deriv_roots.size:
            # Second derivation of third degree polynomial have exactly
            # one root (the question is only if it is on the interval).
            min_x = lac_poly.second_deriv_roots[0]

        # If both conditions are false, we can just take the start of
        # the interval, as we know that it is the "most flat" part of
        # the polynomial on the interval.
        else:
            min_x = lac_poly.min_x

        max_x = lac_poly.max_x

        # Find the point where polynomial starts to raise - threshold is
        # 0.3 - and take only real roots (hopefully there is only one).
        roots = np.roots(lac_poly.poly - (lac_poly.poly(min_x) + 0.3))
        roots = roots[np.logical_and(np.isreal(roots), roots > min_x, roots < max_x)]
        start_x = max(roots).real

        # Calculate the vector cross product.
        v_x = np.poly1d(max_x - start_x)
        v_y = np.poly1d(lac_poly.poly(max_x) - lac_poly.poly(start_x))
        u_x = np.poly1d([1, -start_x])
        u_y = lac_poly.poly - lac_poly.poly(start_x)
        cross_z = v_x * u_y - v_y * u_x

        ftp = np.roots(cross_z.deriv())
        ftp = ftp[np.logical_and(ftp > start_x, ftp < max_x)]
        ftp = ftp[0]

        return {
            'power': ftp,
            'start_point': [start_x, lac_poly.poly(start_x)],
            'end_point': [max_x, lac_poly.poly(max_x)],
            'start_hr': hr_poly.poly(start_x),
            'heart_rate': hr_poly.poly(ftp),
            'lactate': lac_poly.poly(ftp),
        }

    def _calculate_cross_context(self, inputs, lac_poly, hr_poly):
        """Calculate context for cross method."""
        if lac_poly.deriv_roots.size:
            start_point = min(lac_poly.deriv_roots)

        else:
            start_point = inputs['power'][0]

        max_x = lac_poly.max_x

        start_line = np.poly1d(
            np.polyfit(
                [start_point, start_point + 5],
                [lac_poly.poly(start_point), lac_poly.poly(start_point + 5)],
                1,
            )
        )
        end_line = np.poly1d(
            np.polyfit(
                [max_x - 5, max_x], [lac_poly.poly(max_x - 5), lac_poly.poly(max_x)], 1
            )
        )

        cross = np.roots(start_line - end_line)
        power = cross[0]

        return {
            'power': power,
            'start_point': [start_point, lac_poly.poly(start_point)],
            'end_point': [inputs['power'][-1], lac_poly.poly(inputs['power'][-1])],
            'cross': [power, start_line(power)],
            'heart_rate': hr_poly.poly(power),
            'lactate': lac_poly.poly(power),
        }

    def _calculate_at_context(self, inputs, threshold, lac_poly, hr_poly):
        """Calculate context for at method."""
        roots = np.roots(lac_poly.poly - threshold)
        roots = roots[np.isreal(roots)]
        roots = filter(
            lambda val: inputs['power'][0] < val < inputs['power'][-1], roots
        )

        power = list(roots)[0].real

        return {
            'power': power,
            'heart_rate': hr_poly.poly(power),
            'lactate': lac_poly.poly(power),
        }

    def render_context(self, inputs):
        """Render the context."""
        for attr in ['power', 'heart_rate', 'lactate']:
            if attr not in inputs:
                raise ValueError("Missing input '{}'.".format(attr))

        lac_poly = FittedPolynomial(inputs['power'], inputs['lactate'])
        hr_poly = FittedPolynomial(inputs['power'], inputs['heart_rate'])

        return {
            'inputs': inputs,
            'lac_poly': lac_poly,
            'dmax': self._calculate_dmax_context(inputs, lac_poly, hr_poly),
            'cross': self._calculate_cross_context(inputs, lac_poly, hr_poly),
            'at2': self._calculate_at_context(inputs, 2, lac_poly, hr_poly),
            'at4': self._calculate_at_context(inputs, 4, lac_poly, hr_poly),
        }

    def get_results(self, context):
        """Return the result of the analysis."""
        return {
            'dmax': context['dmax']['power'],
            'cross': context['cross']['power'],
            'at2': context['at2']['power'],
            'at4': context['at4']['power'],
        }
