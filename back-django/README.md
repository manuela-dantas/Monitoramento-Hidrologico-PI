# API de Monitoramento de Rios e Chuva

*Dados simulados e fictícios. Não representam rios reais e não servem para alertas ou decisões.*

## Requisitos

Python 3.10+ e pip.

## Como rodar (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed
python manage.py runserver 3000
```
Confira em <a href="http://localhost:3000/api/health">http://localhost:3000/api/health</a>. 


```shell
# Testes
python manage.py test

# Roteiro de fumaça:
`\harness\check.ps1` # (com o servidor ligado)
```

## Rotas
| Método | Rota | Parâmetros | Descrição |
|--------|------|-----------|-----------|
| GET | `/api/health` | – | Estado da API e do banco |
| GET | `/api/stations` | – | Estações ativas, em ordem alfabética, com a hora da última leitura |
| GET | `/api/stations/{id}/summary` | id (caminho) | Dados da estação e a leitura mais recente de nível e de chuva |
| GET | `/api/stations/{id}/series` | metric: level (padrão) ou rain; hours: inteiro de 1 a 72 (padrão 24) | Histórico de uma métrica numa janela solicitada |

#### `GET	/api/health`
```json
{ "status": "ok", "database": "ok" }
```

#### `GET	/api/stations`
```json
{
    "data_mode": "simulation", 
    "stations": 
    [
        {
            "id": "EST-01", "name": "Estação Aurora", 
            "river": "Rio Aurora", 
            "municipality": "Vila Aurora", 
            "updated_at": "2026-11-12T18:00:00Z"
        }, 
        {
            "id": "EST-03", 
            "name": "Estação Campo Alto", 
            "river": "Rio do Campo", 
            "municipality": "Campo Alto", 
            "updated_at": "2026-11-12T18:00:00Z"
        }, 
        {
            "id": "EST-02", 
            "name": "Estação Vale Verde", 
            "river": "Rio Verde", 
            "municipality": "Vale Verde", 
            "updated_at": "2026-11-12T18:00:00Z"
        }
    ]
}
```
#### `GET	/api/stations/EST-01/summary`
```json
{
    "data_mode": "simulation", 
    "message": "Amostra simulada. Não representa condições reais.", 
    "station": 
    {
        "id": "EST-01", 
        "name": "Estação Aurora", 
        "river": "Rio Aurora", 
        "municipality": "Vila Aurora"
    }, 
    "latest": 
    {
        "level_observed_at": "2026-11-12T18:00:00Z", 
        "level_m": 1.13, 
        "rain_observed_at": "2026-11-12T18:00:00Z", 
        "rain_mm_h": 0.0
    }
}
```
#### `GET	/api/stations/EST-01/series?metric=level&hours=24`
```json
{
    "data_mode": "simulation", 
    "station_id": "EST-01", "metric": "level", "unit": "m", 
    "interval_minutes": 60, "from": "2026-11-11T19:00:00Z", 
    "to": "2026-11-12T19:00:00Z", 
    "points": 
    [
        {"timestamp": "2026-11-11T19:00:00Z", "value": 1.02}, 
        {"timestamp": "2026-11-11T20:00:00Z", "value": 1.01}, 
        {"timestamp": "2026-11-11T21:00:00Z", "value": 0.99}, 
        {"timestamp": "2026-11-11T22:00:00Z", "value": 0.98}, 
        {"timestamp": "2026-11-11T23:00:00Z", "value": 0.98}, 
        {"timestamp": "2026-11-12T00:00:00Z", "value": 0.97}, 
        {"timestamp": "2026-11-12T01:00:00Z", "value": 0.97}, 
        {"timestamp": "2026-11-12T02:00:00Z", "value": 0.97}, 
        {"timestamp": "2026-11-12T03:00:00Z", "value": 0.98}, 
        {"timestamp": "2026-11-12T04:00:00Z", "value": 0.98}, 
        {"timestamp": "2026-11-12T05:00:00Z", "value": 0.99}, 
        {"timestamp": "2026-11-12T06:00:00Z", "value": 1.01}, 
        {"timestamp": "2026-11-12T07:00:00Z", "value": 1.02}, 
        {"timestamp": "2026-11-12T08:00:00Z", "value": 1.04}, 
        {"timestamp": "2026-11-12T09:00:00Z", "value": 1.05}, 
        {"timestamp": "2026-11-12T10:00:00Z", "value": 1.07}, 
        {"timestamp": "2026-11-12T11:00:00Z", "value": 1.08}, 
        {"timestamp": "2026-11-12T12:00:00Z", "value": 1.1}, 
        {"timestamp": "2026-11-12T13:00:00Z", "value": 1.11}, 
        {"timestamp": "2026-11-12T14:00:00Z", "value": 1.12}, 
        {"timestamp": "2026-11-12T15:00:00Z", "value": 1.13}, 
        {"timestamp": "2026-11-12T16:00:00Z", "value": 1.13}, 
        {"timestamp": "2026-11-12T17:00:00Z", "value": 1.13}, 
        {"timestamp": "2026-11-12T18:00:00Z", "value": 1.13}
    ]
}

