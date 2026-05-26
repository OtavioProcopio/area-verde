"""initial area verde schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-26 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "configuracao_sistema",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("senha_acesso_hash", sa.String(length=255), nullable=False),
        sa.Column("dias_para_alerta_fiado", sa.Integer(), nullable=False),
        sa.Column("permitir_estoque_negativo", sa.Boolean(), nullable=False),
        sa.Column("nome_bar", sa.String(length=120), nullable=True),
        sa.Column("observacao", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "categoria_produto",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_table(
        "caixa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("valor_inicial", sa.Numeric(12, 2), nullable=False),
        sa.Column("dinheiro_esperado", sa.Numeric(12, 2), nullable=False),
        sa.Column("dinheiro_informado", sa.Numeric(12, 2), nullable=True),
        sa.Column("diferenca", sa.Numeric(12, 2), nullable=True),
        sa.Column("aberto_em", sa.DateTime(), nullable=False),
        sa.Column("fechado_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "comanda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome_cliente", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("aberta_em", sa.DateTime(), nullable=False),
        sa.Column("fechada_em", sa.DateTime(), nullable=True),
        sa.Column("vencimento_em", sa.Date(), nullable=True),
        sa.Column("observacao", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "produto",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("preco_venda", sa.Numeric(12, 2), nullable=False),
        sa.Column("controla_estoque", sa.Boolean(), nullable=False),
        sa.Column("unidade_estoque", sa.String(length=20), nullable=False),
        sa.Column("quantidade_estoque", sa.Numeric(12, 3), nullable=False),
        sa.Column("quantidade_baixa_por_venda", sa.Numeric(12, 3), nullable=False),
        sa.Column("estoque_minimo", sa.Numeric(12, 3), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categoria_produto.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "movimento_caixa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("caixa_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("observacao", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["caixa_id"], ["caixa.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pagamento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("caixa_id", sa.Integer(), nullable=False),
        sa.Column("comanda_id", sa.Integer(), nullable=False),
        sa.Column("forma_pagamento", sa.String(length=20), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["caixa_id"], ["caixa.id"]),
        sa.ForeignKeyConstraint(["comanda_id"], ["comanda.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "item_comanda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comanda_id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=True),
        sa.Column("nome_produto_snapshot", sa.String(length=160), nullable=False),
        sa.Column("preco_unitario_snapshot", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantidade", sa.Numeric(12, 3), nullable=False),
        sa.Column("quantidade_baixada_estoque", sa.Numeric(12, 3), nullable=False),
        sa.Column("total_item", sa.Numeric(12, 2), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["comanda_id"], ["comanda.id"]),
        sa.ForeignKeyConstraint(["produto_id"], ["produto.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "movimento_estoque",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=32), nullable=False),
        sa.Column("quantidade", sa.Numeric(12, 3), nullable=False),
        sa.Column("estoque_antes", sa.Numeric(12, 3), nullable=False),
        sa.Column("estoque_depois", sa.Numeric(12, 3), nullable=False),
        sa.Column("origem", sa.String(length=24), nullable=False),
        sa.Column("referencia_id", sa.Integer(), nullable=True),
        sa.Column("observacao", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["produto_id"], ["produto.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("movimento_estoque")
    op.drop_table("item_comanda")
    op.drop_table("pagamento")
    op.drop_table("movimento_caixa")
    op.drop_table("produto")
    op.drop_table("comanda")
    op.drop_table("caixa")
    op.drop_table("categoria_produto")
    op.drop_table("configuracao_sistema")
