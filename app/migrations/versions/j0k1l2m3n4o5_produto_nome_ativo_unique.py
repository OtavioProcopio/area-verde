"""produto nome ativo unique

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-09-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "j0k1l2m3n4o5"
down_revision: Union[str, None] = "i9j0k1l2m3n4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_produtos_nome_ativo_unique",
        "produto",
        [sa.text("lower(nome)")],
        unique=True,
        postgresql_where=sa.text("ativo = true"),
    )


def downgrade() -> None:
    op.drop_index(
        "idx_produtos_nome_ativo_unique",
        table_name="produto",
    )
