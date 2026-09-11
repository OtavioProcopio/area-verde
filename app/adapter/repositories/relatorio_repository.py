from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from core.domain.enums import StatusComanda
from core.domain.models import Caixa, Comanda, MovimentoEstoque, Pagamento, Produto
from core.interfaces.adapters.repositories.i_relatorio_repository import (
    IRelatorioRepository,
)


class RelatorioRepository(IRelatorioRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_caixa_by_id(self, caixa_id: int) -> Optional[Caixa]:
        statement = (
            select(Caixa)
            .where(Caixa.id == caixa_id)
            .options(selectinload(Caixa.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Caixa.movimentos))  # type: ignore[arg-type]
        )
        return self.session.exec(statement).first()

    def get_caixa_by_data(self, data: date) -> Optional[Caixa]:
        statement = (
            select(Caixa)
            .where(Caixa.data == data)
            .options(selectinload(Caixa.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Caixa.movimentos))  # type: ignore[arg-type]
            .order_by(text("id DESC"))
        )
        return self.session.exec(statement).first()

    def list_comandas(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[StatusComanda] = None,
        caixa_origem_id: Optional[int] = None,
    ) -> list[Comanda]:
        statement = (
            select(Comanda)
            .options(selectinload(Comanda.itens))  # type: ignore[arg-type]
            .options(selectinload(Comanda.pagamentos))  # type: ignore[arg-type]
            .options(selectinload(Comanda.cliente))  # type: ignore[arg-type]
        )
        if status is not None:
            statement = statement.where(Comanda.status == status)
        if caixa_origem_id is not None:
            statement = statement.where(Comanda.caixa_origem_id == caixa_origem_id)
        if data_inicio is not None:
            statement = statement.where(
                Comanda.aberta_em >= datetime.combine(data_inicio, time.min)
            )
        if data_fim is not None:
            statement = statement.where(
                Comanda.aberta_em <= datetime.combine(data_fim, time.max)
            )

        statement = statement.order_by(text("aberta_em DESC"), text("id DESC"))
        return list(self.session.exec(statement).all())

    def list_pagamentos(
        self,
        inicio: Optional[datetime] = None,
        fim: Optional[datetime] = None,
        caixa_id: Optional[int] = None,
    ) -> list[Pagamento]:
        statement = (
            select(Pagamento)
            .options(selectinload(Pagamento.comanda))  # type: ignore[arg-type]
            .order_by(text("criado_em ASC"), text("id ASC"))
        )
        if inicio is not None:
            statement = statement.where(Pagamento.criado_em >= inicio)
        if fim is not None:
            statement = statement.where(Pagamento.criado_em <= fim)
        if caixa_id is not None:
            statement = statement.where(Pagamento.caixa_id == caixa_id)
        return list(self.session.exec(statement).all())

    def list_produtos_controlados(self) -> list[Produto]:
        statement = (
            select(Produto)
            .where(Produto.controla_estoque == True)  # noqa: E712
            .order_by(text("nome ASC"))
        )
        return list(self.session.exec(statement).all())

    def list_movimentos_estoque(
        self,
        inicio: Optional[datetime] = None,
        fim: Optional[datetime] = None,
    ) -> list[MovimentoEstoque]:
        statement = (
            select(MovimentoEstoque)
            .options(selectinload(MovimentoEstoque.produto))  # type: ignore[arg-type]
            .order_by(text("criado_em ASC"), text("id ASC"))
        )
        if inicio is not None:
            statement = statement.where(MovimentoEstoque.criado_em >= inicio)
        if fim is not None:
            statement = statement.where(MovimentoEstoque.criado_em <= fim)
        return list(self.session.exec(statement).all())
