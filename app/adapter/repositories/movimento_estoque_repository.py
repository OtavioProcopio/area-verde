from typing import Optional

from sqlalchemy import text
from sqlmodel import Session, select

from core.domain.models import MovimentoEstoque


class MovimentoEstoqueRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, movimento: MovimentoEstoque) -> MovimentoEstoque:
        self.session.add(movimento)
        return movimento

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, movimento: MovimentoEstoque) -> None:
        self.session.refresh(movimento)

    def list_by_produto(self, produto_id: int) -> list[MovimentoEstoque]:
        statement = (
            select(MovimentoEstoque)
            .where(MovimentoEstoque.produto_id == produto_id)
            .order_by(text("criado_em DESC"), text("id DESC"))
        )
        return list(self.session.exec(statement).all())

    def get_by_id(self, movimento_id: int) -> Optional[MovimentoEstoque]:
        return self.session.get(MovimentoEstoque, movimento_id)
