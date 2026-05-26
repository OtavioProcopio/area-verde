from enum import Enum


class TipoMovimentoCaixa(str, Enum):
    ABERTURA = "ABERTURA"
    SANGRIA = "SANGRIA"
    REFORCO = "REFORCO"
    AJUSTE = "AJUSTE"
