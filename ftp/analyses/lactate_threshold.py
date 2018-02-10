from .base import BaseAnalysis

class LactateThresholdAnalyses(BaseAnalysis):

    name = 'lactate_threshold'
    template = 'lactate_treshold.tex'

    def calculate_context(self, inputs):
        return {
            'section1': "First section",
            'section2': "Second section",
        }
