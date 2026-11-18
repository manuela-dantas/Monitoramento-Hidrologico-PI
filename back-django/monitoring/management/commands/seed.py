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

def is_gap(index, station_index, metric):
    """Regras fixas de lacunas, para que o resultado seja sempre o mesmo.

    - Todas as estações: sensor desligado cerca de 1 vez a cada 10 horas.
    - EST-02: pluviômetro parado nas 2 últimas horas (o nível continua).
    """
    if (index + station_index * 3) % 10 == 7:
        return True
    return metric == 'rain' and station_index == 1 and index >= 71

class Command(BaseCommand):
    help = 'Carrega estações e observações sintéticas (pode ser executado várias vezes).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--com-lacunas', action='store_true',
            help='Pula alguns horários para simular falhas de sensor.',
        )
        parser.add_argument(
            '--limpar', action='store_true',
            help='Apaga todas as observações antes de carregar.',
        )
    @transaction.atomic
    def handle(self, *args, **options):
        if options['limpar']:
            apagadas, _ = Observation.objects.all().delete()
            self.stdout.write(f'{apagadas} observações apagadas.')

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
                values = [('level', round(level, 2), 'm'), ('rain', round(rain, 2), 'mm/h')]
                for metric, value, unit in values:
                    if options['com_lacunas'] and is_gap(index, station_index, metric):
                        continue
                    observations.append(Observation(
                        station_id=data['id'], metric=metric, observed_at=observed_at,
                        value=value, unit=unit,
                    ))

        # ignore_conflicts=True vira INSERT OR IGNORE: a UNIQUE impede duplicatas.
        Observation.objects.bulk_create(observations, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'Amostra simulada pronta ({Station.objects.count()} estações, '
            f'{Observation.objects.count()} observações).'
        ))