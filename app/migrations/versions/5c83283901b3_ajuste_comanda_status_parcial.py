"""ajuste_comanda_status_parcial

Revision ID: 5c83283901b3
Revises: j0k1l2m3n4o5
Create Date: 2026-09-20 14:01:07.671787

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5c83283901b3"
down_revision: Union[str, None] = "j0k1l2m3n4o5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ajuste_comanda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comanda_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("descricao", sa.String(length=500), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["comanda_id"], ["comanda.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_ajuste_comanda_comanda_id",
        "ajuste_comanda",
        ["comanda_id"],
        unique=False,
    )
    op.create_index(
        "idx_ajuste_comanda_criado_em",
        "ajuste_comanda",
        ["criado_em"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_ajuste_comanda_criado_em", table_name="ajuste_comanda")
    op.drop_index("idx_ajuste_comanda_comanda_id", table_name="ajuste_comanda")
    op.drop_table("ajuste_comanda")
