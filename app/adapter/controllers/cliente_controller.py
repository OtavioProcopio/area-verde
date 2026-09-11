from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import build_cliente_service, get_current_session
from adapter.dtos.cliente_dto import (
    ClienteDetalheResponse,
    ClientePendenciasResponse,
    ClienteRequest,
    ClienteResumoResponse,
)
from core.application.use_cases.cliente_service import ClienteService

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


def get_service(session: Session = Depends(get_current_session)) -> ClienteService:
    return build_cliente_service(session)


@router.post(
    "",
    response_model=ClienteDetalheResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_cliente(
    request: ClienteRequest,
    service: ClienteService = Depends(get_service),
) -> ClienteDetalheResponse:
    cliente = service.create(
        nome=request.nome,
        apelido=request.apelido,
        telefone=request.telefone,
        observacao=request.observacao,
    )
    return ClienteDetalheResponse.from_model(cliente)


@router.get("", response_model=list[ClienteResumoResponse])
def listar_clientes(
    ativo: Optional[bool] = Query(default=None),
    nome: Optional[str] = Query(default=None),
    telefone: Optional[str] = Query(default=None),
    service: ClienteService = Depends(get_service),
) -> list[ClienteResumoResponse]:
    clientes = service.listar(ativo=ativo, nome=nome, telefone=telefone)
    return [ClienteResumoResponse.from_model(cliente) for cliente in clientes]


@router.get("/{cliente_id}", response_model=ClienteDetalheResponse)
def consultar_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_service),
) -> ClienteDetalheResponse:
    return ClienteDetalheResponse.from_model(service.get_by_id(cliente_id))


@router.put("/{cliente_id}", response_model=ClienteDetalheResponse)
def editar_cliente(
    cliente_id: int,
    request: ClienteRequest,
    service: ClienteService = Depends(get_service),
) -> ClienteDetalheResponse:
    cliente = service.update(
        cliente_id=cliente_id,
        nome=request.nome,
        apelido=request.apelido,
        telefone=request.telefone,
        observacao=request.observacao,
    )
    return ClienteDetalheResponse.from_model(cliente)


@router.patch("/{cliente_id}/ativar", response_model=ClienteDetalheResponse)
def ativar_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_service),
) -> ClienteDetalheResponse:
    return ClienteDetalheResponse.from_model(service.ativar(cliente_id))


@router.patch("/{cliente_id}/inativar", response_model=ClienteDetalheResponse)
def inativar_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_service),
) -> ClienteDetalheResponse:
    return ClienteDetalheResponse.from_model(service.inativar(cliente_id))


@router.get("/{cliente_id}/pendencias", response_model=ClientePendenciasResponse)
def listar_pendencias_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_service),
) -> ClientePendenciasResponse:
    cliente = service.get_by_id(cliente_id)
    pendencias = service.listar_pendencias(cliente_id)
    return ClientePendenciasResponse.from_model(
        cliente=cliente,
        pendencias=pendencias,
        total_pendente=service.total_pendente(cliente_id),
        total_vencido=service.total_vencido(cliente_id),
    )
