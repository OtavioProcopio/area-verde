from decimal import Decimal

from fastapi import FastAPI
from sqlalchemy import inspect

from api import create_app
from core.domain.enums import StatusCaixa, StatusComanda, UnidadeEstoque
from core.domain.models import Caixa, Comanda, Produto


def test_create_app_without_real_database():
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "Area Verde API"


def test_sqlmodel_schema_can_be_created(test_engine):
    inspector = inspect(test_engine)

    assert {
        "configuracao_sistema",
        "categoria_produto",
        "produto",
        "comanda",
        "item_comanda",
        "caixa",
        "pagamento",
        "movimento_caixa",
        "movimento_estoque",
    }.issubset(set(inspector.get_table_names()))


def test_domain_defaults_match_mvp():
    produto = Produto(nome="Cerveja", preco_venda=Decimal("12.00"))
    comanda = Comanda(nome_cliente="Mesa 1")
    caixa = Caixa()

    assert produto.controla_estoque is True
    assert produto.unidade_estoque == UnidadeEstoque.UNIDADE
    assert comanda.status == StatusComanda.ABERTA
    assert caixa.status == StatusCaixa.ABERTO


def test_container_provides_engine_and_logger(test_container):
    logger = test_container.logger()
    engine = test_container.engine()

    logger.info("Container test")

    assert engine.url.database == ":memory:"
    assert hasattr(logger, "info")
