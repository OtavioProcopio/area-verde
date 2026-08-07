from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, List, Optional, cast

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from core.domain.enums import StatusComanda
from core.domain.models import Cliente, Comanda, ItemComanda


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
            .options(selectinload(Comanda.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Comanda.cliente))  # type: ignore[arg-type]
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
    ) -> List[Comanda]:
        statement = (
            select(Comanda)
            .options(selectinload(Comanda.itens))  # type: ignore[arg-type]
            .options(selectinload(Comanda.cliente))  # type: ignore[arg-type]
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

    def list_abertas(self) -> List[Comanda]:
        return self.list(status=StatusComanda.ABERTA)

    def list_pendencias(
        self,
        cliente_id: Optional[int] = None,
        vencidos: Optional[bool] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        nome: Optional[str] = None,
        quitados: Optional[bool] = None,
    ) -> List[Comanda]:
        pendente_em_column = cast(Any, Comanda.pendente_em)
        if quitados:
            status_filter = and_(
                cast(Any, Comanda.status == StatusComanda.FECHADA),
                pendente_em_column.is_not(None),
            )
        else:
            status_filter = cast(Any, Comanda.status == StatusComanda.PENDENTE)

        statement = (
            select(Comanda)
            .where(status_filter)
            .options(selectinload(Comanda.itens))  # type: ignore[arg-type]
            .options(selectinload(Comanda.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Comanda.cliente))  # type: ignore[arg-type]
        )

        if cliente_id is not None:
            statement = statement.where(Comanda.cliente_id == cliente_id)
        vencimento_column = cast(Any, Comanda.vencimento_em)
        if vencidos is True:
            statement = statement.where(vencimento_column < date.today())
        elif vencidos is False:
            statement = statement.where(
                or_(
                    vencimento_column.is_(None),
                    vencimento_column >= date.today(),
                )
            )
        if data_inicio is not None:
            statement = statement.where(
                Comanda.aberta_em >= datetime.combine(data_inicio, time.min)
            )
        if data_fim is not None:
            statement = statement.where(
                Comanda.aberta_em <= datetime.combine(data_fim, time.max)
            )
        if nome:
            termo = f"%{nome.strip().lower()}%"
            statement = statement.outerjoin(Cliente).where(
                or_(
                    func.lower(Comanda.nome_cliente).like(termo),
                    func.lower(Comanda.nome_cliente_snapshot).like(termo),
                    func.lower(Cliente.nome).like(termo),
                    func.lower(Cliente.apelido).like(termo),
                )
            )

        statement = statement.order_by(text("vencimento_em ASC"), text("id DESC"))
        return list(self.session.exec(statement).all())

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, comanda: Comanda) -> None:
        self.session.refresh(comanda)
