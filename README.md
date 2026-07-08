# API Laudos de Avaliação de Imóveis (CEF)

REST API for querying real estate valuation reports (**laudos**) extracted from
Caixa Econômica Federal (SIMIL) PDFs, covering the Região Metropolitana de
Belo Horizonte (MG), Brazil. Designed following the skills in `.llm/SKILLS/`:

- **api-and-interface-design** — contract‑first, consistent error envelope,
  validation at boundaries, pagination by default, additive evolution.
- **api-connector-builder** — repo‑native layout (`app/`, `core/`, `api/`),
  config schema, explicit errors, tests that mirror the host style.
- **api-design** — plural‑noun resource names, semantic HTTP status codes,
  offset pagination, query‑param filtering, URL path versioning (`/api/v1/...`).

---

## 🚀 API em Produção

✅ **Hospedada em Replit**  
📍 **URL:** https://api-laudos--chicoilha.replit.com  
📚 **Swagger UI:** https://api-laudos--chicoilha.replit.com/docs  
❤️ **Health:** https://api-laudos--chicoilha.replit.com/health  

[→ Ver status em produção](./PRODUCTION_STATUS.md)

---

## 1. Quickstart

### Requirements
- Python 3.11+ (tested on 3.14)
- The data file `laudos_completos.xlsx` in the project root (already present)

### Install
```bash
pip install -r requirements.txt
```

### Run the API
```bash
uvicorn app.main:app --reload
```

- Swagger UI:      <http://127.0.0.1:8000/docs>
- ReDoc UI:        <http://127.0.0.1:8000/redoc>
- OpenAPI schema:  <http://127.0.0.1:8000/openapi.json>
- Health:          <http://127.0.0.1:8000/health>
- Info:            <http://127.0.0.1:8000/info>

> Tip: to export the OpenAPI spec to a static file, run:
> ```bash
> python scripts/export_openapi.py
> ```
> This writes `openapi.json` to the project root for use with external tools.

### Run tests
```bash
pytest -v
```

---

## 2. Dataset summary

| Attribute        | Value                                                          |
|------------------|----------------------------------------------------------------|
| Source file      | `laudos_completos.xlsx`                                        |
| Dictionary       | `dicionario_dados.pdf`                                         |
| Reports          | **189**                                                        |
| Columns          | **145**                                                        |
| Geographic scope | Região Metropolitana de Belo Horizonte (RMBH), MG              |
| Period           | 2025 – 2026                                                    |
| Author           | Francisco Costa Carneiro                                       |
| Source system    | SIMIL / Caixa Econômica Federal                                |
| Sample target    | `valor_avaliacao_r` (R$) — R$ 120.000 a R$ 2.050.000           |

---

## 3. Project structure

```
api_laudos/
├── .llm/                        # Skills used as design guidance
│   └── SKILLS/
│       ├── api-and-interface-design/SKILL.md
│       ├── api-connector-builder/SKILL.md
│       └── api-design/SKILL.md
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + health/info + Swagger metadata
│   ├── schemas.py               # Pydantic schemas = the API contract
│   ├── api/
│   │   ├── __init__.py
│   │   └── laudos.py            # /api/v1/laudos endpoints
│   └── core/
│       ├── __init__.py
│       ├── config.py            # Settings (env-configurable)
│       ├── data.py              # Excel → in-memory store + filtering/pagination
│       └── errors.py            # Consistent error envelope + handlers
├── tests/
│   └── test_api.py             # 20 smoke tests with TestClient
├── scripts/
│   └── export_openapi.py       # Exports openapi.json
├── requirements.txt
├── laudos_completos.xlsx
└── dicionario_dados.pdf
```

---

## 4. Endpoints

Base path: `/api/v1`

### 4.1 Health & metadata

| Method | Path          | Description                                       |
|--------|---------------|---------------------------------------------------|
| GET    | `/`           | Root — links to docs                              |
| GET    | `/health`     | Service health + version + reports loaded         |
| GET    | `/info`       | Dataset & API metadata (totals, coverage, author) |

### 4.2 Laudos

| Method | Path                          | Description                                              |
|--------|-------------------------------|----------------------------------------------------------|
| GET    | `/api/v1/laudos`              | List reports (paginated, filtered, sorted, searchable)  |
| GET    | `/api/v1/laudos/{laudoId}`    | Get a single report by internal sequential ID            |
| GET    | `/api/v1/laudos/stats`         | Aggregate stats by category/municipality + value ranges|

### 4.3 Documentation

| Method | Path             | Description                              |
|--------|------------------|------------------------------------------|
| GET    | `/docs`          | Swagger UI (interactive)                 |
| GET    | `/redoc`         | ReDoc UI (read-only, prettier)           |
| GET    | `/openapi.json`  | OpenAPI 3.1 schema (machine-readable)    |

---

## 5. Query parameters for `GET /api/v1/laudos`

All parameters are optional. Pagination defaults to `page=1&pageSize=20`.

