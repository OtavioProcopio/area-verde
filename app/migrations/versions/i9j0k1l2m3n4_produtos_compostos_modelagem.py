"""produtos_compostos_modelagem

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-05-29 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "i9j0k1l2m3n4"
down_revision: Union[str, None] = "h8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "produto",
        sa.Column(
            "tipo_produto",
            sa.String(length=20),
            server_default="SIMPLES",
            nullable=False,
        ),
    )
    op.create_table(
        "produto_composicao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("produto_pai_id", sa.Integer(), nullable=False),
        sa.Column("produto_componente_id", sa.Integer(), nullable=False),
        sa.Column("quantidade_baixa", sa.Numeric(12, 3), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "quantidade_baixa > 0",
            name="ck_produto_composicao_quantidade_baixa_positiva",
        ),
        sa.ForeignKeyConstraint(["produto_componente_id"], ["produto.id"]),
        sa.ForeignKeyConstraint(["produto_pai_id"], ["produto.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "produto_pai_id",
            "produto_componente_id",
            name="uq_produto_composicao_pai_componente",
        ),
    )
    op.create_index(
        "idx_produto_composicao_produto_pai_id",
        "produto_composicao",
        ["produto_pai_id"],
        unique=False,
    )
    op.create_index(
        "idx_produto_composicao_produto_componente_id",
        "produto_composicao",
        ["produto_componente_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_produto_composicao_produto_componente_id",
        table_name="produto_composicao",
    )
    op.drop_index(
        "idx_produto_composicao_produto_pai_id",
        table_name="produto_composicao",
    )
    op.drop_table("produto_composicao")
    op.drop_column("produto", "tipo_produto")
