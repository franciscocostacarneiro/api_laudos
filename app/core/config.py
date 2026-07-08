"""Application configuration.

Values can be overridden via environment variables, which is the recommended
way to configure services running in containers.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = PROJECT_ROOT / "laudos_completos.xlsx"


class Settings:
    """Lightweight settings object.

    We avoid pydantic-settings here to keep dependencies minimal, but expose
    the same env-first philosophy.
    """

    app_name: str = "API Laudos de Avaliação de Imóveis (CEF)"
    app_version: str = "1.0.0"
    app_description: str = (
        "REST API for querying real estate valuation reports (laudos) "
        "extracted from Caixa Econômica Federal (SIMIL) PDFs for the "
        "Região Metropolitana de Belo Horizonte (MG), Brazil."
    )
    data_file: Path = Path(os.getenv("LAUDOS_DATA_FILE", str(DEFAULT_DATA_FILE)))

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    # Dataset metadata (from the data dictionary)
    author: str = "Francisco Costa Carneiro"
    coverage: str = "Região Metropolitana de Belo Horizonte (RMBH), MG"
    source_file_name: str = "laudos_completos.xlsx"
    total_columns: int = 145


settings = Settings()
