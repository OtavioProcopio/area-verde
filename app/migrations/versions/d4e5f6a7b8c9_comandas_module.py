"""comandas module

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-26 00:00:03.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("comanda", sa.Column("cancelada_em", sa.DateTime(), nullable=True))
    op.add_column(
        "item_comanda",
        sa.Column(
            "atualizado_em",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.alter_column("item_comanda", "atualizado_em", server_default=None)

    op.create_index("idx_comanda_status", "comanda", ["status"])
    op.create_index("idx_comanda_nome_cliente", "comanda", ["nome_cliente"])
    op.create_index("idx_comanda_aberta_em", "comanda", ["aberta_em"])
    op.create_index(
        "idx_item_comanda_comanda_id",
        "item_comanda",
        ["comanda_id"],
    )
    op.create_index(
        "idx_item_comanda_produto_id",
        "item_comanda",
        ["produto_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_item_comanda_produto_id", table_name="item_comanda")
    op.drop_index("idx_item_comanda_comanda_id", table_name="item_comanda")
    op.drop_index("idx_comanda_aberta_em", table_name="comanda")
    op.drop_index("idx_comanda_nome_cliente", table_name="comanda")
    op.drop_index("idx_comanda_status", table_name="comanda")
    op.drop_column("item_comanda", "atualizado_em")
    op.drop_column("comanda", "cancelada_em")
