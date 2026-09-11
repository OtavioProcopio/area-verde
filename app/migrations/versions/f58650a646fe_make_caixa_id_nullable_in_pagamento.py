"""make_caixa_id_nullable_in_pagamento

Revision ID: f58650a646fe
Revises: d4e5f6a7b8c9
Create Date: 2026-05-26 20:09:12.911097

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f58650a646fe"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "pagamento", sa.Column("observacao", sa.String(length=500), nullable=True)
    )
    op.alter_column("pagamento", "caixa_id", existing_type=sa.INTEGER(), nullable=True)
    op.create_index(
        "idx_pagamento_comanda_id", "pagamento", ["comanda_id"], unique=False
    )
    op.create_index("idx_pagamento_criado_em", "pagamento", ["criado_em"], unique=False)
    op.create_index(
        "idx_pagamento_forma_pagamento", "pagamento", ["forma_pagamento"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_pagamento_forma_pagamento", table_name="pagamento")
    op.drop_index("idx_pagamento_criado_em", table_name="pagamento")
    op.drop_index("idx_pagamento_comanda_id", table_name="pagamento")
    op.alter_column("pagamento", "caixa_id", existing_type=sa.INTEGER(), nullable=False)
    op.drop_column("pagamento", "observacao")
