from django import forms

from material import Layout, Row

from .models import Athlete, LactateMeasurement


class AthleteForm(forms.ModelForm):

    class Meta:
        model = Athlete
        fields = ['name', 'age', 'weight']


class LactateMeasurementForm(forms.ModelForm):

    class Meta:
        model = LactateMeasurement
        fields = ['power', 'heart_rate', 'lactate']

    layout = Layout(
        Row('power', 'heart_rate', 'lactate')
    )

    def save(self, analyses, commit=True):

        self.instance.analyses = analyses

        return super().save(commit=commit)
