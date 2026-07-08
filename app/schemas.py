"""Pydantic schemas (the API contract) for the Laudos API.

These schemas define the public contract of the API. They intentionally favor
explicit, additive fields and consistent naming over leaking the raw 145-column
spreadsheet shape to consumers.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# -- Shared/envelope -------------------------------------------------------


class PaginationMeta(BaseModel):
    page: int = Field(..., ge=1, description="Current page number (1-indexed).")
    pageSize: int = Field(..., ge=1, description="Number of items per page.")
    totalItems: int = Field(..., ge=0, description="Total number of matching items.")
    totalPages: int = Field(..., ge=0, description="Total number of pages.")


class ErrorDetail(BaseModel):
    field: Optional[str] = Field(None, description="Field that triggered the error, when relevant.")
    message: str = Field(..., description="Human-readable error message.")
    code: str = Field(..., description="Machine-readable error code.")


class APIError(BaseModel):
    error: ErrorBody = Field(..., description="Structured error payload.")


# Helper container used by APIError
class ErrorBody(BaseModel):
    code: str = Field(..., description="Machine-readable error code, e.g. 'validation_error'.")
    message: str = Field(..., description="Human-readable error summary.")
    details: Optional[list[ErrorDetail]] = Field(
        None, description="Optional list of field-level error details."
    )


# -- Domain models ---------------------------------------------------------


class LaudoBase(BaseModel):
    """Subset of the most useful fields, shared by Laudo and LaudoSummary."""

    numeroLaudo: Optional[str] = Field(
        None, description="Unique CEF (SIMIL) report number, format AGENCIA.PREFIXO.SEQ/ANO.TEMPLATE-VERSAO."
    )
    versaoLaudo: Optional[int] = Field(None, description="Report version (1, 2, 3...).")
    modeloLaudo: Optional[str] = Field(None, description="Form model used, e.g. 'Simplificado'.")
    grupoLaudo: Optional[str] = Field(
        None,
        description="Physical type of appraised property: 'Unidade em Prédio', "
        "'Unidade Isolada Construção', 'Unidade Isolada Terreno'.",
    )
    grauSigilo: Optional[str] = Field(None, description="Classification of secrecy, e.g. 'Restrito'.")
    folhaTotal: Optional[int] = Field(None, description="Total pages of the PDF report.")


class LocationInfo(BaseModel):
    categoriaImovel: Optional[str] = Field(None, description="Property category: 'Apartamento', 'Casa', 'Lote'.")
    uf: Optional[str] = Field(None, description="Federation unit (state).", examples=["MG"])
    municipio: Optional[str] = Field(None, description="Municipality name, uppercase.")
    distritoLocalidadeCidade: Optional[str] = Field(None, description="Administrative district/locality.")
    bairro: Optional[str] = Field(None, description="Neighborhood.")
    enderecoCompleto: Optional[str] = Field(None, description="Full address text.")
    cep: Optional[str] = Field(None, description="Postal code (XX.XXX-XXX).")


class CoordinatesInfo(BaseModel):
    latitudeHemisferio: Optional[str] = Field(None, description="Latitude hemisphere, e.g. 'Sul'.")
    latitudeGraus: Optional[int] = Field(None, description="Latitude degrees.")
    latitudeMin: Optional[int] = Field(None, description="Latitude minutes.")
    latitudeSeg: Optional[float] = Field(None, description="Latitude seconds (decimal).")
    longitudeGraus: Optional[int] = Field(None, description="Longitude degrees.")
    longitudeMin: Optional[int] = Field(None, description="Longitude minutes.")
    longitudeSeg: Optional[float] = Field(None, description="Longitude seconds (decimal).")
    datum: Optional[str] = Field(None, description="Geodetic datum, e.g. 'SAD69'.")


class ValuationInfo(BaseModel):
    metodoAvaliacao: Optional[str] = Field(None, description="Appraisal method, e.g. 'Comparativo de Dados'.")
    grauFundamentacao: Optional[str] = Field(None, description="Foundation grade per NBR 14.653, e.g. 'Grau II'.")
    grauPrecisao: Optional[str] = Field(None, description="Precision grade per NBR 14.653, e.g. 'Grau III'.")
    tipoValorDeterminado: Optional[str] = Field(None, description="Type of determined value, e.g. 'Valor de Compra e Venda'.")
    dataReferenciaAvaliacao: Optional[str] = Field(None, description="Reference date (DD/MM/YYYY).")
    areaAvaliacaoM2: Optional[float] = Field(None, description="Evaluation base area, in m².")
    valorUnitarioM2: Optional[float] = Field(None, description="Unit value in R$/m².")
    valorAvaliacaoReais: Optional[float] = Field(None, description="Appraisal value in BRL (R$). Main target variable.")
    valorAvaliacaoExtenso: Optional[str] = Field(None, description="Appraisal value written out in Portuguese.")
    valorMinimoAdmissivel: Optional[float] = Field(None, description="Minimum admissible value per NBR 14.653-2 (often null).")
    valorMaximoAdmissivel: Optional[float] = Field(None, description="Maximum admissible value per NBR 14.653-2 (often null).")


class ResponsavelTecnicoInfo(BaseModel):
    nome: Optional[str] = Field(None, description="Technical responsible's full name.")
    formacao: Optional[str] = Field(None, description="Professional formation, e.g. 'ENG. CIVIL'.")
    creaCau: Optional[str] = Field(None, description="CREA/CAU registration number.")
    cpf: Optional[str] = Field(None, description="CPF of the technical responsible (sensitive).")


class EmpresaInfo(BaseModel):
    nome: Optional[str] = Field(None, description="Appraisal company name.")
    cnpj: Optional[str] = Field(None, description="Company CNPJ.")
    representanteLegalNome: Optional[str] = Field(None, description="Legal representative's name.")
    representanteLegalCpf: Optional[str] = Field(None, description="Legal representative's CPF (sensitive).")


class LaudoSummary(BaseModel):
    """Lightweight representation used in list responses."""

    id: int = Field(..., description="Internal sequential ID of the report in this dataset.")
    numeroLaudo: Optional[str] = None
    categoriaImovel: Optional[str] = None
    uf: Optional[str] = None
    municipio: Optional[str] = None
    bairro: Optional[str] = None
    dataReferenciaAvaliacao: Optional[str] = None
    valorAvaliacaoReais: Optional[float] = None
    areaAvaliacaoM2: Optional[float] = None
    arquivoPdf: Optional[str] = Field(None, description="Original PDF file name.")


class Laudo(LaudoBase):
    """Full representation of a Laudo."""

    id: int = Field(..., description="Internal sequential ID of the report in this dataset.")
    localizacao: LocationInfo = Field(..., description="Property location.")
    coordenadas: CoordinatesInfo = Field(..., description="Geographic coordinates.")
    cadMunicipal: Optional[float] = Field(None, description="Municipal cadastre code.")
    finalidade: Optional[str] = Field(None, description="Purpose of the appraisal.")
    objetivo: Optional[str] = Field(None, description="Objective of the appraisal.")
    interessado: Optional[str] = Field(None, description="Interested party.")
    avaliacao: ValuationInfo = Field(..., description="Valuation results.")
    responsavelTecnico: ResponsavelTecnicoInfo = Field(..., description="Technical responsible.")
    empresa: EmpresaInfo = Field(..., description="Appraisal company.")
    dataAssinatura: Optional[str] = Field(None, description="Signing date (DD/MM/YYYY).")
    matriculaImovel: Optional[str] = Field(None, description="Property registry record.")
    cnmImovel: Optional[str] = Field(None, description="National Registry Code (CNM).")
    informacoesComplementares: Optional[str] = Field(None, description="Free-text complementary information.")
    arquivoPdf: Optional[str] = Field(None, description="Original PDF file name.")


class PaginatedLaudos(BaseModel):
    data: list[LaudoSummary] = Field(..., description="List of laudo summaries for the current page.")
    pagination: PaginationMeta = Field(..., description="Pagination metadata.")


# -- Statistics ------------------------------------------------------------


class StatPoint(BaseModel):
    count: int = Field(..., description="Number of items considered.")
    min: Optional[float] = Field(None, description="Minimum value.")
    max: Optional[float] = Field(None, description="Maximum value.")
    mean: Optional[float] = Field(None, description="Arithmetic mean.")
    median: Optional[float] = Field(None, description="Median value.")


class ValorUnitarioStats(BaseModel):
    reaisPorM2: StatPoint = Field(..., description="Statistics for valor_unitario_m2 (R$/m²).")
    valorAvaliacaoReais: StatPoint = Field(..., description="Statistics for valor_avaliacao_r (R$).")


class CategoryBreakdownItem(BaseModel):
    categoria: str = Field(..., description="Property category.")
    count: int = Field(..., description="Number of reports in this category.")
    totalValorAvaliacaoReais: Optional[float] = Field(None, description="Sum of appraisal values in BRL.")
    valorMedioReais: Optional[float] = Field(None, description="Mean appraisal value in BRL.")
    valorMedioPorM2: Optional[float] = Field(None, description="Mean unit value (R$/m²).")


class MunicipioBreakdownItem(BaseModel):
    municipio: str = Field(..., description="Municipality name.")
    count: int = Field(..., description="Number of reports in this municipality.")
    valorMedioReais: Optional[float] = Field(None, description="Mean appraisal value in BRL.")


class StatsResponse(BaseModel):
    total: int = Field(..., description="Total number of reports.")
    porCategoria: list[CategoryBreakdownItem] = Field(..., description="Breakdown by property category.")
    porMunicipio: list[MunicipioBreakdownItem] = Field(..., description="Breakdown by municipality.")
    valores: ValorUnitarioStats = Field(..., description="Aggregate valuation statistics.")
    periodo: dict[str, Optional[str]] = Field(..., description="Min/max reference dates of the dataset.")


# -- Health ----------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str = Field(..., description="'ok' when the service is healthy.")
    version: str = Field(..., description="API version.")
    reportsLoaded: int = Field(..., description="Number of reports loaded in memory.")


class InfoResponse(BaseModel):
    name: str = Field(..., description="API name.")
    version: str = Field(..., description="API version.")
    description: str = Field(..., description="Short description of the API.")
    totalReports: int = Field(..., description="Total reports available.")
    totalColumns: int = Field(..., description="Total columns in the source dataset.")
    sourceFile: str = Field(..., description="Name of the source data file.")
    coverage: str = Field(..., description="Geographic coverage.")
    author: str = Field(..., description="Author of the dataset.")
    endpoints: list[str] = Field(..., description="List of available endpoint paths.")
