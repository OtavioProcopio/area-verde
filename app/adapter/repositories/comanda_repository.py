from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import func, text
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from core.domain.enums import StatusComanda
from core.domain.models import Comanda, ItemComanda


class ComandaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, comanda: Comanda) -> Comanda:
        self.session.add(comanda)
        self.session.flush()
        return comanda

    def save(self, comanda: Comanda) -> Comanda:
        self.session.add(comanda)
        return comanda

    def save_item(self, item: ItemComanda) -> ItemComanda:
        self.session.add(item)
        self.session.flush()
        return item

    def delete_item(self, item: ItemComanda) -> None:
        self.session.delete(item)
        self.session.flush()

    def get_by_id(self, comanda_id: int) -> Optional[Comanda]:
        statement = (
            select(Comanda)
            .where(Comanda.id == comanda_id)
            .options(selectinload(Comanda.itens))  # type: ignore[arg-type]
        )
        return self.session.exec(statement).first()

    def get_item_by_id(self, item_id: int) -> Optional[ItemComanda]:
        return self.session.get(ItemComanda, item_id)

    def get_item_by_comanda_produto(
        self, comanda_id: int, produto_id: int
    ) -> Optional[ItemComanda]:
        statement = select(ItemComanda).where(
            ItemComanda.comanda_id == comanda_id,
            ItemComanda.produto_id == produto_id,
        )
        return self.session.exec(statement).first()

    def list(
        self,
        status: Optional[StatusComanda] = None,
        nome: Optional[str] = None,
        data: Optional[date] = None,
    ) -> list[Comanda]:
        statement = select(Comanda).options(
            selectinload(Comanda.itens)  # type: ignore[arg-type]
        )

        if status is not None:
            statement = statement.where(Comanda.status == status)
        if nome:
            statement = statement.where(
                func.lower(Comanda.nome_cliente).like(f"%{nome.strip().lower()}%")
            )
        if data is not None:
            inicio = datetime.combine(data, time.min)
            fim = datetime.combine(data, time.max)
            statement = statement.where(
                Comanda.aberta_em >= inicio,
                Comanda.aberta_em <= fim,
            )

        statement = statement.order_by(text("aberta_em DESC"), text("id DESC"))
        return list(self.session.exec(statement).all())

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, comanda: Comanda) -> None:
        self.session.refresh(comanda)
