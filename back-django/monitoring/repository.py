"""Consultas ao banco. As views não acessam os models diretamente."""
from django.db.models import Max

from .models import Observation, Station
from .utils import to_iso_utc


def list_stations():
    stations = (
        Station.objects.filter(active=True)
        .annotate(updated_at=Max('observations__observed_at'))
        .order_by('name')
    )
    return [
        {
            'id': s.id,
            'name': s.name,
            'river': s.river,
            'municipality': s.municipality,
            'updated_at': to_iso_utc(s.updated_at),
        }
        for s in stations
    ]


def _latest(station, metric):
    return (
        Observation.objects.filter(station=station, metric=metric)
        .order_by('-observed_at')
        .first()
    )


def get_summary(station_id):
    station = Station.objects.filter(id=station_id, active=True).first()
    if station is None:
        return None

    level = _latest(station, 'level')
    rain = _latest(station, 'rain')
    return {
        'station': {
            'id': station.id,
            'name': station.name,
            'river': station.river,
            'municipality': station.municipality,
        },
        'latest': {
            'level_observed_at': to_iso_utc(level.observed_at) if level else None,
            'level_m': level.value if level else None,
            'rain_observed_at': to_iso_utc(rain.observed_at) if rain else None,
            'rain_mm_h': rain.value if rain else None,
        },
    }


def get_series(station_id, metric, start, end):
    rows = (
        Observation.objects.filter(
            station_id=station_id,
            metric=metric,
            observed_at__gte=start,
            observed_at__lte=end,
        )
        .order_by('observed_at')
        .values('observed_at', 'value')
    )
    return [{'timestamp': to_iso_utc(r['observed_at']), 'value': r['value']} for r in rows]


def station_exists(station_id):
    return Station.objects.filter(id=station_id, active=True).exists()