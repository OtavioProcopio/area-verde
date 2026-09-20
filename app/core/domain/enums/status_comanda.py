from enum import Enum


class StatusComanda(str, Enum):
    ABERTA = "ABERTA"
    PARCIALMENTE_PAGA = "PARCIALMENTE_PAGA"
    FECHADA = "FECHADA"
    PENDENTE = "PENDENTE"
    CANCELADA = "CANCELADA"
