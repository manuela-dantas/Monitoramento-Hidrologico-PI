from datetime import timedelta, timezone

from django.http import JsonResponse
from django.utils import timezone as dj_timezone

UNITS = {'level': 'm', 'rain': 'mm/h'}


def to_iso_utc(value):
    """Converte datetime em texto ISO 8601 UTC terminado em Z (ou None)."""
    if value is None:
        return None
    return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def current_hour_utc():
    """Agora em UTC, com minutos e segundos zerados."""
    return dj_timezone.now().replace(minute=0, second=0, microsecond=0)


def window(hours):
    """Devolve (inicio, fim) para as últimas `hours` horas."""
    end = current_hour_utc()
    return end - timedelta(hours=hours), end


def json_response(data, status=200):
    """JsonResponse em UTF-8 legível (mantém acentos sem \\u00e7)."""
    return JsonResponse(data, status=status, json_dumps_params={'ensure_ascii': False})


def error_response(status, code, message):
    return json_response({'error': {'code': code, 'message': message}}, status=status)