from django.db import connection
from django.views.decorators.http import require_GET

from . import repository
from .utils import UNITS, error_response, json_response, to_iso_utc, window

SIMULATION_MESSAGE = 'Amostra simulada. Não representa condições reais.'


@require_GET
def health(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return json_response({'status': 'ok', 'database': 'ok'})


@require_GET
def stations(request):
    return json_response({
        'data_mode': 'simulation',
        'stations': repository.list_stations(),
    })


@require_GET
def station_summary(request, station_id):
    result = repository.get_summary(station_id)
    if result is None:
        return error_response(404, 'station_not_found', 'Estação não encontrada.')
    return json_response({
        'data_mode': 'simulation',
        'message': SIMULATION_MESSAGE,
        'station': result['station'],
        'latest': result['latest'],
    })


@require_GET
def station_series(request, station_id):
    metric = request.GET.get('metric') or 'level'
    hours_text = request.GET.get('hours') or '24'

    if metric not in UNITS:
        return error_response(400, 'invalid_metric', 'metric deve ser level ou rain.')
    try:
        hours = int(hours_text)
    except ValueError:
        hours = 0
    if not 1 <= hours <= 72:
        return error_response(400, 'invalid_hours', 'hours deve ser um inteiro entre 1 e 72.')

    if not repository.station_exists(station_id):
        return error_response(404, 'station_not_found', 'Estação não encontrada.')

    start, end = window(hours)
    return json_response({
        'data_mode': 'simulation',
        'station_id': station_id,
        'metric': metric,
        'unit': UNITS[metric],
        'interval_minutes': 60,
        'from': to_iso_utc(start),
        'to': to_iso_utc(end),
        'points': repository.get_series(station_id, metric, start, end),
    })


def not_found(request, unknown_path=None):
    return error_response(404, 'not_found', 'Rota não encontrada.')