"""produtos categorias module

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-26 00:00:01.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INITIAL_CATEGORIES = (
    "Cervejas",
    "Doses",
    "Refrigerantes",
    "Salgados",
    "Salgadinhos",
    "Avulsos",
    "Outros",
)


def upgrade() -> None:
    op.drop_constraint(
        "categoria_produto_nome_key",
        "categoria_produto",
        type_="unique",
    )
    op.alter_column(
        "produto",
        "categoria_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "idx_categorias_produto_nome",
        "categoria_produto",
        ["nome"],
    )
    op.create_index(
        "idx_categorias_produto_nome_ativo_unique",
        "categoria_produto",
        [sa.text("lower(nome)")],
        unique=True,
        postgresql_where=sa.text("ativo = true"),
    )
    op.create_index(
        "idx_produtos_categoria_id",
        "produto",
        ["categoria_id"],
    )
    op.create_index("idx_produtos_nome", "produto", ["nome"])
    op.create_index("idx_produtos_ativo", "produto", ["ativo"])

    connection = op.get_bind()
    for nome in INITIAL_CATEGORIES:
        connection.execute(
            sa.text("""
                INSERT INTO categoria_produto
                    (nome, ativo, criado_em, atualizado_em)
                SELECT :nome, true, now(), now()
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM categoria_produto
                    WHERE lower(nome) = lower(:nome)
                    AND ativo = true
                )
                """),
            {"nome": nome},
        )


def downgrade() -> None:
    op.drop_index("idx_produtos_ativo", table_name="produto")
    op.drop_index("idx_produtos_nome", table_name="produto")
    op.drop_index("idx_produtos_categoria_id", table_name="produto")
    op.drop_index(
        "idx_categorias_produto_nome_ativo_unique",
        table_name="categoria_produto",
    )
    op.drop_index("idx_categorias_produto_nome", table_name="categoria_produto")
    op.alter_column(
        "produto",
        "categoria_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_unique_constraint(
        "categoria_produto_nome_key",
        "categoria_produto",
        ["nome"],
    )
