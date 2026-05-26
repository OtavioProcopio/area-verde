from enum import Enum


class OrigemMovimentoEstoque(str, Enum):
    COMANDA = "COMANDA"
    ENTRADA_MANUAL = "ENTRADA_MANUAL"
    AJUSTE_MANUAL = "AJUSTE_MANUAL"
    CANCELAMENTO = "CANCELAMENTO"
