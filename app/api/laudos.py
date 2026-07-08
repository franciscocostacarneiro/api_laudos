"""Versioned v1 router exposing the laudos endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.config import settings
from app.core.data import LaudoStore, get_store
from app.core.errors import NotFoundError, ValidationError_
from app.schemas import (
    Laudo,
    PaginatedLaudos,
    PaginationMeta,
    StatsResponse,
)

router = APIRouter(prefix="/api/v1/laudos", tags=["Laudos"])

# Whitelisted values for sort_by and sort_order — validates at the boundary.
ALLOWED_SORT_BY = {
    "id",
    "numeroLaudo",
    "valorAvaliacaoReais",
    "areaAvaliacaoM2",
    "dataReferenciaAvaliacao",
    "municipio",
    "bairro",
}
ALLOWED_SORT_ORDER = {"asc", "desc"}


@router.get(
    "",
    summary="List valuation reports (laudos)",
    response_model=PaginatedLaudos,
    description=(
        "Returns a paginated list of real estate valuation reports (laudos). "
        "Supports filtering by category, location, value and area ranges, "
        "reference date, and free-text search. Sort by any whitelisted field."
    ),
    responses={
        422: {"description": "Validation error for query parameters."},
    },
)
def list_laudos(
    store: LaudoStore = Depends(get_store),
    page: int = Query(1, ge=1, description="Page number (1-indexed)."),
    pageSize: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page (1-100).",
    ),
    sortBy: str = Query("id", description="Sort field. One of: " + ", ".join(sorted(ALLOWED_SORT_BY))),
    sortOrder: str = Query("asc", description="Sort order: 'asc' or 'desc'."),
    categoria: str | None = Query(
        None, description="Property category: 'Apartamento', 'Casa' or 'Lote'."
    ),
    uf: str | None = Query(None, description="Federation unit (state), e.g. 'MG'."),
    municipio: str | None = Query(None, description="Municipality name (case-insensitive)."),
    bairro: str | None = Query(None, description="Neighborhood name (case-insensitive)."),
    grupoLaudo: str | None = Query(
        None,
        description="Report group: 'Unidade em Prédio', 'Unidade Isolada Construção' "
        "or 'Unidade Isolada Terreno'.",
    ),
    valorMin: float | None = Query(None, ge=0, description="Minimum appraisal value in BRL."),
    valorMax: float | None = Query(None, ge=0, description="Maximum appraisal value in BRL."),
    areaMin: float | None = Query(None, ge=0, description="Minimum evaluation area in m²."),
    areaMax: float | None = Query(None, ge=0, description="Maximum evaluation area in m²."),
    dataInicio: str | None = Query(
        None, description="Reference date lower bound (DD/MM/YYYY)."
    ),
    dataFim: str | None = Query(
        None, description="Reference date upper bound (DD/MM/YYYY)."
    ),
    q: str | None = Query(
        None, description="Free-text search across numero, bairro, endereco and municipio."
    ),
) -> PaginatedLaudos:
    # Validate sort params at the boundary
    if sortBy not in ALLOWED_SORT_BY:
        raise ValidationError_(
            f"Invalid sortBy '{sortBy}'. Allowed: {sorted(ALLOWED_SORT_BY)}.",
            [
                {
                    "field": "sortBy",
                    "message": f"Must be one of {sorted(ALLOWED_SORT_BY)}",
                    "code": "invalid_enum",
                }
            ],
        )
    if sortOrder not in ALLOWED_SORT_ORDER:
        raise ValidationError_(
            f"Invalid sortOrder '{sortOrder}'. Allowed: {sorted(ALLOWED_SORT_ORDER)}.",
            [
                {
                    "field": "sortOrder",
                    "message": f"Must be one of {sorted(ALLOWED_SORT_ORDER)}",
                    "code": "invalid_enum",
                }
            ],
        )
    if valorMin is not None and valorMax is not None and valorMin > valorMax:
        raise ValidationError_(
            "valorMin must be <= valorMax.",
            [
                {
                    "field": "valorMin",
                    "message": "valorMin must be less than or equal to valorMax.",
                    "code": "invalid_range",
                }
            ],
        )
    if areaMin is not None and areaMax is not None and areaMin > areaMax:
        raise ValidationError_(
            "areaMin must be <= areaMax.",
            [
                {
                    "field": "areaMin",
                    "message": "areaMin must be less than or equal to areaMax.",
                    "code": "invalid_range",
                }
            ],
        )

    summaries, total_items = store.list_summaries(
        page=page,
        page_size=pageSize,
        sort_by=sortBy,
        sort_order=sortOrder,
        categoria=categoria,
        uf=uf,
        municipio=municipio,
        bairro=bairro,
        grupo_laudo=grupoLaudo,
        valor_min=valorMin,
        valor_max=valorMax,
        area_min=areaMin,
        area_max=areaMax,
        data_inicio=dataInicio,
        data_fim=dataFim,
        q=q,
    )
    total_pages = (total_items + pageSize - 1) // pageSize if total_items else 0
    return PaginatedLaudos(
        data=summaries,
        pagination=PaginationMeta(
            page=page,
            pageSize=pageSize,
            totalItems=total_items,
            totalPages=total_pages,
        ),
    )


@router.get(
    "/stats",
    summary="Aggregate statistics over the dataset",
    response_model=StatsResponse,
    description=(
        "Returns aggregate statistics: counts and value averages by category "
        "and municipality, plus min/max/mean/median for unit value (R$/m²) "
        "and total appraisal value (R$)."
    ),
)
def get_stats(
    store: LaudoStore = Depends(get_store),
    categoria: str | None = Query(
        None, description="Filter stats by property category."
    ),
    municipio: str | None = Query(
        None, description="Filter stats by municipality."
    ),
) -> StatsResponse:
    return store.get_stats(categoria=categoria, municipio=municipio)


@router.get(
    "/{laudoId}",
    summary="Get a single valuation report by ID",
    response_model=Laudo,
    description="Returns the full representation of a single laudo by its internal sequential ID.",
    responses={
        404: {"description": "No laudo with the given ID exists."},
    },
)
def get_laudo(laudoId: int, store: LaudoStore = Depends(get_store)) -> Laudo:
    if laudoId < 0:
        raise NotFoundError("Laudo", laudoId)
    return store.get_by_id(laudoId)