```
## Banco de dados
```text
┌────────────────────────┐          ┌──────────────────────────────────┐
│ stations               │          │ observations                     │
├────────────────────────┤ 1     N  ├──────────────────────────────────┤
│ id (PK, texto)         │◄─────────│ id (PK, inteiro)                 │
│ name                   │          │ station_id (FK → stations.id)    │
│ river                  │          │ metric  ('level' | 'rain')       │
│ municipality           │          │ observed_at (data/hora UTC)      │
│ active                 │          │ value                            │
└────────────────────────┘          │ unit    ('m' | 'mm/h')           │
                                    │ source  ('synthetic')            │
                                    │ UNIQUE(station_id, metric,       │
                                    │        observed_at)              │
                                    └──────────────────────────────────┘
```
**Chave primária (PK):** identifica cada linha. Em `stations` é o código de texto (`EST-01`); em `observation` é um inteiro autoincremental.
**Chave estrangeira (FK):** `observations.station_id` aponta para `stations.id`, então toda observação pertence a uma estação que existe.
**Cardinalidade 1:N:** uma estação tem muitas observações; cada observação tem uma única estação.
**UNIQUE (estação + métrica + horário):** impede gravar a mesma leitura duas vezes. É isso que torna o seed repetível.
**CHECK:** o banco recusa métricas fora de `level`/`rain` e unidades fora de `m`/`mm`/`h`.
**Índice (estação, métrica, horário):** acelera a busca da série e da última leitura.

| Original | Nesta versão | Por quê |
|---|---|---|
| observed_at como texto ISO com Z | Coluna datetime do Django, gravada em UTC (2026-09-28 12:00:00) | O Django converte para datetime do Python e compara datas com segurança. A API formata a saída com Z. |
| ON DELETE CASCADE no banco | on_delete=models.CASCADE no Django | O Django apaga as observações ao apagar a estação pelo ORM. |
| PRAGMA foreign_keys = ON no db.js	| Feito automaticamente pelo Django | O backend SQLite do Django liga o PRAGMA em toda conexão. |

## Validações e erros
Todo erro segue o formato `{"error": {"code": "...", "message": "..."}}`.
| Chamada | HTTP | error.code |
|---|---|---| 
| /stations/NAO-EXISTE/summary | 404 | station_not_found |
| /stations/NAO-EXISTE/series | 404 | station_not_found |
| /stations/EST-01/series?metric=vento | 400 | invalid_metric |
| /stations/EST-01/series?hours=100 | 400 | invalid_hours |
| /stations/EST-01/series?hours=abc | 400 | invalid_hours |
| /api/rota-inexistente | 404 | not_found |

## Decisões e limitações
- Django no lugar de Express: a tarefa propôs reimplementar o starter em Node.js/Express usando Python + Django, mantendo o mesmo contrato da API. Por isso o `harness/check.ps1` original funciona sem alterações. O Django substitui as peças do starter: `views.py` + `urls.py` fazem o papel do Express, `models.py` + migrations o do `db.js`/`schema.sql`, e o comando `seed` o do `seed.js`. As consultas são parametrizadas pelo ORM, protegendo contra SQL injection, e `views.py` fica separado de `repository.py`.
- Datas gravadas como datetime UTC e formatadas com Z na saída.
- O seed usa a hora atual: rodar em outra hora adiciona horários novos, sem duplicar os antigos. A primeira execução cria 438 observações (3 estações × 73 horários × 2 métricas). Se o seed ficar mais de 72 horas sem rodar, as séries voltam vazias.
- Sem autenticação, previsão ou sensores reais (fora do escopo).

## Próximos passos
- Paginação e filtros por intervalo de datas
- Cache das respostas de leitura
- Docker e docker-compose
- Testes de carga
- Documentação interativa (OpenAPI + Swagger UI)
- Relatório de qualidade dos dados e exportação da série em CSV