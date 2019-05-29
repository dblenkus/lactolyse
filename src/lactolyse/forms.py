"""Lactolyse forms."""
from django import forms

from material import Layout, Row

from .models import (
    Athlete,
    ConconiMeasurement,
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

    layout = Layout(Row('pace', 'heart_rate', 'lactate'))

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
