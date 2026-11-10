import math
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from monitoring.models import Observation, Station
from monitoring.utils import current_hour_utc

STATIONS = [
    {'id': 'EST-01', 'name': 'Estação Aurora', 'river': 'Rio Aurora', 'municipality': 'Vila Aurora'},
    {'id': 'EST-02', 'name': 'Estação Vale Verde', 'river': 'Rio Verde', 'municipality': 'Vale Verde'},
    {'id': 'EST-03', 'name': 'Estação Campo Alto', 'river': 'Rio do Campo', 'municipality': 'Campo Alto'},
]


class Command(BaseCommand):
    help = 'Carrega estações e observações sintéticas (pode ser executado várias vezes).'

    @transaction.atomic
    def handle(self, *args, **options):
        for data in STATIONS:
            Station.objects.get_or_create(id=data['id'], defaults=data)

        end_hour = current_hour_utc()
        observations = []
        for index in range(73):
            observed_at = end_hour - timedelta(hours=72 - index)
            for station_index, data in enumerate(STATIONS):
                level = 1.05 + station_index * 0.24 + 0.08 * math.sin(index / 5 + station_index)
                if (index + station_index * 7) % 17 < 3:
                    rain = 0.4 + ((index + station_index) % 4) * 0.35
                else:
                    rain = 0
                observations.append(Observation(
                    station_id=data['id'], metric='level', observed_at=observed_at,
                    value=round(level, 2), unit='m',
                ))
                observations.append(Observation(
                    station_id=data['id'], metric='rain', observed_at=observed_at,
                    value=round(rain, 2), unit='mm/h',
                ))

        # ignore_conflicts=True vira INSERT OR IGNORE: a UNIQUE impede duplicatas.
        Observation.objects.bulk_create(observations, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'Amostra simulada pronta ({Station.objects.count()} estações, '
            f'{Observation.objects.count()} observações).'
        ))