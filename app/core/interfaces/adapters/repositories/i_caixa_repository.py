from datetime import date
from typing import Optional, Protocol

from core.domain.enums import StatusCaixa
from core.domain.models import Caixa, MovimentoCaixa


class ICaixaRepository(Protocol):
    def get_by_id(self, caixa_id: int) -> Optional[Caixa]: ...

    def get_aberto(self) -> Optional[Caixa]: ...

    def list(
        self,
        status: Optional[StatusCaixa] = None,
        data: Optional[date] = None,
    ) -> list[Caixa]: ...

    def save(self, caixa: Caixa) -> Caixa: ...

    def save_movimento(self, movimento: MovimentoCaixa) -> MovimentoCaixa: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def refresh(self, caixa: Caixa) -> None: ...