| Parameter     | Type    | Default | Description                                                          |
|---------------|---------|---------|----------------------------------------------------------------------|
| `page`        | int     | `1`     | Page number (1-indexed, ≥1)                                          |
| `pageSize`    | int     | `20`    | Items per page (1–100)                                               |
| `sortBy`      | enum    | `id`    | `id`, `numeroLaudo`, `valorAvaliacaoReais`, `areaAvaliacaoM2`, `dataReferenciaAvaliacao`, `municipio`, `bairro` |
| `sortOrder`   | enum    | `asc`   | `asc` or `desc`                                                      |
| `categoria`   | string  | —       | `Apartamento`, `Casa`, `Lote`                                        |
| `uf`          | string  | —       | Federation unit, e.g. `MG`                                           |
| `municipio`   | string  | —       | Municipality name (case-insensitive)                                 |
| `bairro`      | string  | —       | Neighborhood (case-insensitive)                                      |
| `grupoLaudo`  | string  | —       | `Unidade em Prédio`, `Unidade Isolada Construção`, `Unidade Isolada Terreno` |
| `valorMin`    | float   | —       | Min appraisal value in BRL (≥0)                                      |
| `valorMax`    | float   | —       | Max appraisal value in BRL (≥0)                                      |
| `areaMin`     | float   | —       | Min evaluation area in m² (≥0)                                       |
| `areaMax`     | float   | —       | Max evaluation area in m² (≥0)                                      |
| `dataInicio`  | date    | —       | Reference date lower bound (`DD/MM/YYYY`)                            |
| `dataFim`     | date    | —       | Reference date upper bound (`DD/MM/YYYY`)                            |
| `q`           | string  | —       | Free-text search across `numero_laudo`, `bairro`, `endereco_completo`, `municipio` |

### Examples

```bash
# Page 1 with default filters
curl "http://127.0.0.1:8000/api/v1/laudos"

# Apartments in BELO HORIZONTE, sorted by value desc
curl "http://127.0.0.1:8000/api/v1/laudos?categoria=Apartamento&municipio=BELO%20HORIZONTE&sortBy=valorAvaliacaoReais&sortOrder=desc"

# Values between R$ 200.000 and R$ 400.000
curl "http://127.0.0.1:8000/api/v1/laudos?valorMin=200000&valorMax=400000&pageSize=100"

# Full-text search
curl "http://127.0.0.1:8000/api/v1/laudos?q=SERRA&pageSize=100"

# Get report #0
curl "http://127.0.0.1:8000/api/v1/laudos/0"

# Aggregate stats
curl "http://127.0.0.1:8000/api/v1/laudos/stats"
```

---

## 6. Response formats

### 6.1 Paginated list (`GET /api/v1/laudos`)

```json
{
  "data": [
    {
      "id": 0,
      "numeroLaudo": "6994.1022.000579403/2026.01.01.01-000001",
      "categoriaImovel": "Apartamento",
      "uf": "MG",
      "municipio": "BELO HORIZONTE",
      "bairro": "VENDA NOVA",
      "dataReferenciaAvaliacao": "25/04/2026",
      "valorAvaliacaoReais": 268000.0,
      "areaAvaliacaoM2": 44.98,
      "arquivoPdf": "LA000579403202601010100000101.pdf"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 189,
    "totalPages": 10
  }
}
```

### 6.2 Single report (`GET /api/v1/laudos/{laudoId}`)

Returns the full `Laudo` object with nested `localizacao`, `coordenadas`,
`avaliacao`, `responsavelTecnico` and `empresa` groups. See the Swagger UI
(`/docs`) for the complete schema with field-level descriptions.

### 6.3 Errors

All error responses share a single shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": [
      { "field": "sortBy", "message": "Must be one of [...]", "code": "invalid_enum" }
    ]
  }
}
```

| Status | Code              | Description                                   |
|--------|-------------------|-----------------------------------------------|
| 400    | `bad_request`     | Malformed request                              |
| 401    | `unauthorized`    | Authentication required or invalid (future)    |
| 403    | `forbidden`       | Authenticated but not authorized (future)      |
| 404    | `not_found`       | Resource not found                             |
| 422    | `validation_error`| Validation failed (query/path/body)            |
| 500    | `internal_error`  | Unexpected server error (no internals leaked)  |

---

## 7. Design principles applied

### Hyrum's Law
Every observable behavior is a potential commitment — the contract (in
`schemas.py`) is intentional and additive.

### Contract first
`app/schemas.py` defines the public types before the implementation. The
endpoints depend on those types, not the raw spreadsheet shape.

### Consistent error semantics
A single `APIError` envelope (`{"error": {...}}`) is used for every error
path, including FastAPI's request validation errors and unhandled exceptions
(internal details are never leaked).

### Validate at boundaries
All external input (query params) is validated at the route handler:
whitelisted `sortBy`/`sortOrder`, range sanity (`valorMin ≤ valorMax`), type
coercion. Internal code trusts the validated types.

### Pagination by default
List endpoints always paginate; `pageSize` is capped at 100.

### Addition over modification
Schemas use optional fields so new fields can be added without breaking
existing consumers.

### URL path versioning
All resource routes are namespaced under `/api/v1/...`.

---

## 8. Testing

Run the full suite:

```bash
pytest -v
```

Tests use FastAPI's `TestClient` against the real Excel file and cover:
- All endpoints (health, info, list, get, stats)
- Pagination math (page/totalPages/totalItems)
- Filters (categoria, value range, free-text search)
- Sorting (asc/desc by value)
- Error format consistency (404, 422 for invalid sortBy/sortOrder/page/range)
- OpenAPI schema availability and Swagger UI
