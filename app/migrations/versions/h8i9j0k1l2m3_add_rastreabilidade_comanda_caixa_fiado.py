"""add_rastreabilidade_comanda_caixa_fiado

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-05-27 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h8i9j0k1l2m3"
down_revision: Union[str, None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("comanda", sa.Column("caixa_origem_id", sa.Integer(), nullable=True))
    op.add_column("comanda", sa.Column("pendente_em", sa.DateTime(), nullable=True))
    op.create_foreign_key(
        "fk_comanda_caixa_origem_id_caixa",
        "comanda",
        "caixa",
        ["caixa_origem_id"],
        ["id"],
    )
    op.create_index(
        "idx_comanda_caixa_origem_id",
        "comanda",
        ["caixa_origem_id"],
        unique=False,
    )
    op.create_index(
        "idx_comanda_pendente_em",
        "comanda",
        ["pendente_em"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_comanda_pendente_em", table_name="comanda")
    op.drop_index("idx_comanda_caixa_origem_id", table_name="comanda")
    op.drop_constraint(
        "fk_comanda_caixa_origem_id_caixa",
        "comanda",
        type_="foreignkey",
    )
    op.drop_column("comanda", "pendente_em")
    op.drop_column("comanda", "caixa_origem_id")
