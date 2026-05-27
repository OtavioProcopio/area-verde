from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import build_fiado_service, get_current_session
from adapter.dtos.fiado_dto import (
    MarcarFiadoRequest,
    PendenciaDetalheResponse,
    PendenciaResumoResponse,
    QuitarFiadoRequest,
    QuitarFiadoResponse,
)
from core.application.use_cases.fiado_service import FiadoService

router = APIRouter(tags=["Fiado / Pendências"])


def get_service(session: Session = Depends(get_current_session)) -> FiadoService:
    return build_fiado_service(session)


@router.post(
    "/api/comandas/{comanda_id}/fiado",
    response_model=PendenciaDetalheResponse,
    status_code=status.HTTP_200_OK,
)
def marcar_comanda_como_fiado(
    comanda_id: int,
    request: MarcarFiadoRequest,
    service: FiadoService = Depends(get_service),
) -> PendenciaDetalheResponse:
    comanda = service.marcar_fiado(
        comanda_id=comanda_id,
        cliente_id=request.cliente_id,
        vencimento_em=request.vencimento_em,
        observacao=request.observacao,
    )
    return PendenciaDetalheResponse.from_model(comanda)


@router.get("/api/fiados", response_model=list[PendenciaResumoResponse])
def listar_fiados(
    cliente_id: Optional[int] = Query(default=None, alias="clienteId"),
    vencidos: Optional[bool] = Query(default=None),
    data_inicio: Optional[date] = Query(default=None, alias="dataInicio"),
    data_fim: Optional[date] = Query(default=None, alias="dataFim"),
    nome: Optional[str] = Query(default=None),
    service: FiadoService = Depends(get_service),
) -> list[PendenciaResumoResponse]:
    pendencias = service.listar_pendencias(
        cliente_id=cliente_id,
        vencidos=vencidos,
        data_inicio=data_inicio,
        data_fim=data_fim,
        nome=nome,
    )
    return [PendenciaResumoResponse.from_model(comanda) for comanda in pendencias]


@router.get("/api/fiados/vencidos", response_model=list[PendenciaResumoResponse])
def listar_fiados_vencidos(
    service: FiadoService = Depends(get_service),
) -> list[PendenciaResumoResponse]:
    return [
        PendenciaResumoResponse.from_model(comanda)
        for comanda in service.listar_vencidas()
    ]


@router.get("/api/fiados/{comanda_id}", response_model=PendenciaDetalheResponse)
def consultar_fiado(
    comanda_id: int,
    service: FiadoService = Depends(get_service),
) -> PendenciaDetalheResponse:
    return PendenciaDetalheResponse.from_model(service.consultar_pendencia(comanda_id))


@router.post(
    "/api/fiados/{comanda_id}/quitar",
    response_model=QuitarFiadoResponse,
    status_code=status.HTTP_200_OK,
)
def quitar_fiado(
    comanda_id: int,
    request: QuitarFiadoRequest,
    service: FiadoService = Depends(get_service),
) -> QuitarFiadoResponse:
    result = service.quitar(
        comanda_id=comanda_id,
        forma_pagamento=request.forma_pagamento,
        valor_pago=request.valor_pago,
        observacao=request.observacao,
    )
    return QuitarFiadoResponse.from_model(
        comanda=result.comanda,
        pagamentos=result.pagamentos,
    )
