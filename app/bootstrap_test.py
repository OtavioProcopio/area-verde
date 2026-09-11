from decimal import Decimal

from fastapi import FastAPI
from sqlalchemy import inspect, text

from api import create_app
from core.domain.enums import StatusCaixa, StatusComanda, TipoProduto, UnidadeEstoque
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
        "produto_composicao",
        "comanda",
        "item_comanda",
        "caixa",
        "pagamento",
        "movimento_caixa",
        "movimento_estoque",
    }.issubset(set(inspector.get_table_names()))


def test_product_category_indexes_can_be_created(test_engine):
    inspector = inspect(test_engine)

    categoria_indexes = {
        index["name"] for index in inspector.get_indexes("categoria_produto")
    }
    produto_indexes = {index["name"] for index in inspector.get_indexes("produto")}
    composicao_indexes = {
        index["name"] for index in inspector.get_indexes("produto_composicao")
    }

    assert "idx_categorias_produto_nome" in categoria_indexes
    with test_engine.connect() as connection:
        expression_index = connection.execute(text("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'index'
                AND name = 'idx_categorias_produto_nome_ativo_unique'
                """)).first()

    assert expression_index is not None
    assert "idx_produtos_categoria_id" in produto_indexes
    assert "idx_produtos_nome" in produto_indexes
    assert "idx_produtos_ativo" in produto_indexes
    assert "idx_produto_composicao_produto_pai_id" in composicao_indexes
    assert "idx_produto_composicao_produto_componente_id" in composicao_indexes


def test_domain_defaults_match_mvp():
    produto = Produto(
        nome="Cerveja",
        categoria_id=1,
        preco_venda=Decimal("12.00"),
    )
    comanda = Comanda(nome_cliente="Mesa 1")
    caixa = Caixa()

    assert produto.controla_estoque is True
    assert produto.tipo_produto == TipoProduto.SIMPLES
    assert produto.unidade_estoque == UnidadeEstoque.UNIDADE
    assert comanda.status == StatusComanda.ABERTA
    assert caixa.status == StatusCaixa.ABERTO


def test_container_provides_engine_and_logger(test_container):
    logger = test_container.logger()
    engine = test_container.engine()

    logger.info("Container test")

    assert engine.url.database == ":memory:"
    assert hasattr(logger, "info")
