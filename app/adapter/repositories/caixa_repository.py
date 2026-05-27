from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from core.domain.enums import StatusCaixa
from core.domain.models import Caixa, MovimentoCaixa
from core.interfaces.adapters.repositories.i_caixa_repository import ICaixaRepository


class CaixaRepository(ICaixaRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, caixa_id: int) -> Optional[Caixa]:
        statement = (
            select(Caixa)
            .where(Caixa.id == caixa_id)
            .options(selectinload(Caixa.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Caixa.movimentos))  # type: ignore[arg-type]
        )
        return self.session.exec(statement).first()

    def get_aberto(self) -> Optional[Caixa]:
        statement = (
            select(Caixa)
            .where(Caixa.status == StatusCaixa.ABERTO)
            .options(selectinload(Caixa.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Caixa.movimentos))  # type: ignore[arg-type]
            .order_by(text("id DESC"))
        )
        return self.session.exec(statement).first()

    def list(
        self,
        status: Optional[StatusCaixa] = None,
        data: Optional[date] = None,
    ) -> list[Caixa]:
        statement = select(Caixa)
        if status is not None:
            statement = statement.where(Caixa.status == status)
        if data is not None:
            statement = statement.where(Caixa.data == data)

        statement = statement.order_by(text("data DESC"), text("id DESC"))
        return list(self.session.exec(statement).all())

    def save(self, caixa: Caixa) -> Caixa:
        self.session.add(caixa)
        self.session.flush()
        return caixa

    def save_movimento(self, movimento: MovimentoCaixa) -> MovimentoCaixa:
        self.session.add(movimento)
        self.session.flush()
        return movimento

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, caixa: Caixa) -> None:
        self.session.refresh(caixa)
