"""Lactolyse models."""

import hashlib
import os

from django.conf import settings
from django.db import models


def _generate_report_name(instance, filename, prefix):
    """Generate unique filename with given prefix."""
    sha256 = hashlib.sha256()
    for chunk in instance.report.chunks():
        sha256.update(chunk)

    extension = os.path.splitext(filename)[1]

    return os.path.join(prefix, sha256.hexdigest() + extension)


def generate_lactate_threshold_name(instance, filename):
    """Generate an unique filename for report based on it's hash."""
    prefix = os.path.join('reports', 'lactate_threshold')
    return _generate_report_name(instance, filename, prefix)


def generate_conconi_test_name(instance, filename):
    """Generate an unique filename for report based on it's hash."""
    prefix = os.path.join('reports', 'conconi_test')
    return _generate_report_name(instance, filename, prefix)


class Athlete(models.Model):
    """Athlete model."""

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    name = models.CharField(max_length=100)

    age = models.IntegerField()

    weight = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        """Format model name."""
        return "name: {}, age: {}".format(self.name, self.age)


class LactateThresholdAnalyses(models.Model):
    """Lactate Threshold Analyses model."""

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)

    created = models.DateField(auto_now_add=True)

    report = models.FileField(upload_to=generate_lactate_threshold_name)

    result_dmax = models.IntegerField(null=True)

    result_cross = models.IntegerField(null=True)

    result_at2 = models.IntegerField(null=True)

    result_at4 = models.IntegerField(null=True)

    def __str__(self):
        """Format model name."""
        return "athlete: {}, date: {}".format(self.athlete.name, self.created)


class LactateMeasurement(models.Model):
    """Lactate Measurement model."""

    analyses = models.ForeignKey(LactateThresholdAnalyses, on_delete=models.CASCADE)

    power = models.IntegerField()

    heart_rate = models.IntegerField()

    lactate = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        """Format model name."""
        return "name: {}, power: {}, heart rate: {}, lactate: {}".format(
            self.analyses.athlete.name, self.power, self.heart_rate, self.lactate
        )


class LactateThresholdRunAnalyses(models.Model):
    """Lactate Threshold Analyses for runners model."""

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)

    created = models.DateField(auto_now_add=True)

    report = models.FileField(upload_to=generate_lactate_threshold_name)

    result_dmax = models.IntegerField(null=True)

    result_cross = models.IntegerField(null=True)

    result_at2 = models.IntegerField(null=True)

    result_at4 = models.IntegerField(null=True)

    def __str__(self):
        """Format model name."""
        return "athlete: {}, date: {}".format(self.athlete.name, self.created)


class LactateRunMeasurement(models.Model):
    """Lactate Measurement model."""

    analyses = models.ForeignKey(LactateThresholdRunAnalyses, on_delete=models.CASCADE)

    pace = models.IntegerField()

    heart_rate = models.IntegerField()

    lactate = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        """Format model name."""
        return "name: {}, pace: {}, heart rate: {}, lactate: {}".format(
            self.analyses.athlete.name, self.pace, self.heart_rate, self.lactate
        )


class CriticalPowerAnalyses(models.Model):
    """Lactate Threshold Analyses for runners model."""

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)

    created = models.DateField(auto_now_add=True)

    report = models.FileField(upload_to=generate_lactate_threshold_name)

    result = models.IntegerField(null=True)

    def __str__(self):
        """Format model name."""
        return "athlete: {}, date: {}".format(self.athlete.name, self.created)


class CriticalPowerMeasurement(models.Model):
    """Lactate Measurement model."""

    analyses = models.ForeignKey(CriticalPowerAnalyses, on_delete=models.CASCADE)

    time = models.IntegerField()

    power = models.IntegerField()

    def __str__(self):
        """Format model name."""
        return "name: {}, time: {}, power: {}".format(
            self.analyses.athlete.name, self.time, self.power
        )


class ConconiTestAnalyses(models.Model):
    """Lactate Threshold Analyses model."""

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)

    created = models.DateField(auto_now_add=True)

    report = models.FileField(upload_to=generate_conconi_test_name)

    result = models.IntegerField(null=True)

    def __str__(self):
        """Format model name."""
        return "athlete: {}, date: {}".format(self.athlete.name, self.created)


class ConconiMeasurement(models.Model):
    """Lactate Measurement model."""

    analyses = models.ForeignKey(ConconiTestAnalyses, on_delete=models.CASCADE)

    power = models.IntegerField()

    heart_rate = models.IntegerField()

    def __str__(self):
        """Format model name."""
        return "name: {}, power: {}, heart rate: {}".format(
            self.analyses.athlete.name, self.power, self.heart_rate
        )
