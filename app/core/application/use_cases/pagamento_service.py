from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from core.application.use_cases.caixa_service import CaixaService
from core.domain.enums import FormaPagamento, StatusComanda
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Comanda, Pagamento
from core.interfaces.adapters.repositories.i_comanda_repository import (
    IComandaRepository,
)
from core.interfaces.adapters.repositories.i_pagamento_repository import (
    IPagamentoRepository,
)


@dataclass(frozen=True)
class FechamentoComandaResult:
    comanda: Comanda
    pagamentos: list[Pagamento]


class PagamentoService:
    def __init__(
        self,
        pagamento_repository: IPagamentoRepository,
        comanda_repository: IComandaRepository,
        caixa_service: CaixaService,
    ):
        self.pagamento_repository = pagamento_repository
        self.comanda_repository = comanda_repository
        self.caixa_service = caixa_service

    def fechar_comanda(
        self,
        comanda_id: int,
        forma_pagamento: FormaPagamento,
        valor_pago: Decimal,
        observacao: Optional[str] = None,
    ) -> FechamentoComandaResult:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if not comanda:
            raise NotFoundError("comanda_nao_encontrada", "Comanda não encontrada")

        if comanda.status != StatusComanda.ABERTA:
            raise ApplicationError("comanda_nao_aberta", "Comanda não está aberta", 400)

        if comanda.total <= 0:
            raise ApplicationError(
                "comanda_sem_consumo", "Comanda sem consumo para fechamento", 400
            )

        if forma_pagamento == FormaPagamento.FIADO:
            raise ApplicationError(
                "forma_pagamento_invalida",
                "FIADO deve ser tratado pelo módulo de pendências",
                400,
            )

        if valor_pago != comanda.total:
            raise ApplicationError(
                "valor_pago_invalido",
                "Valor pago deve ser igual ao total da comanda",
                400,
            )

        try:
            try:
                caixa = self.caixa_service.get_caixa_aberto()
            except NotFoundError:
                raise ApplicationError(
                    "caixa_aberto_nao_encontrado",
                    "Nenhum caixa aberto encontrado",
                    400,
                )
            pagamento = Pagamento(
                caixa_id=caixa.id,
                comanda_id=comanda.id,
                forma_pagamento=forma_pagamento,
                valor=valor_pago,
                observacao=observacao,
            )

            self.pagamento_repository.criar_pagamento(pagamento)
            self.caixa_service.aplicar_pagamento(
                caixa=caixa,
                forma_pagamento=forma_pagamento,
                valor=valor_pago,
            )

            comanda.status = StatusComanda.FECHADA
            comanda.fechada_em = datetime.now()
            comanda.atualizado_em = datetime.now()

            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)

        except Exception as e:
            self.comanda_repository.rollback()
            raise e

        pagamentos_comanda = self.pagamento_repository.listar_por_comanda(comanda_id)
        return FechamentoComandaResult(
            comanda=comanda,
            pagamentos=pagamentos_comanda,
        )

    def listar_pagamentos(self, comanda_id: int) -> List[Pagamento]:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if not comanda:
            raise NotFoundError("comanda_nao_encontrada", "Comanda não encontrada")

        return self.pagamento_repository.listar_por_comanda(comanda_id)
