from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import build_estoque_service, get_current_session
from adapter.dtos.estoque_dto import (
    AjusteEstoqueRequest,
    EntradaEstoqueRequest,
    EstoqueProdutoResponse,
    MovimentoEstoqueResponse,
)
from core.application.use_cases.estoque_service import EstoqueService

router = APIRouter(prefix="/api/estoque", tags=["Estoque"])


def get_service(session: Session = Depends(get_current_session)) -> EstoqueService:
    return build_estoque_service(session)


@router.get("", response_model=list[EstoqueProdutoResponse])
def list_estoque(
    ativo: Optional[bool] = Query(default=None),
    categoria_id: Optional[int] = Query(default=None, alias="categoriaId"),
    nome: Optional[str] = Query(default=None),
    service: EstoqueService = Depends(get_service),
) -> list[EstoqueProdutoResponse]:
    produtos = service.list(
        ativo=ativo,
        categoria_id=categoria_id,
        nome=nome,
    )
    return [EstoqueProdutoResponse.from_model(produto) for produto in produtos]


@router.get("/baixo", response_model=list[EstoqueProdutoResponse])
def list_estoque_baixo(
    service: EstoqueService = Depends(get_service),
) -> list[EstoqueProdutoResponse]:
    produtos = service.list_baixo()
    return [EstoqueProdutoResponse.from_model(produto) for produto in produtos]


@router.get("/negativo", response_model=list[EstoqueProdutoResponse])
def list_estoque_negativo(
    service: EstoqueService = Depends(get_service),
) -> list[EstoqueProdutoResponse]:
    produtos = service.list_negativo()
    return [EstoqueProdutoResponse.from_model(produto) for produto in produtos]


@router.get(
    "/produtos/{produto_id}/movimentos",
    response_model=list[MovimentoEstoqueResponse],
)
def list_movimentos_produto(
    produto_id: int,
    service: EstoqueService = Depends(get_service),
) -> list[MovimentoEstoqueResponse]:
    movimentos = service.list_movimentos(produto_id)
    return [MovimentoEstoqueResponse.from_model(movimento) for movimento in movimentos]


@router.post(
    "/produtos/{produto_id}/entrada",
    response_model=MovimentoEstoqueResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_entrada(
    produto_id: int,
    request: EntradaEstoqueRequest,
    service: EstoqueService = Depends(get_service),
) -> MovimentoEstoqueResponse:
    movimento = service.adicionar_entrada(
        produto_id=produto_id,
        quantidade=request.quantidade,
        observacao=request.observacao,
    )
    return MovimentoEstoqueResponse.from_model(movimento)


@router.post(
    "/produtos/{produto_id}/ajuste",
    response_model=MovimentoEstoqueResponse,
    status_code=status.HTTP_201_CREATED,
)
def ajustar_estoque(
    produto_id: int,
    request: AjusteEstoqueRequest,
    service: EstoqueService = Depends(get_service),
) -> MovimentoEstoqueResponse:
    movimento = service.ajustar(
        produto_id=produto_id,
        novo_estoque=request.novo_estoque,
        observacao=request.observacao,
    )
    return MovimentoEstoqueResponse.from_model(movimento)
