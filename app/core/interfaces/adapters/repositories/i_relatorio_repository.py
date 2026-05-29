from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional

from core.domain.enums import StatusComanda
from core.domain.models import Caixa, Comanda, Pagamento, Produto


class IRelatorioRepository(ABC):
    @abstractmethod
    def get_caixa_by_id(self, caixa_id: int) -> Optional[Caixa]:
        pass

    @abstractmethod
    def get_caixa_by_data(self, data: date) -> Optional[Caixa]:
        pass

    @abstractmethod
    def list_comandas(
        self,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[StatusComanda] = None,
        caixa_origem_id: Optional[int] = None,
    ) -> list[Comanda]:
        pass

    @abstractmethod
    def list_pagamentos(
        self,
        inicio: Optional[datetime] = None,
        fim: Optional[datetime] = None,
        caixa_id: Optional[int] = None,
    ) -> list[Pagamento]:
        pass

    @abstractmethod
    def list_produtos_controlados(self) -> list[Produto]:
        pass
