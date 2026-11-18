from django.core.management import call_command
from django.test import TestCase

from .models import Observation


class ExtrasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed', '--com-lacunas', verbosity=0)

    # --- 17.1 seed com lacunas ---

    def test_seed_com_lacunas_tem_menos_observacoes(self):
        self.assertLess(Observation.objects.count(), 438)

    def test_seed_com_lacunas_e_idempotente(self):
        antes = Observation.objects.count()
        call_command('seed', '--com-lacunas', verbosity=0)
        self.assertEqual(Observation.objects.count(), antes)

    def test_limpar_recria_a_amostra_completa(self):
        call_command('seed', '--limpar', verbosity=0)
        self.assertEqual(Observation.objects.count(), 438)

    def test_resumo_mostra_horarios_diferentes_por_metrica(self):
        latest = self.client.get('/api/stations/EST-02/summary').json()['latest']
        self.assertNotEqual(latest['level_observed_at'], latest['rain_observed_at'])

    # --- 17.2 relatório de qualidade ---

    def test_qualidade_bate_com_a_serie(self):
        url = '/api/stations/EST-02/{}?metric=rain&hours=24'
        serie = self.client.get(url.format('series')).json()
        qualidade = self.client.get(url.format('quality')).json()

        self.assertEqual(qualidade['expected_points'], 25)
        self.assertEqual(qualidade['found_points'], len(serie['points']))
        self.assertEqual(
            qualidade['missing_points'],
            len(qualidade['missing_timestamps'])
        )
        self.assertEqual(
            qualidade['expected_points'],
            qualidade['found_points'] + qualidade['missing_points']
        )

    def test_qualidade_valida_parametros(self):
        response = self.client.get(
            '/api/stations/EST-01/quality?hours=0'
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/stations/NAO/quality')
        self.assertEqual(response.status_code, 404)