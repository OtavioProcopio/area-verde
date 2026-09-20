from enum import Enum


class TipoAjusteComanda(str, Enum):
    ACRESCIMO = "ACRESCIMO"
    DESCONTO = "DESCONTO"
