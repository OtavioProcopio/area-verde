from fastapi import Request
from sqlmodel import Session

from adapter.repositories.categoria_produto_repository import (
    CategoriaProdutoRepository,
)
from adapter.repositories.movimento_estoque_repository import MovimentoEstoqueRepository
from adapter.repositories.produto_repository import ProdutoRepository
from core.application.use_cases.categoria_produto_service import (
    CategoriaProdutoService,
)
from core.application.use_cases.estoque_service import EstoqueService
from core.application.use_cases.produto_service import ProdutoService
from infra.config.context import db_session_context


def get_current_session(request: Request) -> Session:
    session = db_session_context.get()
    if session is not None:
        return session

    return request.app.container.db_session()  # type: ignore[attr-defined]


def build_categoria_produto_service(session: Session) -> CategoriaProdutoService:
    repository = CategoriaProdutoRepository(session)
    return CategoriaProdutoService(repository)


def build_produto_service(session: Session) -> ProdutoService:
    categoria_repository = CategoriaProdutoRepository(session)
    produto_repository = ProdutoRepository(session)
    return ProdutoService(
        produto_repository=produto_repository,
        categoria_repository=categoria_repository,
    )


def build_estoque_service(session: Session) -> EstoqueService:
    produto_repository = ProdutoRepository(session)
    movimento_repository = MovimentoEstoqueRepository(session)
    return EstoqueService(
        produto_repository=produto_repository,
        movimento_repository=movimento_repository,
    )
