from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar, List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Index, Numeric, String, UniqueConstraint, text
from sqlmodel import Field, Relationship, SQLModel

from core.domain.enums import (
    FormaPagamento,
    OrigemMovimentoEstoque,
    StatusCaixa,
    StatusComanda,
    TipoMovimentoCaixa,
    TipoMovimentoEstoque,
    TipoProduto,
    UnidadeEstoque,
)

MONEY_COLUMN = Numeric(12, 2)
QUANTITY_COLUMN = Numeric(12, 3)


class ConfiguracaoSistema(SQLModel, table=True):
    __tablename__: ClassVar[str] = "configuracao_sistema"

    id: Optional[int] = Field(default=None, primary_key=True)
    senha_acesso_hash: str = Field(sa_column=Column(String(255), nullable=False))
    dias_para_alerta_fiado: int = Field(default=7)
    permitir_estoque_negativo: bool = Field(default=False)
    nome_bar: str = Field(default="Area Verde", sa_column=Column(String(120)))
    observacao: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)


class CategoriaProduto(SQLModel, table=True):
    __tablename__: ClassVar[str] = "categoria_produto"
    __table_args__: ClassVar[tuple] = (
        Index(
            "idx_categorias_produto_nome_ativo_unique",
            text("lower(nome)"),
            unique=True,
            postgresql_where=text("ativo = true"),
            sqlite_where=text("ativo = 1"),
        ),
        Index("idx_categorias_produto_nome", "nome"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(sa_column=Column(String(120), nullable=False))
    ativo: bool = Field(default=True)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    produtos: List["Produto"] = Relationship(back_populates="categoria")


class Produto(SQLModel, table=True):
    __tablename__: ClassVar[str] = "produto"
    __table_args__: ClassVar[tuple] = (
        Index("idx_produtos_categoria_id", "categoria_id"),
        Index("idx_produtos_nome", "nome"),
        Index("idx_produtos_ativo", "ativo"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    categoria_id: int = Field(foreign_key="categoria_produto.id")
    nome: str = Field(sa_column=Column(String(160), nullable=False))
    preco_venda: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    tipo_produto: TipoProduto = Field(
        default=TipoProduto.SIMPLES,
        sa_column=Column(
            SAEnum(TipoProduto, native_enum=False, length=20),
            nullable=False,
        ),
    )
    controla_estoque: bool = Field(default=True)
    unidade_estoque: UnidadeEstoque = Field(
        default=UnidadeEstoque.UNIDADE,
        sa_column=Column(
            SAEnum(UnidadeEstoque, native_enum=False, length=20),
            nullable=False,
        ),
    )
    quantidade_estoque: Decimal = Field(
        default=Decimal("0.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    quantidade_baixa_por_venda: Decimal = Field(
        default=Decimal("1.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    estoque_minimo: Decimal = Field(
        default=Decimal("0.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    ativo: bool = Field(default=True)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    categoria: Optional[CategoriaProduto] = Relationship(back_populates="produtos")
    itens_comanda: List["ItemComanda"] = Relationship(back_populates="produto")
    movimentos_estoque: List["MovimentoEstoque"] = Relationship(
        back_populates="produto"
    )
    composicoes: List["ProdutoComposicao"] = Relationship(
        back_populates="produto_pai",
        sa_relationship_kwargs={
            "foreign_keys": "ProdutoComposicao.produto_pai_id",
        },
    )
    componente_em: List["ProdutoComposicao"] = Relationship(
        back_populates="produto_componente",
        sa_relationship_kwargs={
            "foreign_keys": "ProdutoComposicao.produto_componente_id",
        },
    )


class ProdutoComposicao(SQLModel, table=True):
    __tablename__: ClassVar[str] = "produto_composicao"
    __table_args__: ClassVar[tuple] = (
        UniqueConstraint(
            "produto_pai_id",
            "produto_componente_id",
            name="uq_produto_composicao_pai_componente",
        ),
        CheckConstraint(
            "quantidade_baixa > 0",
            name="ck_produto_composicao_quantidade_baixa_positiva",
        ),
        Index("idx_produto_composicao_produto_pai_id", "produto_pai_id"),
        Index(
            "idx_produto_composicao_produto_componente_id",
            "produto_componente_id",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    produto_pai_id: int = Field(foreign_key="produto.id")
    produto_componente_id: int = Field(foreign_key="produto.id")
    quantidade_baixa: Decimal = Field(
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    produto_pai: Optional[Produto] = Relationship(
        back_populates="composicoes",
        sa_relationship_kwargs={
            "foreign_keys": "ProdutoComposicao.produto_pai_id",
        },
    )
    produto_componente: Optional[Produto] = Relationship(
        back_populates="componente_em",
        sa_relationship_kwargs={
            "foreign_keys": "ProdutoComposicao.produto_componente_id",
        },
    )


class Cliente(SQLModel, table=True):
    __tablename__: ClassVar[str] = "cliente"
    __table_args__: ClassVar[tuple] = (
        Index("idx_cliente_nome", "nome"),
        Index("idx_cliente_apelido", "apelido"),
        Index("idx_cliente_telefone", "telefone"),
        Index("idx_cliente_ativo", "ativo"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(sa_column=Column(String(160), nullable=False))
    apelido: Optional[str] = Field(default=None, sa_column=Column(String(160)))
    telefone: Optional[str] = Field(default=None, sa_column=Column(String(40)))
    observacao: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    ativo: bool = Field(default=True)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    comandas: List["Comanda"] = Relationship(back_populates="cliente")


class Comanda(SQLModel, table=True):
    __tablename__: ClassVar[str] = "comanda"
    __table_args__: ClassVar[tuple] = (
        Index("idx_comanda_cliente_id", "cliente_id"),
        Index("idx_comanda_caixa_origem_id", "caixa_origem_id"),
        Index("idx_comanda_pendente_em", "pendente_em"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    caixa_origem_id: Optional[int] = Field(default=None, foreign_key="caixa.id")
    cliente_id: Optional[int] = Field(default=None, foreign_key="cliente.id")
    nome_cliente: str = Field(sa_column=Column(String(160), nullable=False))
    nome_cliente_snapshot: Optional[str] = Field(
        default=None, sa_column=Column(String(160))
    )
    status: StatusComanda = Field(
        default=StatusComanda.ABERTA,
        sa_column=Column(
            SAEnum(StatusComanda, native_enum=False, length=20),
            nullable=False,
        ),
    )
    total: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    aberta_em: datetime = Field(default_factory=datetime.now)
    fechada_em: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    cancelada_em: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    pendente_em: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    vencimento_em: Optional[date] = None
    observacao: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    itens: List["ItemComanda"] = Relationship(back_populates="comanda")
    pagamentos: List["Pagamento"] = Relationship(back_populates="comanda")
    cliente: Optional[Cliente] = Relationship(back_populates="comandas")
    caixa_origem: Optional["Caixa"] = Relationship(back_populates="comandas_origem")


class ItemComanda(SQLModel, table=True):
    __tablename__: ClassVar[str] = "item_comanda"

    id: Optional[int] = Field(default=None, primary_key=True)
    comanda_id: int = Field(foreign_key="comanda.id")
    produto_id: Optional[int] = Field(default=None, foreign_key="produto.id")
    nome_produto_snapshot: str = Field(sa_column=Column(String(160), nullable=False))
    preco_unitario_snapshot: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    quantidade: Decimal = Field(
        default=Decimal("1.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    quantidade_baixada_estoque: Decimal = Field(
        default=Decimal("0.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    total_item: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    comanda: Optional[Comanda] = Relationship(back_populates="itens")
    produto: Optional[Produto] = Relationship(back_populates="itens_comanda")


class Caixa(SQLModel, table=True):
    __tablename__: ClassVar[str] = "caixa"
    __table_args__: ClassVar[tuple] = (
        Index("idx_caixa_status", "status"),
        Index("idx_caixa_data", "data"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    data: date = Field(default_factory=date.today)
    status: StatusCaixa = Field(
        default=StatusCaixa.ABERTO,
        sa_column=Column(
            SAEnum(StatusCaixa, native_enum=False, length=20),
            nullable=False,
        ),
    )
    valor_inicial: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    dinheiro_esperado: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    dinheiro_informado: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(MONEY_COLUMN, nullable=True),
    )
    diferenca: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(MONEY_COLUMN, nullable=True),
    )
    aberto_em: datetime = Field(default_factory=datetime.now)
    fechado_em: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, nullable=True)
    )
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

    pagamentos: List["Pagamento"] = Relationship(back_populates="caixa")
    movimentos: List["MovimentoCaixa"] = Relationship(back_populates="caixa")
    comandas_origem: List["Comanda"] = Relationship(back_populates="caixa_origem")


class Pagamento(SQLModel, table=True):
    __tablename__: ClassVar[str] = "pagamento"
    __table_args__: ClassVar[tuple] = (
        Index("idx_pagamento_caixa_id", "caixa_id"),
        Index("idx_pagamento_comanda_id", "comanda_id"),
        Index("idx_pagamento_forma_pagamento", "forma_pagamento"),
        Index("idx_pagamento_criado_em", "criado_em"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    caixa_id: Optional[int] = Field(default=None, foreign_key="caixa.id")
    comanda_id: int = Field(foreign_key="comanda.id")
    forma_pagamento: FormaPagamento = Field(
        sa_column=Column(
            SAEnum(FormaPagamento, native_enum=False, length=20),
            nullable=False,
        )
    )
    valor: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    observacao: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    criado_em: datetime = Field(default_factory=datetime.now)

    caixa: Optional[Caixa] = Relationship(back_populates="pagamentos")
    comanda: Optional[Comanda] = Relationship(back_populates="pagamentos")


class MovimentoCaixa(SQLModel, table=True):
    __tablename__: ClassVar[str] = "movimento_caixa"
    __table_args__: ClassVar[tuple] = (
        Index("idx_movimento_caixa_caixa_id", "caixa_id"),
        Index("idx_movimento_caixa_tipo", "tipo"),
        Index("idx_movimento_caixa_criado_em", "criado_em"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    caixa_id: int = Field(foreign_key="caixa.id")
    tipo: TipoMovimentoCaixa = Field(
        sa_column=Column(
            SAEnum(TipoMovimentoCaixa, native_enum=False, length=20),
            nullable=False,
        )
    )
    valor: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(MONEY_COLUMN, nullable=False),
    )
    observacao: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    criado_em: datetime = Field(default_factory=datetime.now)

    caixa: Optional[Caixa] = Relationship(back_populates="movimentos")


class MovimentoEstoque(SQLModel, table=True):
    __tablename__: ClassVar[str] = "movimento_estoque"

    id: Optional[int] = Field(default=None, primary_key=True)
    produto_id: int = Field(foreign_key="produto.id")
    tipo: TipoMovimentoEstoque = Field(
        sa_column=Column(
            SAEnum(TipoMovimentoEstoque, native_enum=False, length=32),
            nullable=False,
        )
    )
    quantidade: Decimal = Field(
        default=Decimal("0.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    estoque_antes: Decimal = Field(
        default=Decimal("0.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    estoque_depois: Decimal = Field(
        default=Decimal("0.000"),
        sa_column=Column(QUANTITY_COLUMN, nullable=False),
    )
    origem: OrigemMovimentoEstoque = Field(
        sa_column=Column(
            SAEnum(OrigemMovimentoEstoque, native_enum=False, length=24),
            nullable=False,
        )
    )
    referencia_id: Optional[int] = None
    observacao: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    criado_em: datetime = Field(default_factory=datetime.now)

    produto: Optional[Produto] = Relationship(back_populates="movimentos_estoque")
