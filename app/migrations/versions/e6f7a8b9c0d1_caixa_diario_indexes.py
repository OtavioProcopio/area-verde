"""caixa_diario_indexes

Revision ID: e6f7a8b9c0d1
Revises: f58650a646fe
Create Date: 2026-05-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, None] = "f58650a646fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("idx_caixa_status", "caixa", ["status"], unique=False)
    op.create_index("idx_caixa_data", "caixa", ["data"], unique=False)
    op.create_index(
        "idx_movimento_caixa_caixa_id",
        "movimento_caixa",
        ["caixa_id"],
        unique=False,
    )
    op.create_index(
        "idx_movimento_caixa_tipo",
        "movimento_caixa",
        ["tipo"],
        unique=False,
    )
    op.create_index(
        "idx_movimento_caixa_criado_em",
        "movimento_caixa",
        ["criado_em"],
        unique=False,
    )
    op.create_index(
        "idx_pagamento_caixa_id",
        "pagamento",
        ["caixa_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_pagamento_caixa_id", table_name="pagamento")
    op.drop_index("idx_movimento_caixa_criado_em", table_name="movimento_caixa")
    op.drop_index("idx_movimento_caixa_tipo", table_name="movimento_caixa")
    op.drop_index("idx_movimento_caixa_caixa_id", table_name="movimento_caixa")
    op.drop_index("idx_caixa_data", table_name="caixa")
    op.drop_index("idx_caixa_status", table_name="caixa")
