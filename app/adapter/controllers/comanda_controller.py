from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import build_comanda_service, get_current_session
from adapter.dtos.comanda_dto import (
    AdicionarItemComandaRequest,
    AlterarQuantidadeItemRequest,
    CancelarComandaRequest,
    ComandaDetalheResponse,
    ComandaResumoResponse,
    CriarComandaRequest,
)
from core.application.use_cases.comanda_service import ComandaService
from core.domain.enums import StatusComanda

router = APIRouter(prefix="/api/comandas", tags=["Comandas"])


def get_service(session: Session = Depends(get_current_session)) -> ComandaService:
    return build_comanda_service(session)


@router.post(
    "",
    response_model=ComandaDetalheResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_comanda(
    request: CriarComandaRequest,
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.create(
        nome_cliente=request.nome_cliente,
        observacao=request.observacao,
    )
    return ComandaDetalheResponse.from_model(comanda)


@router.get("", response_model=list[ComandaResumoResponse])
def listar_comandas(
    status_filter: Optional[StatusComanda] = Query(default=None, alias="status"),
    nome: Optional[str] = Query(default=None),
    data: Optional[date] = Query(default=None),
    service: ComandaService = Depends(get_service),
) -> list[ComandaResumoResponse]:
    comandas = service.listar(status=status_filter, nome=nome, data=data)
    return [ComandaResumoResponse.from_model(comanda) for comanda in comandas]


@router.get("/abertas", response_model=list[ComandaResumoResponse])
def listar_comandas_abertas(
    service: ComandaService = Depends(get_service),
) -> list[ComandaResumoResponse]:
    comandas = service.list_abertas()
    return [ComandaResumoResponse.from_model(comanda) for comanda in comandas]


@router.get("/{comanda_id}", response_model=ComandaDetalheResponse)
def consultar_comanda(
    comanda_id: int,
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.get_by_id(comanda_id)
    return ComandaDetalheResponse.from_model(comanda)


@router.post("/{comanda_id}/itens", response_model=ComandaDetalheResponse)
def adicionar_item(
    comanda_id: int,
    request: AdicionarItemComandaRequest,
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.adicionar_item(
        comanda_id=comanda_id,
        produto_id=request.produto_id,
        quantidade=request.quantidade,
    )
    return ComandaDetalheResponse.from_model(comanda)


@router.patch(
    "/{comanda_id}/itens/{item_id}/incrementar",
    response_model=ComandaDetalheResponse,
)
def incrementar_item(
    comanda_id: int,
    item_id: int,
    request: AlterarQuantidadeItemRequest = AlterarQuantidadeItemRequest(),
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.incrementar_item(
        comanda_id=comanda_id,
        item_id=item_id,
        quantidade=request.quantidade,
    )
    return ComandaDetalheResponse.from_model(comanda)


@router.patch(
    "/{comanda_id}/itens/{item_id}/diminuir",
    response_model=ComandaDetalheResponse,
)
def diminuir_item(
    comanda_id: int,
    item_id: int,
    request: AlterarQuantidadeItemRequest = AlterarQuantidadeItemRequest(),
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.diminuir_item(
        comanda_id=comanda_id,
        item_id=item_id,
        quantidade=request.quantidade,
    )
    return ComandaDetalheResponse.from_model(comanda)


@router.delete("/{comanda_id}/itens/{item_id}", response_model=ComandaDetalheResponse)
def remover_item(
    comanda_id: int,
    item_id: int,
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.remover_item(comanda_id=comanda_id, item_id=item_id)
    return ComandaDetalheResponse.from_model(comanda)


@router.patch("/{comanda_id}/cancelar", response_model=ComandaDetalheResponse)
def cancelar_comanda(
    comanda_id: int,
    request: CancelarComandaRequest = CancelarComandaRequest(),
    service: ComandaService = Depends(get_service),
) -> ComandaDetalheResponse:
    comanda = service.cancelar(comanda_id=comanda_id, motivo=request.motivo)
    return ComandaDetalheResponse.from_model(comanda)
