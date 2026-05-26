from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select

from core.domain.models import CategoriaProduto


class CategoriaProdutoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, categoria: CategoriaProduto) -> CategoriaProduto:
        self.session.add(categoria)
        self.session.commit()
        self.session.refresh(categoria)
        return categoria

    def update(self, categoria: CategoriaProduto) -> CategoriaProduto:
        self.session.add(categoria)
        self.session.commit()
        self.session.refresh(categoria)
        return categoria

    def get_by_id(self, categoria_id: int) -> Optional[CategoriaProduto]:
        return self.session.get(CategoriaProduto, categoria_id)

    def get_active_by_nome(
        self, nome: str, exclude_id: Optional[int] = None
    ) -> Optional[CategoriaProduto]:
        ativo = True
        statement = select(CategoriaProduto).where(
            func.lower(CategoriaProduto.nome) == nome.strip().lower(),
            CategoriaProduto.ativo == ativo,
        )
        if exclude_id is not None:
            statement = statement.where(CategoriaProduto.id != exclude_id)

        return self.session.exec(statement).first()

    def list(self, ativo: Optional[bool] = None) -> list[CategoriaProduto]:
        statement = select(CategoriaProduto)
        if ativo is not None:
            statement = statement.where(CategoriaProduto.ativo == ativo)

        statement = statement.order_by(CategoriaProduto.nome)
        return list(self.session.exec(statement).all())
