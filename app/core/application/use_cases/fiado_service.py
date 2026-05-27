from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from core.application.use_cases.caixa_service import CaixaService
from core.application.use_cases.cliente_service import ClienteService
from core.domain.enums import FormaPagamento, StatusComanda
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Cliente, Comanda, Pagamento
from core.interfaces.adapters.repositories.i_cliente_repository import (
    IClienteRepository,
)
from core.interfaces.adapters.repositories.i_comanda_repository import (
    IComandaRepository,
)
from core.interfaces.adapters.repositories.i_pagamento_repository import (
    IPagamentoRepository,
)


@dataclass(frozen=True)
class QuitarFiadoResult:
    comanda: Comanda
    pagamentos: list[Pagamento]


class FiadoService:
    def __init__(
        self,
        pagamento_repository: IPagamentoRepository,
        comanda_repository: IComandaRepository,
        cliente_repository: IClienteRepository,
        caixa_service: CaixaService,
    ):
        self.pagamento_repository = pagamento_repository
        self.comanda_repository = comanda_repository
        self.cliente_repository = cliente_repository
        self.caixa_service = caixa_service

    def marcar_fiado(
        self,
        comanda_id: int,
        cliente_id: Optional[int] = None,
        vencimento_em: Optional[date] = None,
        observacao: Optional[str] = None,
    ) -> Comanda:
        try:
            try:
                caixa = self.caixa_service.get_caixa_aberto()
            except NotFoundError:
                raise ApplicationError(
                    "caixa_aberto_nao_encontrado",
                    "Nenhum caixa aberto encontrado",
                    400,
                )

            comanda = self._get_comanda(comanda_id)
            self._ensure_aberta(comanda)
            self._ensure_com_consumo(comanda)

            cliente = self._resolve_cliente(comanda, cliente_id)
            ClienteService.ensure_ativo(cliente)
            vencimento = self._resolve_vencimento(vencimento_em)

            comanda.cliente_id = cliente.id
            comanda.nome_cliente_snapshot = ClienteService.nome_operacional(cliente)
            if comanda.caixa_origem_id is None:
                comanda.caixa_origem_id = caixa.id
            comanda.status = StatusComanda.PENDENTE
            comanda.pendente_em = datetime.now()
            comanda.vencimento_em = vencimento
            comanda.observacao = (
                observacao if observacao is not None else comanda.observacao
            )
            comanda.atualizado_em = datetime.now()

            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        return self._get_comanda(comanda_id)

    def listar_pendencias(
        self,
        cliente_id: Optional[int] = None,
        vencidos: Optional[bool] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        nome: Optional[str] = None,
    ) -> list[Comanda]:
        return self.comanda_repository.list_pendencias(
            cliente_id=cliente_id,
            vencidos=vencidos,
            data_inicio=data_inicio,
            data_fim=data_fim,
            nome=nome,
        )

    def listar_vencidas(self) -> list[Comanda]:
        return self.listar_pendencias(vencidos=True)

    def consultar_pendencia(self, comanda_id: int) -> Comanda:
        comanda = self._get_comanda(comanda_id)
        self._ensure_pendente(comanda)
        return comanda

    def quitar(
        self,
        comanda_id: int,
        forma_pagamento: FormaPagamento,
        valor_pago: Decimal,
        observacao: Optional[str] = None,
    ) -> QuitarFiadoResult:
        self._ensure_forma_quitacao_valida(forma_pagamento)
        if valor_pago <= Decimal("0"):
            raise ApplicationError("valor_pago_invalido", "Valor pago inválido", 400)

        try:
            comanda = self._get_comanda(comanda_id)
            self._ensure_pendente(comanda)
            if valor_pago != comanda.total:
                raise ApplicationError(
                    "valor_pago_invalido",
                    "Valor pago deve ser igual ao total da pendência",
                    400,
                )

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

            now = datetime.now()
            comanda.status = StatusComanda.FECHADA
            comanda.fechada_em = now
            comanda.atualizado_em = now
            self.comanda_repository.save(comanda)
            self.comanda_repository.commit()
            self.comanda_repository.refresh(comanda)
        except Exception:
            self.comanda_repository.rollback()
            raise

        pagamentos = self.pagamento_repository.listar_por_comanda(comanda_id)
        return QuitarFiadoResult(
            comanda=self._get_comanda(comanda_id), pagamentos=pagamentos
        )

    def _get_comanda(self, comanda_id: int) -> Comanda:
        comanda = self.comanda_repository.get_by_id(comanda_id)
        if comanda is None:
            raise NotFoundError("comanda_nao_encontrada", "Comanda não encontrada")
        return comanda

    def _resolve_cliente(
        self,
        comanda: Comanda,
        cliente_id: Optional[int],
    ) -> Cliente:
        resolved_id = cliente_id if cliente_id is not None else comanda.cliente_id
        if resolved_id is None:
            raise ApplicationError(
                "cliente_obrigatorio_para_fiado",
                "Cliente cadastrado é obrigatório para fiado",
                400,
            )

        cliente = self.cliente_repository.get_by_id(resolved_id)
        if cliente is None:
            raise NotFoundError("cliente_nao_encontrado", "Cliente não encontrado")
        return cliente

    @staticmethod
    def _resolve_vencimento(vencimento_em: Optional[date]) -> date:
        hoje = date.today()
        if vencimento_em is None:
            return hoje + timedelta(days=7)
        if vencimento_em < hoje:
            raise ApplicationError(
                "vencimento_invalido",
                "Vencimento não pode ser anterior à data atual",
                400,
            )
        return vencimento_em

    @staticmethod
    def _ensure_aberta(comanda: Comanda) -> None:
        if comanda.status != StatusComanda.ABERTA:
            raise ApplicationError("comanda_nao_aberta", "Comanda não está aberta", 400)

    @staticmethod
    def _ensure_pendente(comanda: Comanda) -> None:
        if comanda.status != StatusComanda.PENDENTE:
            raise ApplicationError(
                "comanda_nao_pendente",
                "Comanda não está pendente",
                400,
            )

    @staticmethod
    def _ensure_com_consumo(comanda: Comanda) -> None:
        if comanda.total <= Decimal("0") or not comanda.itens:
            raise ApplicationError(
                "comanda_sem_consumo",
                "Comanda sem consumo para fiado",
                400,
            )

    @staticmethod
    def _ensure_forma_quitacao_valida(forma_pagamento: FormaPagamento) -> None:
        if forma_pagamento == FormaPagamento.FIADO:
            raise ApplicationError(
                "fiado_nao_pode_quitar_fiado",
                "FIADO não pode quitar fiado",
                400,
            )
        if forma_pagamento not in {
            FormaPagamento.DINHEIRO,
            FormaPagamento.PIX,
            FormaPagamento.CARTAO,
        }:
            raise ApplicationError(
                "forma_pagamento_invalida",
                "Forma de pagamento inválida",
                400,
            )
