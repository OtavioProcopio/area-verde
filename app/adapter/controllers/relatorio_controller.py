from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import (
    build_relatorio_service,
    get_current_session,
)
from adapter.dtos.relatorio_dto import (
    EstoqueConsumidoResponse,
    ProdutoMaisVendidoResponse,
    RelatorioCaixaResponse,
    RelatorioComandasResponse,
    RelatorioDiarioResponse,
    RelatorioEstoqueResponse,
    RelatorioFiadosResponse,
)
from core.application.use_cases.relatorio_service import RelatorioService
from core.domain.enums import StatusComanda

router = APIRouter(prefix="/api/relatorios", tags=["Relatórios"])


def get_service(session: Session = Depends(get_current_session)) -> RelatorioService:
    return build_relatorio_service(session)


@router.get(
    "/diario",
    response_model=RelatorioDiarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta relatório diário",
)
def relatorio_diario(
    data: Optional[date] = Query(default=None),
    service: RelatorioService = Depends(get_service),
) -> RelatorioDiarioResponse:
    return RelatorioDiarioResponse.from_result(service.relatorio_diario(data=data))


@router.get(
    "/caixas/{caixa_id}",
    response_model=RelatorioCaixaResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta relatório por caixa",
)
def relatorio_caixa(
    caixa_id: int,
    service: RelatorioService = Depends(get_service),
) -> RelatorioCaixaResponse:
    return RelatorioCaixaResponse.from_result(service.relatorio_caixa(caixa_id))


@router.get(
    "/produtos-mais-vendidos",
    response_model=list[ProdutoMaisVendidoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista produtos mais vendidos",
)
def produtos_mais_vendidos(
    data_inicio: Optional[date] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[date] = Query(default=None, alias="dataFim"),
    limite: int = Query(default=10),
    service: RelatorioService = Depends(get_service),
) -> list[ProdutoMaisVendidoResponse]:
    produtos = service.produtos_mais_vendidos(
        data_inicio=data_inicio,
        data_fim=data_fim,
        limite=limite,
    )
    return [ProdutoMaisVendidoResponse.from_result(item) for item in produtos]


@router.get(
    "/fiados",
    response_model=RelatorioFiadosResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta relatório de fiados",
)
def relatorio_fiados(
    status_fiado: str = Query(default="todos", alias="status"),
    cliente_id: Optional[int] = Query(default=None, alias="clienteId"),
    data_inicio: Optional[date] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[date] = Query(default=None, alias="dataFim"),
    service: RelatorioService = Depends(get_service),
) -> RelatorioFiadosResponse:
    return RelatorioFiadosResponse.from_result(
        service.relatorio_fiados(
            status=status_fiado,
            cliente_id=cliente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
    )


@router.get(
    "/estoque",
    response_model=RelatorioEstoqueResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta relatório de estoque",
)
def relatorio_estoque(
    tipo: str = Query(default="todos"),
    service: RelatorioService = Depends(get_service),
) -> RelatorioEstoqueResponse:
    return RelatorioEstoqueResponse.from_result(service.relatorio_estoque(tipo=tipo))


@router.get(
    "/estoque-consumido",
    response_model=list[EstoqueConsumidoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista consumo de estoque por produto",
)
def estoque_consumido(
    data_inicio: Optional[date] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[date] = Query(default=None, alias="dataFim"),
    service: RelatorioService = Depends(get_service),
) -> list[EstoqueConsumidoResponse]:
    consumidos = service.estoque_consumido(
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return [EstoqueConsumidoResponse.from_result(item) for item in consumidos]


@router.get(
    "/comandas",
    response_model=RelatorioComandasResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta relatório de comandas",
)
def relatorio_comandas(
    data_inicio: Optional[date] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[date] = Query(default=None, alias="dataFim"),
    status_comanda: Optional[StatusComanda] = Query(default=None, alias="status"),
    service: RelatorioService = Depends(get_service),
) -> RelatorioComandasResponse:
    return RelatorioComandasResponse.from_result(
        service.relatorio_comandas(
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status_comanda,
        )
    )
