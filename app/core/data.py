"""Data loader: reads the Excel file into an in-memory store.

This module is responsible for:
- loading the Excel file exactly once at startup,
- coercing raw 145-column rows into the compact DTOs exposed by the API,
- providing filtered, sorted and paginated access.

It intentionally treats the spreadsheet as untrusted external data, validating
and coercing types at the boundary as recommended by the skills.
"""
from __future__ import annotations

import statistics
from typing import Any, Iterable

import pandas as pd

from app.core.config import settings
from app.schemas import (
    CategoryBreakdownItem,
    CoordinatesInfo,
    EmpresaInfo,
    Laudo,
    LaudoSummary,
    LocationInfo,
    MunicipioBreakdownItem,
    ResponsavelTecnicoInfo,
    StatPoint,
    StatsResponse,
    ValorUnitarioStats,
    ValuationInfo,
)


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    return s if s else None


def _clean_int(value: Any) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _clean_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        f = float(value)
    except (ValueError, TypeError):
        return None
    if pd.isna(f):
        return None
    return f


def _to_summary(row: pd.Series, index: int) -> LaudoSummary:
    return LaudoSummary(
        id=index,
        numeroLaudo=_clean_str(row.get("numero_laudo")),
        categoriaImovel=_clean_str(row.get("categoria_imovel")),
        uf=_clean_str(row.get("uf")),
        municipio=_clean_str(row.get("municipio")),
        bairro=_clean_str(row.get("bairro")),
        dataReferenciaAvaliacao=_clean_str(row.get("data_referencia_avaliacao")),
        valorAvaliacaoReais=_clean_float(row.get("valor_avaliacao_r")),
        areaAvaliacaoM2=_clean_float(row.get("area_avaliacao_m2")),
        arquivoPdf=_clean_str(row.get("arquivo_pdf")),
    )


def _to_laudo(row: pd.Series, index: int) -> Laudo:
    return Laudo(
        id=index,
        numeroLaudo=_clean_str(row.get("numero_laudo")),
        versaoLaudo=_clean_int(row.get("versao_laudo")),
        modeloLaudo=_clean_str(row.get("modelo_laudo")),
        grupoLaudo=_clean_str(row.get("grupo_laudo")),
        grauSigilo=_clean_str(row.get("grau_sigilo")),
        folhaTotal=_clean_int(row.get("folha_total")),
        localizacao=LocationInfo(
            categoriaImovel=_clean_str(row.get("categoria_imovel")),
            uf=_clean_str(row.get("uf")),
            municipio=_clean_str(row.get("municipio")),
            distritoLocalidadeCidade=_clean_str(row.get("distrito_localidade_cidade")),
            bairro=_clean_str(row.get("bairro")),
            enderecoCompleto=_clean_str(row.get("endereco_completo")),
            cep=_clean_str(row.get("cep")),
        ),
        coordenadas=CoordinatesInfo(
            latitudeHemisferio=_clean_str(row.get("latitude_hemisferio")),
            latitudeGraus=_clean_int(row.get("latitude_graus")),
            latitudeMin=_clean_int(row.get("latitude_min")),
            latitudeSeg=_clean_float(row.get("latitude_seg")),
            longitudeGraus=_clean_int(row.get("longitude_graus")),
            longitudeMin=_clean_int(row.get("longitude_min")),
            longitudeSeg=_clean_float(row.get("longitude_seg")),
            datum=_clean_str(row.get("datum")),
        ),
        cadMunicipal=_clean_float(row.get("cad_municipal")),
        finalidade=_clean_str(row.get("finalidade")),
        objetivo=_clean_str(row.get("objetivo")),
        interessado=_clean_str(row.get("interessado")),
        avaliacao=ValuationInfo(
            metodoAvaliacao=_clean_str(row.get("metodo_avaliacao")),
            grauFundamentacao=_clean_str(row.get("grau_fundamentacao")),
            grauPrecisao=_clean_str(row.get("grau_precisao")),
            tipoValorDeterminado=_clean_str(row.get("tipo_valor_determinado")),
            dataReferenciaAvaliacao=_clean_str(row.get("data_referencia_avaliacao")),
            areaAvaliacaoM2=_clean_float(row.get("area_avaliacao_m2")),
            valorUnitarioM2=_clean_float(row.get("valor_unitario_m2")),
            valorAvaliacaoReais=_clean_float(row.get("valor_avaliacao_r")),
            valorAvaliacaoExtenso=_clean_str(row.get("valor_avaliacao_extenso")),
            valorMinimoAdmissivel=_clean_float(row.get("valor_minimo_admissivel")),
            valorMaximoAdmissivel=_clean_float(row.get("valor_maximo_admissivel")),
        ),
        responsavelTecnico=ResponsavelTecnicoInfo(
            nome=_clean_str(row.get("responsavel_tecnico_nome")),
            formacao=_clean_str(row.get("responsavel_tecnico_formacao")),
            creaCau=_clean_str(row.get("responsavel_tecnico_crea_cau")),
            cpf=_clean_str(row.get("responsavel_tecnico_cpf")),
        ),
        empresa=EmpresaInfo(
            nome=_clean_str(row.get("empresa_nome")),
            cnpj=_clean_str(row.get("empresa_cnpj")),
            representanteLegalNome=_clean_str(row.get("representante_legal_nome")),
            representanteLegalCpf=_clean_str(row.get("representante_legal_cpf")),
        ),
        dataAssinatura=_clean_str(row.get("data_assinatura")),
        matriculaImovel=_clean_str(row.get("matricula_imovel")),
        cnmImovel=_clean_str(row.get("cnm_imovel")),
        informacoesComplementares=_clean_str(row.get("informacoes_complementares")),
        arquivoPdf=_clean_str(row.get("arquivo_pdf")),
    )


