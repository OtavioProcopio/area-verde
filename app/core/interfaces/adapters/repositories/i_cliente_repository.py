from typing import Optional, Protocol

from core.domain.models import Cliente


class IClienteRepository(Protocol):
    def create(self, cliente: Cliente) -> Cliente: ...

    def save(self, cliente: Cliente) -> Cliente: ...

    def get_by_id(self, cliente_id: int) -> Optional[Cliente]: ...

    def list(
        self,
        ativo: Optional[bool] = None,
        nome: Optional[str] = None,
        telefone: Optional[str] = None,
    ) -> list[Cliente]: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def refresh(self, cliente: Cliente) -> None: ...
