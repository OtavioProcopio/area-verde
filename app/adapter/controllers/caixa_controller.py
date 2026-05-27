from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import build_caixa_service, get_current_session
from adapter.dtos.caixa_dto import (
    AbrirCaixaRequest,
    CaixaDetalheResponse,
    CaixaResumoResponse,
    FecharCaixaRequest,
    MovimentoCaixaRequest,
)
from core.application.use_cases.caixa_service import CaixaService
from core.domain.enums import StatusCaixa

router = APIRouter(prefix="/api/caixas", tags=["Caixa Diário"])


@router.post(
    "/abrir",
    response_model=CaixaDetalheResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Abre o caixa diário",
)
def abrir_caixa(
    request: AbrirCaixaRequest,
    session: Session = Depends(get_current_session),
) -> CaixaDetalheResponse:
    service: CaixaService = build_caixa_service(session)
    caixa = service.abrir_caixa(
        valor_inicial=request.valor_inicial,
        observacao=request.observacao,
    )
    return CaixaDetalheResponse.from_model(caixa)


@router.get(
    "/aberto",
    response_model=CaixaDetalheResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta o caixa aberto",
)
def get_caixa_aberto(
    session: Session = Depends(get_current_session),
) -> CaixaDetalheResponse:
    service: CaixaService = build_caixa_service(session)
    return CaixaDetalheResponse.from_model(service.get_caixa_aberto())


@router.get(
    "",
    response_model=List[CaixaResumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Lista caixas",
)
def listar_caixas(
    status_caixa: Optional[StatusCaixa] = Query(default=None, alias="status"),
    data: Optional[date] = None,
    session: Session = Depends(get_current_session),
) -> List[CaixaResumoResponse]:
    service: CaixaService = build_caixa_service(session)
    caixas = service.listar_caixas(status=status_caixa, data=data)
    return [CaixaResumoResponse.from_model(caixa) for caixa in caixas]


@router.get(
    "/{caixa_id}",
    response_model=CaixaDetalheResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulta caixa por ID",
)
def get_caixa_by_id(
    caixa_id: int,
    session: Session = Depends(get_current_session),
) -> CaixaDetalheResponse:
    service: CaixaService = build_caixa_service(session)
    return CaixaDetalheResponse.from_model(service.get_by_id(caixa_id))


@router.post(
    "/{caixa_id}/reforcos",
    response_model=CaixaDetalheResponse,
    status_code=status.HTTP_200_OK,
    summary="Registra reforço de caixa",
)
def registrar_reforco(
    caixa_id: int,
    request: MovimentoCaixaRequest,
    session: Session = Depends(get_current_session),
) -> CaixaDetalheResponse:
    service: CaixaService = build_caixa_service(session)
    caixa = service.registrar_reforco(
        caixa_id=caixa_id,
        valor=request.valor,
        observacao=request.observacao,
    )
    return CaixaDetalheResponse.from_model(caixa)


@router.post(
    "/{caixa_id}/sangrias",
    response_model=CaixaDetalheResponse,
    status_code=status.HTTP_200_OK,
    summary="Registra sangria de caixa",
)
def registrar_sangria(
    caixa_id: int,
    request: MovimentoCaixaRequest,
    session: Session = Depends(get_current_session),
) -> CaixaDetalheResponse:
    service: CaixaService = build_caixa_service(session)
    caixa = service.registrar_sangria(
        caixa_id=caixa_id,
        valor=request.valor,
        observacao=request.observacao,
    )
    return CaixaDetalheResponse.from_model(caixa)


@router.post(
    "/{caixa_id}/fechar",
    response_model=CaixaDetalheResponse,
    status_code=status.HTTP_200_OK,
    summary="Fecha o caixa diário",
)
def fechar_caixa(
    caixa_id: int,
    request: FecharCaixaRequest,
    session: Session = Depends(get_current_session),
) -> CaixaDetalheResponse:
    service: CaixaService = build_caixa_service(session)
    caixa = service.fechar_caixa(
        caixa_id=caixa_id,
        dinheiro_informado=request.dinheiro_informado,
        observacao=request.observacao,
    )
    return CaixaDetalheResponse.from_model(caixa)
