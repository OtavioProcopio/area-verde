from typing import Any, Optional, cast

from sqlalchemy import func, or_, text
from sqlmodel import Session, select

from core.domain.models import Cliente
from core.interfaces.adapters.repositories.i_cliente_repository import (
    IClienteRepository,
)


class ClienteRepository(IClienteRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, cliente: Cliente) -> Cliente:
        self.session.add(cliente)
        self.session.flush()
        return cliente

    def save(self, cliente: Cliente) -> Cliente:
        self.session.add(cliente)
        self.session.flush()
        return cliente

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        return self.session.get(Cliente, cliente_id)

    def list(
        self,
        ativo: Optional[bool] = None,
        nome: Optional[str] = None,
        telefone: Optional[str] = None,
    ) -> list[Cliente]:
        statement = select(Cliente)

        if ativo is not None:
            statement = statement.where(Cliente.ativo == ativo)
        if nome:
            termo = f"%{nome.strip().lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Cliente.nome).like(termo),
                    func.lower(Cliente.apelido).like(termo),
                )
            )
        if telefone:
            telefone_column = cast(Any, Cliente.telefone)
            statement = statement.where(telefone_column.like(f"%{telefone.strip()}%"))

        statement = statement.order_by(text("nome ASC"), text("id ASC"))
        return list(self.session.exec(statement).all())

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, cliente: Cliente) -> None:
        self.session.refresh(cliente)
