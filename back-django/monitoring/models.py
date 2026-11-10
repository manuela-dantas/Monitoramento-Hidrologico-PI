from django.db import models


class Station(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=120)
    river = models.CharField(max_length=120)
    municipality = models.CharField(max_length=120)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'stations'
        ordering = ['name']

    def __str__(self):
        return f'{self.id} - {self.name}'


class Observation(models.Model):
    class Metric(models.TextChoices):
        LEVEL = 'level', 'Nível'
        RAIN = 'rain', 'Chuva'

    class Unit(models.TextChoices):
        METERS = 'm', 'metros'
        MM_PER_HOUR = 'mm/h', 'milímetros por hora'

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name='observations'
    )
    metric = models.CharField(max_length=10, choices=Metric.choices)
    observed_at = models.DateTimeField()
    value = models.FloatField()
    unit = models.CharField(max_length=10, choices=Unit.choices)
    source = models.CharField(max_length=20, default='synthetic')

    class Meta:
        db_table = 'observations'
        constraints = [
            models.UniqueConstraint(
                fields=['station', 'metric', 'observed_at'],
                name='uniq_observation_station_metric_time',
            ),
            models.CheckConstraint(
                condition=models.Q(metric__in=['level', 'rain']),
                name='check_observation_metric',
            ),
            models.CheckConstraint(
                condition=models.Q(unit__in=['m', 'mm/h']),
                name='check_observation_unit',
            ),
        ]
        indexes = [
            models.Index(
                fields=['station', 'metric', 'observed_at'],
                name='idx_obs_station_metric_time',
            ),
        ]

    def __str__(self):
        return f'{self.station_id} {self.metric} {self.observed_at:%Y-%m-%d %H:%M} = {self.value}'