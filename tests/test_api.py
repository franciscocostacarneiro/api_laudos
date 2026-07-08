"""Smoke tests for the Laudos API.

These tests use FastAPI's TestClient (no network required) and the real
Excel file in the project root. They validate that every endpoint works,
the contract (schemas) holds, and the documented error format is enforced.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `app` is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "docs" in body


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"
    assert body["reportsLoaded"] == 189


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    body = response.json()
    assert body["name"].startswith("API Laudos")
    assert body["totalReports"] == 189
    assert body["totalColumns"] == 145
    assert body["sourceFile"] == "laudos_completos.xlsx"
    assert any(ep.endswith("/api/v1/laudos") for ep in body["endpoints"])


def test_list_laudos_default():
    response = client.get("/api/v1/laudos")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "pagination" in body
    p = body["pagination"]
    assert p["page"] == 1
    assert p["pageSize"] == 20
    assert p["totalItems"] == 189
    assert p["totalPages"] == 10  # 189 / 20 = 9.45 -> 10 pages
    assert len(body["data"]) == 20
    item = body["data"][0]
    assert "id" in item
    assert "numeroLaudo" in item
    assert "valorAvaliacaoReais" in item


def test_list_laudos_pagination():
    response = client.get("/api/v1/laudos?page=2&pageSize=10")
    assert response.status_code == 200
    body = response.json()
    p = body["pagination"]
    assert p["page"] == 2
    assert p["pageSize"] == 10
    assert p["totalItems"] == 189
    assert p["totalPages"] == 19  # 189 / 10 = 18.9 -> 19 pages
    assert len(body["data"]) == 10


def test_list_laudos_filter_categoria():
    response = client.get("/api/v1/laudos?categoria=Apartamento")
    assert response.status_code == 200
    body = response.json()
    for item in body["data"]:
        assert item["categoriaImovel"] == "Apartamento"


def test_list_laudos_filter_value_range():
    response = client.get(
        "/api/v1/laudos?valorMin=200000&valorMax=400000&pageSize=100"
    )
    assert response.status_code == 200
    body = response.json()
    for item in body["data"]:
        v = item["valorAvaliacaoReais"]
        assert v is None or (200000 <= v <= 400000)


def test_list_laudos_sort_desc():
    # Sort by valorAvaliacaoReais desc — first item should be the max (2,050,000)
    response = client.get(
        "/api/v1/laudos?sortBy=valorAvaliacaoReais&sortOrder=desc&pageSize=100"
    )
    assert response.status_code == 200
    body = response.json()
    values = [i["valorAvaliacaoReais"] for i in body["data"] if i["valorAvaliacaoReais"] is not None]
    assert values == sorted(values, reverse=True)
    assert values[0] == 2050000.0


def test_list_laudos_q_search():
    response = client.get("/api/v1/laudos?q=SERRA&pageSize=100")
    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["totalItems"] > 0
    # The summary doesn't expose enderecoCompleto; verify each hit by fetching
    # the full record and checking that "SERRA" appears somewhere searchable.
    for item in body["data"]:
        full = client.get(f"/api/v1/laudos/{item['id']}").json()
        haystack = " ".join(
            [
                full.get("numeroLaudo") or "",
                full["localizacao"].get("municipio") or "",
                full["localizacao"].get("bairro") or "",
                full["localizacao"].get("enderecoCompleto") or "",
            ]
        ).upper()
        assert "SERRA" in haystack


def test_list_laudos_invalid_sort_by():
    response = client.get("/api/v1/laudos?sortBy=invalidField")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"][0]["field"] == "sortBy"


def test_list_laudos_invalid_sort_order():
    response = client.get("/api/v1/laudos?sortOrder=sideways")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"][0]["field"] == "sortOrder"


def test_list_laudos_invalid_page():
    response = client.get("/api/v1/laudos?page=0")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"


def test_list_laudos_value_min_gt_max():
    response = client.get("/api/v1/laudos?valorMin=500000&valorMax=100000")
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"][0]["field"] == "valorMin"


def test_get_laudo_by_id():
    response = client.get("/api/v1/laudos/0")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 0
    assert body["localizacao"]["uf"] == "MG"
    assert "avaliacao" in body
    assert "responsavelTecnico" in body
    assert "empresa" in body


def test_get_laudo_not_found():
    response = client.get("/api/v1/laudos/9999")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert "9999" in body["error"]["message"]


def test_get_laudo_negative_id():
    response = client.get("/api/v1/laudos/-1")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"


def test_stats():
    response = client.get("/api/v1/laudos/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 189
    assert len(body["porCategoria"]) == 3
    # Apartamento should be the most common
    assert body["porCategoria"][0]["categoria"] == "Apartamento"
    assert body["valores"]["valorAvaliacaoReais"]["count"] == 182  # 189 - 7 nulls approx
    assert body["valores"]["valorAvaliacaoReais"]["min"] == 120000.0
    assert body["valores"]["valorAvaliacaoReais"]["max"] == 2050000.0


def test_openapi_schema_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"].startswith("API Laudos")
    assert "/api/v1/laudos" in schema["paths"]
    assert "/api/v1/laudos/{laudoId}" in schema["paths"]
    assert "/api/v1/laudos/stats" in schema["paths"]
    assert "/health" in schema["paths"]
    assert "/info" in schema["paths"]


def test_swagger_ui_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()


def test_error_format_consistency():
    """Every error response should share the same {"error": {...}} shape."""
    for path in ["/api/v1/laudos/9999", "/api/v1/laudos?sortBy=nope"]:
        response = client.get(path)
        assert response.status_code >= 400
        body = response.json()
        assert "error" in body
        assert "code" in body["error"]
        assert "message" in body["error"]
