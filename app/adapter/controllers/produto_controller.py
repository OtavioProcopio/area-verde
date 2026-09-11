from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import build_produto_service, get_current_session
from adapter.dtos.produto_dto import ProdutoRequest, ProdutoResponse
from core.application.use_cases.produto_service import ProdutoService

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])


def get_service(session: Session = Depends(get_current_session)) -> ProdutoService:
    return build_produto_service(session)


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def create_produto(
    request: ProdutoRequest,
    service: ProdutoService = Depends(get_service),
) -> ProdutoResponse:
    produto = service.create(
        nome=request.nome,
        categoria_id=request.categoria_id,
        preco_venda=request.preco_venda,
        tipo_produto=request.tipo_produto,
        controla_estoque=request.controla_estoque,
        unidade_estoque=request.unidade_estoque,
        quantidade_estoque=request.quantidade_estoque,
        quantidade_baixa_por_venda=request.quantidade_baixa_por_venda,
        estoque_minimo=request.estoque_minimo,
    )
    return ProdutoResponse.from_model(produto)


@router.get("", response_model=list[ProdutoResponse])
def list_produtos(
    ativo: Optional[bool] = Query(default=None),
    categoria_id: Optional[int] = Query(default=None, alias="categoriaId"),
    nome: Optional[str] = Query(default=None),
    service: ProdutoService = Depends(get_service),
) -> list[ProdutoResponse]:
    produtos = service.list(
        ativo=ativo,
        categoria_id=categoria_id,
        nome=nome,
    )
    return [ProdutoResponse.from_model(produto) for produto in produtos]


@router.get("/{produto_id}", response_model=ProdutoResponse)
def get_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_service),
) -> ProdutoResponse:
    produto = service.get_by_id(produto_id)
    return ProdutoResponse.from_model(produto)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def update_produto(
    produto_id: int,
    request: ProdutoRequest,
    service: ProdutoService = Depends(get_service),
) -> ProdutoResponse:
    produto = service.update(
        produto_id=produto_id,
        nome=request.nome,
        categoria_id=request.categoria_id,
        preco_venda=request.preco_venda,
        tipo_produto=request.tipo_produto,
        controla_estoque=request.controla_estoque,
        unidade_estoque=request.unidade_estoque,
        quantidade_estoque=request.quantidade_estoque,
        quantidade_baixa_por_venda=request.quantidade_baixa_por_venda,
        estoque_minimo=request.estoque_minimo,
    )
    return ProdutoResponse.from_model(produto)


@router.patch("/{produto_id}/ativar", response_model=ProdutoResponse)
def activate_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_service),
) -> ProdutoResponse:
    produto = service.activate(produto_id)
    return ProdutoResponse.from_model(produto)


@router.patch("/{produto_id}/inativar", response_model=ProdutoResponse)
def deactivate_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_service),
) -> ProdutoResponse:
    produto = service.deactivate(produto_id)
    return ProdutoResponse.from_model(produto)
