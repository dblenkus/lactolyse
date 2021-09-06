"""Lactolyse forms."""
import re

from django import forms

from material import Layout, Row

from .models import (
    Athlete,
    ConconiMeasurement,
    CriticalPowerMeasurement,
    LactateMeasurement,
    LactateRunMeasurement,
)


class AthleteForm(forms.ModelForm):
    """Form for Athlete model."""

    class Meta:
        """AthleteForm Meta options."""

        model = Athlete
        fields = ['name', 'age', 'weight']

    def save(self, contributor, commit=True):
        """Asign the contributor and save the instance."""
        self.instance.contributor = contributor

        return super().save(commit=commit)


class LactateMeasurementForm(forms.ModelForm):
    """Form for LactateMeasurement model."""

    class Meta:
        """LactateMeasurementForm Meta options."""

        model = LactateMeasurement
        fields = ['power', 'heart_rate', 'lactate']

    layout = Layout(Row('power', 'heart_rate', 'lactate'))

    def save(self, analyses, commit=True):
        """Asign the measurement to the analysis and save it."""
        self.instance.analyses = analyses

        return super().save(commit=commit)


class LactateRunMeasurementForm(forms.ModelForm):
    """Form for LactateRunMeasurement model."""

    class Meta:
        """LactateRunMeasurementForm Meta options."""

        model = LactateRunMeasurement
        fields = ['pace', 'heart_rate', 'lactate']

    pace = forms.CharField()
    layout = Layout(Row('pace', 'heart_rate', 'lactate'))

    def clean_pace(self):
        data = self.cleaned_data['pace']
        data = list(map(int, re.split(r":|\.", data)))

        return data[0] if len(data) == 1 else data[0] * 60 + data[1]

    def save(self, analyses, commit=True):
        """Asign the measurement to the analysis and save it."""
        self.instance.analyses = analyses

        return super().save(commit=commit)


class CriticalPowerMeasurementForm(forms.ModelForm):
    """Form for CriticalPowerMeasurement model."""

    class Meta:
        """CriticalPowerForm Meta options."""

        model = CriticalPowerMeasurement
        fields = ['time', 'power']

    layout = Layout(Row('time', 'power'))

    def save(self, analyses, commit=True):
        """Asign the measurement to the analysis and save it."""
        self.instance.analyses = analyses

        return super().save(commit=commit)


class ConconiMeasurementForm(forms.ModelForm):
    """Form for ConconiMeasurement model."""

    class Meta:
        """ConconiMeasurementForm Meta options."""

        model = ConconiMeasurement
        fields = ['power', 'heart_rate']

    layout = Layout(Row('power', 'heart_rate'))

    def save(self, analyses, commit=True):
        """Asign the measurement to the analysis and save it."""
        self.instance.analyses = analyses

        return super().save(commit=commit)
