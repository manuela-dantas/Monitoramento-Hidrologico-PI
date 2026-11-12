from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from .models import Observation, Station
from .utils import current_hour_utc


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed', verbosity=0)

    def test_seed_e_idempotente(self):
        antes = Observation.objects.count()
        call_command('seed', verbosity=0)
        self.assertEqual(Observation.objects.count(), antes)
        self.assertEqual(Station.objects.count(), 3)

    def test_lista_estacoes_em_ordem_alfabetica(self):
        body = self.client.get('/api/stations').json()
        self.assertEqual(body['data_mode'], 'simulation')
        nomes = [s['name'] for s in body['stations']]
        self.assertEqual(nomes, sorted(nomes))
        self.assertTrue(body['stations'][0]['updated_at'].endswith('Z'))

    def test_resumo_tem_horario_por_metrica(self):
        body = self.client.get('/api/stations/EST-01/summary').json()
        self.assertEqual(body['station']['id'], 'EST-01')
        self.assertIn('level_observed_at', body['latest'])
        self.assertIn('rain_mm_h', body['latest'])

    def test_serie_ordenada_e_com_unidade(self):
        body = self.client.get('/api/stations/EST-01/series?metric=level&hours=24').json()
        self.assertEqual(body['unit'], 'm')
        horarios = [p['timestamp'] for p in body['points']]
        self.assertEqual(horarios, sorted(horarios))
        self.assertTrue(all(h.endswith('Z') for h in horarios))

    def test_lacuna_nao_e_preenchida(self):
        apagado = current_hour_utc() - timedelta(hours=2)
        Observation.objects.filter(station_id='EST-01', metric='rain', observed_at=apagado).delete()
        body = self.client.get('/api/stations/EST-01/series?metric=rain&hours=4').json()
        self.assertEqual(len(body['points']), 4)

    def test_serie_vazia_retorna_lista_vazia(self):
        Observation.objects.filter(station_id='EST-02').delete()
        body = self.client.get('/api/stations/EST-02/series?hours=6').json()
        self.assertEqual(body['points'], [])

    def test_erros(self):
        casos = [
            ('/api/stations/NAO-EXISTE/summary', 404, 'station_not_found'),
            ('/api/stations/NAO-EXISTE/series', 404, 'station_not_found'),
            ('/api/stations/EST-01/series?metric=vento', 400, 'invalid_metric'),
            ('/api/stations/EST-01/series?hours=0', 400, 'invalid_hours'),
            ('/api/stations/EST-01/series?hours=73', 400, 'invalid_hours'),
            ('/api/stations/EST-01/series?hours=abc', 400, 'invalid_hours'),
        ]
        for url, status, code in casos:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)
                self.assertEqual(response.json()['error']['code'], code)

    def test_erro_inesperado_vira_500_sem_detalhes(self):
        with patch('monitoring.repository.list_stations', side_effect=RuntimeError('segredo')):
            response = self.client.get('/api/stations')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error']['code'], 'internal_error')
        self.assertNotIn('segredo', response.content.decode())