"""FastAPI application entrypoint.

Run with::

    uvicorn app.main:app --reload

Then open the Swagger UI at http://127.0.0.1:8000/docs
and the ReDoc UI at http://127.0.0.1:8000/redoc.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.laudos import router as laudos_router
from app.core.config import settings
from app.core.data import get_store, init_store
from app.core.errors import register_exception_handlers
from app.schemas import HealthResponse, InfoResponse


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    # Load the Excel data into memory exactly once at startup.
    init_store()
    store = get_store()
    app.state.store = store
    yield
    # No explicit teardown required for an in-memory store.


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    contact={
        "name": settings.author,
        "url": "https://www.gov.br/caixa",
    },
    license_info={
        "name": "Restricted — CEF internal data",
        "url": "https://www.gov.br/caixa",
    },
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Health",
            "description": "Service health and metadata endpoints.",
        },
        {
            "name": "Laudos",
            "description": (
                "Operations to list, filter and inspect real estate valuation "
                "reports (laudos) extracted from Caixa Econômica Federal PDFs."
            ),
        },
    ],
)

register_exception_handlers(app)


# -- Health & metadata endpoints ------------------------------------------


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_model=HealthResponse,
    description="Returns service health, current version and number of loaded reports.",
)
def health() -> HealthResponse:
    store = get_store()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        reportsLoaded=store.total,
    )


@app.get(
    "/info",
    tags=["Health"],
    summary="Dataset and API metadata",
    response_model=InfoResponse,
    description="Returns metadata about the API and the underlying dataset.",
)
def info() -> InfoResponse:
    store = get_store()
    return InfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        totalReports=store.total,
        totalColumns=settings.total_columns,
        sourceFile=settings.source_file_name,
        coverage=settings.coverage,
        author=settings.author,
        endpoints=[
            "GET /api/v1/laudos",
            "GET /api/v1/laudos/{laudoId}",
            "GET /api/v1/laudos/stats",
            "GET /health",
            "GET /info",
            "GET /docs  (Swagger UI)",
            "GET /redoc (ReDoc UI)",
            "GET /openapi.json (OpenAPI schema)",
        ],
    )


# -- Domain routes --------------------------------------------------------

app.include_router(laudos_router)


@app.get("/", tags=["Health"], include_in_schema=False)
def root() -> dict:
    return {
        "message": "API Laudos — see /docs for the Swagger UI",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }
