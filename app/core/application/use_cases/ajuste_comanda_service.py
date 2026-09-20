from datetime import datetime
from decimal import Decimal
from typing import List

from core.domain.enums import StatusComanda, TipoAjusteComanda
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import AjusteComanda, Comanda
from core.interfaces.adapters.repositories.i_comanda_repository import (
    IComandaRepository,
)


class AjusteComandaService:
    def __init__(self, comanda_repository: IComandaRepository):
        self.comanda_repository = comanda_repository

    @staticmethod
    def total_ajustado(comanda: Comanda) -> Decimal:
        delta = sum(
            (
                (
                    ajuste.valor
                    if ajuste.tipo == TipoAjusteComanda.ACRESCIMO
                    else -ajuste.valor
                )
                for ajuste in comanda.ajustes
            ),
            Decimal("0.00"),
        )
        return comanda.total + delta

    @staticmethod
    def saldo_restante(comanda: Comanda) -> Decimal:
        pago = sum(
            (pagamento.valor for pagamento in comanda.pagamentos), Decimal("0.00")
        )
        return AjusteComandaService.total_ajustado(comanda) - pago

    def aplicar_ajuste(
        self,
        comanda_id: int,
        tipo: TipoAjusteComanda,
        valor: Decimal,
        descricao: str,
    ) -> Comanda:
        try:
            comanda = self._get_comanda(comanda_id)
            self._ensure_pode_ajustar(comanda)
            self._ensure_descricao_valida(descricao)
            self._ensure_valor_valido(comanda, tipo, valor)

            ajuste = AjusteComanda(
                comanda_id=comanda_id,
                tipo=tipo,
                valor=valor,
                descricao=descricao.strip(),
                criado_em=datetime.now(),
            )
            self.comanda_repository.save_ajuste(ajuste)
            comanda.ajustes.append(ajuste)
            comanda.atualizado_em = datetime.now()
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self._get_comanda(comanda_id)

    def listar_ajustes(self, comanda_id: int) -> List[AjusteComanda]:
        comanda = self._get_comanda(comanda_id)
        return list(comanda.ajustes)

    def _get_comanda(self, comanda_id: int) -> Comanda:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if comanda is None:
            raise NotFoundError("comanda_nao_encontrada", "Comanda não encontrada")
        return comanda

    @staticmethod
    def _ensure_pode_ajustar(comanda: Comanda) -> None:
        if comanda.status in {StatusComanda.FECHADA, StatusComanda.CANCELADA}:
            raise ApplicationError("comanda_nao_aberta", "Comanda não está aberta", 400)

    @staticmethod
    def _ensure_descricao_valida(descricao: str) -> None:
        if not descricao or not descricao.strip():
            raise ApplicationError(
                "ajuste_descricao_obrigatoria",
                "Descrição do ajuste é obrigatória",
                400,
            )

    @staticmethod
    def _ensure_valor_valido(
        comanda: Comanda, tipo: TipoAjusteComanda, valor: Decimal
    ) -> None:
        if valor <= Decimal("0"):
            raise ApplicationError(
                "ajuste_valor_invalido", "Valor do ajuste inválido", 400
            )
        delta = valor if tipo == TipoAjusteComanda.ACRESCIMO else -valor
        if AjusteComandaService.total_ajustado(comanda) + delta < Decimal("0"):
            raise ApplicationError(
                "ajuste_valor_invalido", "Valor do ajuste inválido", 400
            )
