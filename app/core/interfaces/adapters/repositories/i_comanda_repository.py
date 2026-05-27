from __future__ import annotations

from datetime import date
from typing import List, Optional, Protocol

from core.domain.enums import StatusComanda
from core.domain.models import Comanda, ItemComanda


class IComandaRepository(Protocol):
    def create(self, comanda: Comanda) -> Comanda: ...

    def save(self, comanda: Comanda) -> Comanda: ...

    def save_item(self, item: ItemComanda) -> ItemComanda: ...

    def delete_item(self, item: ItemComanda) -> None: ...

    def get_by_id(self, comanda_id: int) -> Optional[Comanda]: ...

    def get_item_by_id(self, item_id: int) -> Optional[ItemComanda]: ...

    def get_item_by_comanda_produto(
        self, comanda_id: int, produto_id: int
    ) -> Optional[ItemComanda]: ...

    def list(
        self,
        status: Optional[StatusComanda] = None,
        nome: Optional[str] = None,
        data: Optional[date] = None,
    ) -> List[Comanda]: ...

    def list_abertas(self) -> List[Comanda]: ...

    def list_pendencias(
        self,
        cliente_id: Optional[int] = None,
        vencidos: Optional[bool] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        nome: Optional[str] = None,
    ) -> List[Comanda]: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def refresh(self, comanda: Comanda) -> None: ...
