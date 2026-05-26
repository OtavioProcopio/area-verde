from enum import Enum


class StatusComanda(str, Enum):
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"
    PENDENTE = "PENDENTE"
    CANCELADA = "CANCELADA"
