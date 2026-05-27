from datetime import datetime
from typing import List

from adapter.dtos.pagamento_dto import (
    FecharComandaRequest,
    FecharComandaResponse,
    PagamentoResponse,
)
from core.domain.enums import FormaPagamento, StatusComanda
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Pagamento
from core.interfaces.adapters.repositories.i_comanda_repository import (
    IComandaRepository,
)
from core.interfaces.adapters.repositories.i_pagamento_repository import (
    IPagamentoRepository,
)


class PagamentoService:
    def __init__(
        self,
        pagamento_repository: IPagamentoRepository,
        comanda_repository: IComandaRepository,
    ):
        self.pagamento_repository = pagamento_repository
        self.comanda_repository = comanda_repository

    def fechar_comanda(
        self, comanda_id: int, request: FecharComandaRequest
    ) -> FecharComandaResponse:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if not comanda:
            raise NotFoundError("comanda_nao_encontrada", "Comanda não encontrada")

        if comanda.status != StatusComanda.ABERTA:
            raise ApplicationError("comanda_nao_aberta", "Comanda não está aberta", 400)

        if comanda.total <= 0:
            raise ApplicationError(
                "comanda_sem_consumo", "Comanda sem consumo para fechamento", 400
            )

        if request.forma_pagamento == FormaPagamento.FIADO:
            raise ApplicationError(
                "fiado_nao_implementado", "Fiado ainda não implementado", 400
            )

        if request.valor_pago != comanda.total:
            raise ApplicationError(
                "valor_pago_invalido",
                "Valor pago deve ser igual ao total da comanda",
                400,
            )

        try:
            pagamento = Pagamento(
                comanda_id=comanda.id,
                forma_pagamento=request.forma_pagamento,
                valor=request.valor_pago,
                observacao=request.observacao,
            )

            self.pagamento_repository.criar_pagamento(pagamento)

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

        response_model = FecharComandaResponse.model_validate(comanda)
        response_model.pagamentos = [
            PagamentoResponse.model_validate(p) for p in pagamentos_comanda
        ]

        return response_model

    def listar_pagamentos(self, comanda_id: int) -> List[PagamentoResponse]:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if not comanda:
            raise NotFoundError("comanda_nao_encontrada", "Comanda não encontrada")

        pagamentos = self.pagamento_repository.listar_por_comanda(comanda_id)
        return [PagamentoResponse.model_validate(p) for p in pagamentos]
