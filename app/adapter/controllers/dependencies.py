from fastapi import Request
from sqlmodel import Session

from adapter.repositories.caixa_repository import CaixaRepository
from adapter.repositories.categoria_produto_repository import (
    CategoriaProdutoRepository,
)
from adapter.repositories.cliente_repository import ClienteRepository
from adapter.repositories.comanda_repository import ComandaRepository
from adapter.repositories.movimento_estoque_repository import MovimentoEstoqueRepository
from adapter.repositories.pagamento_repository import PagamentoRepository
from adapter.repositories.produto_composicao_repository import (
    ProdutoComposicaoRepository,
)
from adapter.repositories.produto_repository import ProdutoRepository
from adapter.repositories.relatorio_repository import RelatorioRepository
from core.application.use_cases.caixa_service import CaixaService
from core.application.use_cases.categoria_produto_service import (
    CategoriaProdutoService,
)
from core.application.use_cases.cliente_service import ClienteService
from core.application.use_cases.comanda_service import ComandaService
from core.application.use_cases.estoque_service import EstoqueService
from core.application.use_cases.fiado_service import FiadoService
from core.application.use_cases.pagamento_service import PagamentoService
from core.application.use_cases.produto_composicao_service import (
    ProdutoComposicaoService,
)
from core.application.use_cases.produto_service import ProdutoService
from core.application.use_cases.relatorio_service import RelatorioService
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


def build_produto_composicao_service(session: Session) -> ProdutoComposicaoService:
    produto_repository = ProdutoRepository(session)
    composicao_repository = ProdutoComposicaoRepository(session)
    return ProdutoComposicaoService(
        produto_repository=produto_repository,
        composicao_repository=composicao_repository,
    )


def build_estoque_service(session: Session) -> EstoqueService:
    produto_repository = ProdutoRepository(session)
    movimento_repository = MovimentoEstoqueRepository(session)
    return EstoqueService(
        produto_repository=produto_repository,
        movimento_repository=movimento_repository,
    )


def build_caixa_service(session: Session) -> CaixaService:
    caixa_repository = CaixaRepository(session)
    comanda_repository = ComandaRepository(session)
    return CaixaService(
        caixa_repository=caixa_repository,
        comanda_repository=comanda_repository,
    )


def build_cliente_service(session: Session) -> ClienteService:
    cliente_repository = ClienteRepository(session)
    comanda_repository = ComandaRepository(session)
    return ClienteService(
        cliente_repository=cliente_repository,
        comanda_repository=comanda_repository,
    )


def build_comanda_service(session: Session) -> ComandaService:
    comanda_repository = ComandaRepository(session)
    cliente_repository = ClienteRepository(session)
    caixa_repository = CaixaRepository(session)
    produto_repository = ProdutoRepository(session)
    movimento_repository = MovimentoEstoqueRepository(session)
    estoque_service = EstoqueService(
        produto_repository=produto_repository,
        movimento_repository=movimento_repository,
    )
    return ComandaService(
        comanda_repository=comanda_repository,
        produto_repository=produto_repository,
        estoque_service=estoque_service,
        cliente_repository=cliente_repository,
        caixa_repository=caixa_repository,
    )


def build_pagamento_service(session: Session) -> PagamentoService:
    pagamento_repository = PagamentoRepository(session)
    comanda_repository = ComandaRepository(session)
    caixa_service = build_caixa_service(session)
    return PagamentoService(
        pagamento_repository=pagamento_repository,
        comanda_repository=comanda_repository,
        caixa_service=caixa_service,
    )


def build_fiado_service(session: Session) -> FiadoService:
    pagamento_repository = PagamentoRepository(session)
    comanda_repository = ComandaRepository(session)
    cliente_repository = ClienteRepository(session)
    caixa_service = build_caixa_service(session)
    return FiadoService(
        pagamento_repository=pagamento_repository,
        comanda_repository=comanda_repository,
        cliente_repository=cliente_repository,
        caixa_service=caixa_service,
    )


def build_relatorio_service(session: Session) -> RelatorioService:
    relatorio_repository = RelatorioRepository(session)
    return RelatorioService(relatorio_repository)
