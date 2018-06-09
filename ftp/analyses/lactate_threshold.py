import logging

import numpy as np

from .base import BaseAnalysis

logger = logging.getLogger(__name__)


class LactateThresholdAnalyses(BaseAnalysis):

    name = 'lactate_threshold'
    template = 'lactate_treshold.tex'

    def _calculate_dmax_context(self, inputs, lac_poly, hr_poly):

        def perpendicular(vector):
            return np.array(-vector[1], vector[0])

        # Determine where polynomial is the "most horizontal", i.e. root
        # of second derivative.

        min_x = np.roots(lac_poly.deriv())
        min_x = filter(lambda val: inputs['power'][0] < val < inputs['power'][-1], min_x)
        min_x = list(min_x)[0]

        # Find the point where polynomial starts to raise - threshold is
        # 0.5 - and take only real roots (hopefully there is only one).
        roots = np.roots(lac_poly - (lac_poly(min_x) + 0.5))
        roots = roots[np.isreal(roots)]
        roots = filter(lambda val: min_x < val < inputs['power'][-1], roots)
        roots = list(roots)

        # if len(roots) != 1:
        #     msg = "Something strange happened, there is more than one root."
        #     logger.error(msg)
        #     raise

        # Take the (real) root and calculate the y value.
        start_point = [roots[0].real, lac_poly(roots[0].real)]

        # Calculate the vector cross product.
        v_x = np.poly1d(inputs['power'][-1] - start_point[0])
        v_y = np.poly1d(lac_poly(inputs['power'][-1]) - start_point[1])
        u_x = np.poly1d([1, -start_point[0]])
        u_y = lac_poly - np.poly1d(start_point[1])
        cross_z = v_x * u_y - v_y * u_x

        ftp = np.roots(cross_z.deriv())
        ftp = filter(lambda val: start_point[0] < val < inputs['power'][-1], ftp)
        ftp = list(ftp)[0]

        line_poly = np.poly1d(np.polyfit(
            [start_point[0], inputs['power'][-1]],
            [start_point[1], inputs['lactate'][-1]],
            1
        ))

        perp_poly = perpendicular(line_poly)

        return {
            'power': ftp,
            'start_point': start_point,
            'end_point': [inputs['power'][-1], lac_poly(inputs['power'][-1])],
            'start_hr': hr_poly(start_point[0]),
            'heart_rate': hr_poly(ftp),
            'lactate': lac_poly(ftp),
        }

    def _calculate_cross_context(self, inputs, lac_poly, hr_poly):
        start_line = np.poly1d(
            np.polyfit(
                [inputs['power'][0], inputs['power'][0] + 5],
                [lac_poly(inputs['power'][0] ), lac_poly(inputs['power'][0] + 5)],
                1
            )
        )
        end_line = np.poly1d(
            np.polyfit(
                [inputs['power'][-1] - 5, inputs['power'][-1]],
                [lac_poly(inputs['power'][-1] - 5), lac_poly(inputs['power'][-1])],
                1
            )
        )

        cross = np.roots(start_line - end_line)
        power = cross[0]

        return {
            'power': power,
            'start_point': [inputs['power'][0], lac_poly(inputs['power'][0])],
            'end_point': [inputs['power'][-1], lac_poly(inputs['power'][-1])],
            'cross': [power, start_line(power)],
            'heart_rate': hr_poly(power),
            'lactate': lac_poly(power),
        }

    def _calculate_ftp_context(self, dmax, cross):
        return {
            'power': (dmax['power'] + cross['power']) / 2,
            'heart_rate': (dmax['heart_rate'] + cross['heart_rate']) / 2,
            'lactate': (dmax['lactate'] + cross['lactate']) / 2,
        }

    def _calculate_at_context(self, inputs, threshold, lac_poly, hr_poly):
        roots = np.roots(lac_poly - threshold)
        roots = roots[np.isreal(roots)]
        roots = filter(lambda val: inputs['power'][0] < val < inputs['power'][-1], roots)

        power = list(roots)[0].real

        return {
            'power': power,
            'heart_rate': hr_poly(power),
            'lactate': lac_poly(power),
        }

    def render_context(self, inputs):
        for attr in ['power', 'heart_rate', 'lactate']:
            if attr not in inputs:
                raise ValueError("Missing input '{}'.".format(attr))

        lac_poly = np.poly1d(np.polyfit(inputs['power'], inputs['lactate'], 3))
        hr_poly = np.poly1d(np.polyfit(inputs['power'], inputs['heart_rate'], 3))

        dmax_context = self._calculate_dmax_context(inputs, lac_poly, hr_poly)
        cross_context = self._calculate_cross_context(inputs, lac_poly, hr_poly)

        return {
            'inputs': inputs,
            'lac_poly': lac_poly,
            'dmax': dmax_context,
            'cross': cross_context,
            'ftp': self._calculate_ftp_context(dmax_context, cross_context),
            'at2': self._calculate_at_context(inputs, 2, lac_poly, hr_poly),
            'at4': self._calculate_at_context(inputs, 4, lac_poly, hr_poly),
        }
