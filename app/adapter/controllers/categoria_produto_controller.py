from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from adapter.controllers.dependencies import (
    build_categoria_produto_service,
    get_current_session,
)
from adapter.dtos.categoria_produto_dto import (
    CategoriaProdutoRequest,
    CategoriaProdutoResponse,
)
from core.application.use_cases.categoria_produto_service import (
    CategoriaProdutoService,
)

router = APIRouter(prefix="/api/categorias", tags=["Categorias"])


def get_service(
    session: Session = Depends(get_current_session),
) -> CategoriaProdutoService:
    return build_categoria_produto_service(session)


@router.post(
    "",
    response_model=CategoriaProdutoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_categoria(
    request: CategoriaProdutoRequest,
    service: CategoriaProdutoService = Depends(get_service),
) -> CategoriaProdutoResponse:
    categoria = service.create(nome=request.nome)
    return CategoriaProdutoResponse.from_model(categoria)


@router.get("", response_model=list[CategoriaProdutoResponse])
def list_categorias(
    ativo: Optional[bool] = Query(default=None),
    service: CategoriaProdutoService = Depends(get_service),
) -> list[CategoriaProdutoResponse]:
    categorias = service.list(ativo=ativo)
    return [CategoriaProdutoResponse.from_model(categoria) for categoria in categorias]


@router.get("/{categoria_id}", response_model=CategoriaProdutoResponse)
def get_categoria(
    categoria_id: int,
    service: CategoriaProdutoService = Depends(get_service),
) -> CategoriaProdutoResponse:
    categoria = service.get_by_id(categoria_id)
    return CategoriaProdutoResponse.from_model(categoria)


@router.put("/{categoria_id}", response_model=CategoriaProdutoResponse)
def update_categoria(
    categoria_id: int,
    request: CategoriaProdutoRequest,
    service: CategoriaProdutoService = Depends(get_service),
) -> CategoriaProdutoResponse:
    categoria = service.update(categoria_id=categoria_id, nome=request.nome)
    return CategoriaProdutoResponse.from_model(categoria)


@router.patch("/{categoria_id}/ativar", response_model=CategoriaProdutoResponse)
def activate_categoria(
    categoria_id: int,
    service: CategoriaProdutoService = Depends(get_service),
) -> CategoriaProdutoResponse:
    categoria = service.activate(categoria_id)
    return CategoriaProdutoResponse.from_model(categoria)


@router.patch("/{categoria_id}/inativar", response_model=CategoriaProdutoResponse)
def deactivate_categoria(
    categoria_id: int,
    service: CategoriaProdutoService = Depends(get_service),
) -> CategoriaProdutoResponse:
    categoria = service.deactivate(categoria_id)
    return CategoriaProdutoResponse.from_model(categoria)
