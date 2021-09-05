"""Conconi test."""
import numpy as np

from .base import BaseAnalysis


class CriticalPowerAnalyses(BaseAnalysis):

    name = 'critical_power'
    template = 'critical_power.tex'

    def _calculate_cp_context(self, time, power):
        inv_time = list(map(lambda t: 1 / t, time))

        power_poly = np.poly1d(np.polyfit(inv_time, power, 1))

        inverse_power_poly = np.poly1d(np.polyfit(power, inv_time, 1))

        work = np.multiply(time, power)
        work_poly = np.poly1d(np.polyfit(time, work, 1))

        return {
            'power': power_poly(0),
            'power_poly': power_poly,
            'inverse_power': inverse_power_poly.roots[0],
            'inverse_power_poly': inverse_power_poly,
            'work': work_poly(0),
        }

    def _calculate_zones(self, power, work):
        poly = lambda time: power + (work / time)
        return {
            '1': power * 0.45,
            '2': power * 0.7,
            '2a': power * 0.77,
            '3': power * 0.95,
            '4': poly(45 * 60),
            '5': poly(10 * 60),
            '6': poly(3 * 60),
        }

    def render_context(self, inputs):
        """Render the context."""
        for attr in ['time', 'power']:
            if attr not in inputs:
                raise ValueError("Missing input '{}'.".format(attr))

        critical_power = self._calculate_cp_context(inputs['time'], inputs['power'])

        return {
            'inputs': inputs,
            'cp': critical_power,
            'zones': self._calculate_zones(
                critical_power['power'],
                critical_power['work'],
            ),
        }

    def get_results(self, context):
        """Return the result of the analysis."""
        return {'result': context['cp']['power']}
