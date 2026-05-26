"""estoque module indexes

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-26 00:00:02.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_movimento_estoque_produto_id",
        "movimento_estoque",
        ["produto_id"],
    )
    op.create_index(
        "idx_movimento_estoque_tipo",
        "movimento_estoque",
        ["tipo"],
    )
    op.create_index(
        "idx_movimento_estoque_origem",
        "movimento_estoque",
        ["origem"],
    )
    op.create_index(
        "idx_movimento_estoque_criado_em",
        "movimento_estoque",
        ["criado_em"],
    )


def downgrade() -> None:
    op.drop_index("idx_movimento_estoque_criado_em", table_name="movimento_estoque")
    op.drop_index("idx_movimento_estoque_origem", table_name="movimento_estoque")
    op.drop_index("idx_movimento_estoque_tipo", table_name="movimento_estoque")
    op.drop_index("idx_movimento_estoque_produto_id", table_name="movimento_estoque")
