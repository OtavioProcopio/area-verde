"""clientes_fiado

Revision ID: g7h8i9j0k1l2
Revises: e6f7a8b9c0d1
Create Date: 2026-05-27 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cliente",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("apelido", sa.String(length=160), nullable=True),
        sa.Column("telefone", sa.String(length=40), nullable=True),
        sa.Column("observacao", sa.String(length=500), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cliente_nome", "cliente", ["nome"], unique=False)
    op.create_index("idx_cliente_apelido", "cliente", ["apelido"], unique=False)
    op.create_index("idx_cliente_telefone", "cliente", ["telefone"], unique=False)
    op.create_index("idx_cliente_ativo", "cliente", ["ativo"], unique=False)

    op.add_column("comanda", sa.Column("cliente_id", sa.Integer(), nullable=True))
    op.add_column(
        "comanda",
        sa.Column("nome_cliente_snapshot", sa.String(length=160), nullable=True),
    )
    op.create_foreign_key(
        "fk_comanda_cliente_id_cliente",
        "comanda",
        "cliente",
        ["cliente_id"],
        ["id"],
    )
    op.create_index(
        "idx_comanda_cliente_id",
        "comanda",
        ["cliente_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_comanda_cliente_id", table_name="comanda")
    op.drop_constraint(
        "fk_comanda_cliente_id_cliente",
        "comanda",
        type_="foreignkey",
    )
    op.drop_column("comanda", "nome_cliente_snapshot")
    op.drop_column("comanda", "cliente_id")

    op.drop_index("idx_cliente_ativo", table_name="cliente")
    op.drop_index("idx_cliente_telefone", table_name="cliente")
    op.drop_index("idx_cliente_apelido", table_name="cliente")
    op.drop_index("idx_cliente_nome", table_name="cliente")
    op.drop_table("cliente")
