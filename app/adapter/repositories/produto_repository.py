from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select

from core.domain.models import Produto


class ProdutoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, produto: Produto) -> Produto:
        self.session.add(produto)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def update(self, produto: Produto) -> Produto:
        self.session.add(produto)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def save(self, produto: Produto) -> Produto:
        self.session.add(produto)
        return produto

    def add(self, produto: Produto) -> Produto:
        self.session.add(produto)
        self.session.flush()
        return produto

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, produto: Produto) -> None:
        self.session.refresh(produto)

    def get_by_id(self, produto_id: int) -> Optional[Produto]:
        return self.session.get(Produto, produto_id)

    def list(
        self,
        ativo: Optional[bool] = None,
        categoria_id: Optional[int] = None,
        nome: Optional[str] = None,
    ) -> list[Produto]:
        statement = select(Produto)

        if ativo is not None:
            statement = statement.where(Produto.ativo == ativo)
        if categoria_id is not None:
            statement = statement.where(Produto.categoria_id == categoria_id)
        if nome:
            statement = statement.where(
                func.lower(Produto.nome).like(f"%{nome.strip().lower()}%")
            )

        statement = statement.order_by(Produto.nome)
        return list(self.session.exec(statement).all())