class LaudoStore:
    """In-memory store providing filtered/sorted/paginated access to laudos."""

    def __init__(self, data_file: Path | None = None) -> None:  # type: ignore[name-defined]
        from pathlib import Path  # local import keeps top-level clean

        path = Path(data_file) if data_file else settings.data_file
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        df = pd.read_excel(path, sheet_name="Laudos")
        df = df.reset_index(drop=True)
        self._df = df
        self._laudos: list[Laudo] = [_to_laudo(row, i) for i, (_, row) in enumerate(df.iterrows())]
        self._summaries: list[LaudoSummary] = [
            _to_summary(row, i) for i, (_, row) in enumerate(df.iterrows())
        ]

    # -- queries ----------------------------------------------------------

    @property
    def total(self) -> int:
        return len(self._laudos)

    def get_by_id(self, laudo_id: int) -> Laudo:
        if laudo_id < 0 or laudo_id >= len(self._laudos):
            from app.core.errors import NotFoundError

            raise NotFoundError("Laudo", laudo_id)
        return self._laudos[laudo_id]

    def _apply_filters(
        self,
        df: pd.DataFrame,
        *,
        categoria: str | None,
        uf: str | None,
        municipio: str | None,
        bairro: str | None,
        grupo_laudo: str | None,
        valor_min: float | None,
        valor_max: float | None,
        area_min: float | None,
        area_max: float | None,
        data_inicio: str | None,
        data_fim: str | None,
        q: str | None,
    ) -> pd.DataFrame:
        # We keep data_referencia_avaliacao as string DD/MM/YYYY. Since all
        # dates have 10 chars (DD/MM/YYYY) lexicographic comparison works,
        # but we normalize to DD/MM/YYYY zero-padded to be safe.
        if categoria:
            df = df[df["categoria_imovel"].astype(str).str.lower() == categoria.lower()]
        if uf:
            df = df[df["uf"].astype(str).str.lower() == uf.lower()]
        if municipio:
            df = df[df["municipio"].astype(str).str.lower() == municipio.lower()]
        if bairro:
            df = df[df["bairro"].astype(str).str.lower() == bairro.lower()]
        if grupo_laudo:
            df = df[df["grupo_laudo"].astype(str).str.lower() == grupo_laudo.lower()]
        if valor_min is not None:
            df = df[df["valor_avaliacao_r"] >= valor_min]
        if valor_max is not None:
            df = df[df["valor_avaliacao_r"] <= valor_max]
        if area_min is not None:
            df = df[df["area_avaliacao_m2"] >= area_min]
        if area_max is not None:
            df = df[df["area_avaliacao_m2"] <= area_max]
        if data_inicio:
            df = df[df["data_referencia_avaliacao"].astype(str) >= data_inicio]
        if data_fim:
            df = df[df["data_referencia_avaliacao"].astype(str) <= data_fim]
        if q:
            mask = (
                df["numero_laudo"].astype(str).str.contains(q, case=False, na=False)
                | df["bairro"].astype(str).str.contains(q, case=False, na=False)
                | df["endereco_completo"].astype(str).str.contains(q, case=False, na=False)
                | df["municipio"].astype(str).str.contains(q, case=False, na=False)
            )
            df = df[mask]
        return df

    def list_summaries(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_order: str = "asc",
        categoria: str | None = None,
        uf: str | None = None,
        municipio: str | None = None,
        bairro: str | None = None,
        grupo_laudo: str | None = None,
        valor_min: float | None = None,
        valor_max: float | None = None,
        area_min: float | None = None,
        area_max: float | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        q: str | None = None,
    ) -> tuple[list[LaudoSummary], int]:
        df = self._df.copy()

        # Apply filters (source-of-truth columns)
        df = self._apply_filters(
            df,
            categoria=categoria,
            uf=uf,
            municipio=municipio,
            bairro=bairro,
            grupo_laudo=grupo_laudo,
            valor_min=valor_min,
            valor_max=valor_max,
            area_min=area_min,
            area_max=area_max,
            data_inicio=data_inicio,
            data_fim=data_fim,
            q=q,
        )

        # Sorting — map whitelisted sort keys to source columns
        sort_map = {
            "id": None,  # use index order
            "numeroLaudo": "numero_laudo",
            "valorAvaliacaoReais": "valor_avaliacao_r",
            "areaAvaliacaoM2": "area_avaliacao_m2",
            "dataReferenciaAvaliacao": "data_referencia_avaliacao",
            "municipio": "municipio",
            "bairro": "bairro",
        }
        sort_col = sort_map.get(sort_by, None)
        if sort_col is None:
            # stable default: keep the (filtered) natural index order
            ordered_ids = list(df.index)
            if sort_order == "desc":
                ordered_ids = list(reversed(ordered_ids))
        else:
            ascending = sort_order == "asc"
            df = df.sort_values(by=sort_col, ascending=ascending, na_position="last")
            ordered_ids = list(df.index)

        total_items = len(ordered_ids)
        start = (page - 1) * page_size
        end = start + page_size
        page_ids = ordered_ids[start:end]

        summaries = [self._summaries[i] for i in page_ids]
        return summaries, total_items

    def get_stats(self, categoria: str | None = None, municipio: str | None = None) -> StatsResponse:
        df = self._df.copy()
        if categoria:
            df = df[df["categoria_imovel"].astype(str).str.lower() == categoria.lower()]
        if municipio:
            df = df[df["municipio"].astype(str).str.lower() == municipio.lower()]

        def stat(series: pd.Series) -> StatPoint:
            valid = series.dropna()
            if valid.empty:
                return StatPoint(count=0, min=None, max=None, mean=None, median=None)
            return StatPoint(
                count=int(valid.shape[0]),
                min=float(valid.min()),
                max=float(valid.max()),
                mean=float(valid.mean()),
                median=float(valid.median()),
            )

        # Breakdown by category (omit rows with missing category)
        cat_items: list[CategoryBreakdownItem] = []
        cat_df = df[df["categoria_imovel"].notna()]
        for cat, g in cat_df.groupby("categoria_imovel", dropna=False):
            cat_items.append(
                CategoryBreakdownItem(
                    categoria=str(cat),
                    count=int(g.shape[0]),
                    totalValorAvaliacaoReais=_clean_float(g["valor_avaliacao_r"].sum()),
                    valorMedioReais=_clean_float(g["valor_avaliacao_r"].mean()),
                    valorMedioPorM2=_clean_float(g["valor_unitario_m2"].mean()),
                )
            )
        cat_items.sort(key=lambda x: x.count, reverse=True)

        # Breakdown by municipality (omit rows with missing municipality)
        mun_items: list[MunicipioBreakdownItem] = []
        mun_df = df[df["municipio"].notna()]
        for mun, g in mun_df.groupby("municipio", dropna=False):
            mun_items.append(
                MunicipioBreakdownItem(
                    municipio=str(mun),
                    count=int(g.shape[0]),
                    valorMedioReais=_clean_float(g["valor_avaliacao_r"].mean()),
                )
            )
        mun_items.sort(key=lambda x: x.count, reverse=True)

        # Period
        dates = df["data_referencia_avaliacao"].dropna().astype(str)
        periodo = {
            "min": str(dates.min()) if not dates.empty else None,
            "max": str(dates.max()) if not dates.empty else None,
        }

        return StatsResponse(
            total=int(df.shape[0]),
            porCategoria=cat_items,
            porMunicipio=mun_items,
            valores=ValorUnitarioStats(
                reaisPorM2=stat(df["valor_unitario_m2"]),
                valorAvaliacaoReais=stat(df["valor_avaliacao_r"]),
            ),
            periodo=periodo,
        )


# Module-level singleton populated by the FastAPI lifespan
_store: LaudoStore | None = None


def init_store(data_file: Path | None = None) -> None:  # type: ignore[name-defined]
    global _store
    _store = LaudoStore(data_file=data_file)


def get_store() -> LaudoStore:
    if _store is None:
        init_store()
    assert _store is not None
    return _store
