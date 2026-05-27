from typing import List

from sqlmodel import Session, select

from core.domain.models import Pagamento
from core.interfaces.adapters.repositories.i_pagamento_repository import (
    IPagamentoRepository,
)


class PagamentoRepository(IPagamentoRepository):
    def __init__(self, session: Session):
        self.session = session

    def criar_pagamento(self, pagamento: Pagamento) -> Pagamento:
        self.session.add(pagamento)
        self.session.flush()
        self.session.refresh(pagamento)
        return pagamento

    def listar_por_comanda(self, comanda_id: int) -> List[Pagamento]:
        statement = (
            select(Pagamento).where(Pagamento.comanda_id == comanda_id)
            # type: ignore
            .order_by(Pagamento.criado_em)  # type: ignore
        )
        results = self.session.exec(statement)
        return list(results.all())
