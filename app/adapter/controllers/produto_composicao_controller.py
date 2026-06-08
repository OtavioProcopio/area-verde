from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from adapter.controllers.dependencies import (
    build_produto_composicao_service,
    build_produto_service,
    get_current_session,
)
from adapter.dtos.produto_composicao_dto import (
    ProdutoComposicaoCreateRequest,
    ProdutoComposicaoResponse,
    ProdutoComposicaoUpdateRequest,
    ProdutoCompostoCreateRequest,
    ProdutoCompostoResponse,
)
from core.application.use_cases.produto_composicao_service import (
    ComponenteCompostoInput,
    ProdutoComposicaoService,
)
from core.application.use_cases.produto_service import ProdutoService

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])


def get_service(
    session: Session = Depends(get_current_session),
) -> ProdutoComposicaoService:
    return build_produto_composicao_service(session)


def get_produto_service(
    session: Session = Depends(get_current_session),
) -> ProdutoService:
    return build_produto_service(session)


@router.post(
    "/compostos",
    response_model=ProdutoCompostoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_produto_composto(
    request: ProdutoCompostoCreateRequest,
    service: ProdutoComposicaoService = Depends(get_service),
) -> ProdutoCompostoResponse:
    produto, composicoes = service.create_composto(
        nome=request.nome,
        categoria_id=request.categoria_id,
        preco_venda=request.preco_venda,
        controla_estoque=request.controla_estoque,
        unidade_estoque=request.unidade_estoque,
        quantidade_estoque=request.quantidade_estoque,
        quantidade_baixa_por_venda=request.quantidade_baixa_por_venda,
        estoque_minimo=request.estoque_minimo,
        componentes=[
            ComponenteCompostoInput(
                produto_componente_id=item.produto_componente_id,
                quantidade_baixa=item.quantidade_baixa,
            )
            for item in request.componentes
        ],
    )
    return ProdutoCompostoResponse.from_models(produto, composicoes)


@router.get("/{produto_id}/composicao", response_model=ProdutoComposicaoResponse)
def get_composicao(
    produto_id: int,
    service: ProdutoComposicaoService = Depends(get_service),
    produto_service: ProdutoService = Depends(get_produto_service),
) -> ProdutoComposicaoResponse:
    produto = produto_service.get_by_id(produto_id)
    composicoes = service.list_by_parent(produto_id)
    return ProdutoComposicaoResponse.from_models(produto, composicoes)


@router.post(
    "/{produto_id}/composicao/componentes",
    response_model=ProdutoComposicaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_componente(
    produto_id: int,
    request: ProdutoComposicaoCreateRequest,
    service: ProdutoComposicaoService = Depends(get_service),
    produto_service: ProdutoService = Depends(get_produto_service),
) -> ProdutoComposicaoResponse:
    service.add_componente(
        produto_pai_id=produto_id,
        produto_componente_id=request.produto_componente_id,
        quantidade_baixa=request.quantidade_baixa,
    )
    produto = produto_service.get_by_id(produto_id)
    composicoes = service.list_by_parent(produto_id)
    return ProdutoComposicaoResponse.from_models(produto, composicoes)


@router.put(
    "/{produto_id}/composicao/componentes/{componente_id}",
    response_model=ProdutoComposicaoResponse,
)
def update_componente(
    produto_id: int,
    componente_id: int,
    request: ProdutoComposicaoUpdateRequest,
    service: ProdutoComposicaoService = Depends(get_service),
    produto_service: ProdutoService = Depends(get_produto_service),
) -> ProdutoComposicaoResponse:
    service.update_componente(
        produto_pai_id=produto_id,
        produto_componente_id=componente_id,
        quantidade_baixa=request.quantidade_baixa,
    )
    produto = produto_service.get_by_id(produto_id)
    composicoes = service.list_by_parent(produto_id)
    return ProdutoComposicaoResponse.from_models(produto, composicoes)


@router.delete(
    "/{produto_id}/composicao/componentes/{componente_id}",
    response_model=ProdutoComposicaoResponse,
)
def delete_componente(
    produto_id: int,
    componente_id: int,
    service: ProdutoComposicaoService = Depends(get_service),
    produto_service: ProdutoService = Depends(get_produto_service),
) -> ProdutoComposicaoResponse:
    service.delete_componente(
        produto_pai_id=produto_id,
        produto_componente_id=componente_id,
    )
    produto = produto_service.get_by_id(produto_id)
    composicoes = service.list_by_parent(produto_id)
    return ProdutoComposicaoResponse.from_models(produto, composicoes)
