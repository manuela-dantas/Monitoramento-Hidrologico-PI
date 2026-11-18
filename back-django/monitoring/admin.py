from django.contrib import admin

from .models import Observation, Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'river', 'municipality', 'active']
    list_filter = ['active']
    search_fields = ['id', 'name', 'river', 'municipality']


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ['station', 'metric', 'observed_at', 'value', 'unit', 'source']
    list_filter = ['station', 'metric']
    date_hierarchy = 'observed_at'
    ordering = ['-observed_at']