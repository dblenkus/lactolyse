"""Lactolyse Django admin."""
from django.contrib import admin

from lactolyse.models import LactateThresholdAnalyses


class LactateThresholdAnalysesAdmin(admin.ModelAdmin):
    """Initial group configuration."""

    model = LactateThresholdAnalyses

    list_display = (
        'get_athlete',
        'created',
        'result_dmax',
        'result_cross',
        'result_at4',
        'result_at2',
    )

    def get_athlete(self, obj):
        """Return athlete's name."""
        return obj.athlete.name

    get_athlete.short_description = 'Athlete'
    get_athlete.admin_order_field = 'athlete__name'


admin.site.register(LactateThresholdAnalyses, LactateThresholdAnalysesAdmin)
