from enum import Enum


class TipoMovimentoEstoque(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA_VENDA = "SAIDA_VENDA"
    DEVOLUCAO_CANCELAMENTO = "DEVOLUCAO_CANCELAMENTO"
    AJUSTE = "AJUSTE"
