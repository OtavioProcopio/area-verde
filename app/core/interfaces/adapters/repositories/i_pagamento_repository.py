from abc import ABC, abstractmethod
from typing import List

from core.domain.models import Pagamento


class IPagamentoRepository(ABC):
    @abstractmethod
    def criar_pagamento(self, pagamento: Pagamento) -> Pagamento:
        pass

    @abstractmethod
    def listar_por_comanda(self, comanda_id: int) -> List[Pagamento]:
        pass
