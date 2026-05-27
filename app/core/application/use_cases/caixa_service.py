from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from core.domain.enums import FormaPagamento, StatusCaixa, TipoMovimentoCaixa
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Caixa, MovimentoCaixa
from core.interfaces.adapters.repositories.i_caixa_repository import ICaixaRepository


class CaixaService:
    def __init__(self, caixa_repository: ICaixaRepository):
        self.caixa_repository = caixa_repository

    def abrir_caixa(
        self,
        valor_inicial: Decimal,
        observacao: Optional[str] = None,
    ) -> Caixa:
        self._ensure_valor_nao_negativo(valor_inicial, "valor_inicial_invalido")
        if self.caixa_repository.get_aberto() is not None:
            raise ApplicationError("caixa_ja_aberto", "Já existe caixa aberto", 400)

        now = datetime.now()
        caixa = Caixa(
            data=date.today(),
            status=StatusCaixa.ABERTO,
            valor_inicial=valor_inicial,
            dinheiro_esperado=valor_inicial,
            dinheiro_informado=None,
            diferenca=None,
            aberto_em=now,
            fechado_em=None,
            criado_em=now,
            atualizado_em=now,
        )

        try:
            self.caixa_repository.save(caixa)
            movimento = self._criar_movimento(
                caixa=caixa,
                tipo=TipoMovimentoCaixa.ABERTURA,
                valor=valor_inicial,
                observacao=observacao,
            )
            self.caixa_repository.save_movimento(movimento)
            self.caixa_repository.commit()
            self.caixa_repository.refresh(caixa)
        except Exception:
            self.caixa_repository.rollback()
            raise

        return self.get_by_id(self._get_caixa_id(caixa))

    def get_caixa_aberto(self) -> Caixa:
        caixa = self.caixa_repository.get_aberto()
        if caixa is None:
            raise NotFoundError(
                "caixa_aberto_nao_encontrado",
                "Nenhum caixa aberto encontrado",
            )
        return caixa

    def listar_caixas(
        self,
        status: Optional[StatusCaixa] = None,
        data: Optional[date] = None,
    ) -> list[Caixa]:
        return self.caixa_repository.list(status=status, data=data)

    def get_by_id(self, caixa_id: int) -> Caixa:
        caixa = self.caixa_repository.get_by_id(caixa_id)
        if caixa is None:
            raise NotFoundError("caixa_nao_encontrado", "Caixa não encontrado")
        return caixa

    def registrar_reforco(
        self,
        caixa_id: int,
        valor: Decimal,
        observacao: Optional[str] = None,
    ) -> Caixa:
        self._ensure_valor_positivo(valor)
        return self._registrar_movimento(
            caixa_id=caixa_id,
            tipo=TipoMovimentoCaixa.REFORCO,
            valor=valor,
            observacao=observacao,
        )

    def registrar_sangria(
        self,
        caixa_id: int,
        valor: Decimal,
        observacao: Optional[str] = None,
    ) -> Caixa:
        self._ensure_valor_positivo(valor)
        return self._registrar_movimento(
            caixa_id=caixa_id,
            tipo=TipoMovimentoCaixa.SANGRIA,
            valor=valor,
            observacao=observacao,
        )

    def fechar_caixa(
        self,
        caixa_id: int,
        dinheiro_informado: Decimal,
        observacao: Optional[str] = None,
    ) -> Caixa:
        self._ensure_valor_nao_negativo(
            dinheiro_informado,
            "dinheiro_informado_invalido",
        )

        try:
            caixa = self._get_caixa_aberto_by_id(caixa_id)
            now = datetime.now()
            caixa.dinheiro_informado = dinheiro_informado
            caixa.diferenca = dinheiro_informado - caixa.dinheiro_esperado
            caixa.status = StatusCaixa.FECHADO
            caixa.fechado_em = now
            caixa.atualizado_em = now

            self.caixa_repository.save(caixa)
            self.caixa_repository.commit()
            self.caixa_repository.refresh(caixa)
        except Exception:
            self.caixa_repository.rollback()
            raise

        return self.get_by_id(caixa_id)

    def aplicar_pagamento(
        self,
        caixa: Caixa,
        forma_pagamento: FormaPagamento,
        valor: Decimal,
    ) -> None:
        self._ensure_caixa_aberto(caixa)
        if forma_pagamento == FormaPagamento.DINHEIRO:
            caixa.dinheiro_esperado += valor
            caixa.atualizado_em = datetime.now()
            self.caixa_repository.save(caixa)

    def _registrar_movimento(
        self,
        caixa_id: int,
        tipo: TipoMovimentoCaixa,
        valor: Decimal,
        observacao: Optional[str],
    ) -> Caixa:
        try:
            caixa = self._get_caixa_aberto_by_id(caixa_id)
            if tipo == TipoMovimentoCaixa.SANGRIA:
                novo_esperado = caixa.dinheiro_esperado - valor
                if novo_esperado < Decimal("0"):
                    raise ApplicationError(
                        "sangria_invalida",
                        "Sangria não pode deixar caixa negativo",
                        400,
                    )
                caixa.dinheiro_esperado = novo_esperado
            else:
                caixa.dinheiro_esperado += valor

            caixa.atualizado_em = datetime.now()
            movimento = self._criar_movimento(
                caixa=caixa,
                tipo=tipo,
                valor=valor,
                observacao=observacao,
            )

            self.caixa_repository.save_movimento(movimento)
            self.caixa_repository.save(caixa)
            self.caixa_repository.commit()
            self.caixa_repository.refresh(caixa)
        except Exception:
            self.caixa_repository.rollback()
            raise

        return self.get_by_id(caixa_id)

    def _get_caixa_aberto_by_id(self, caixa_id: int) -> Caixa:
        caixa = self.get_by_id(caixa_id)
        self._ensure_caixa_aberto(caixa)
        return caixa

    @staticmethod
    def _ensure_caixa_aberto(caixa: Caixa) -> None:
        if caixa.status != StatusCaixa.ABERTO:
            raise ApplicationError(
                "caixa_fechado",
                "Caixa fechado não permite movimentação",
                400,
            )

    @staticmethod
    def _ensure_valor_positivo(valor: Decimal) -> None:
        if valor <= Decimal("0"):
            raise ApplicationError("valor_invalido", "Valor inválido", 400)

    @staticmethod
    def _ensure_valor_nao_negativo(valor: Decimal, code: str) -> None:
        if valor < Decimal("0"):
            raise ApplicationError(code, "Valor inválido", 400)

    @staticmethod
    def _criar_movimento(
        caixa: Caixa,
        tipo: TipoMovimentoCaixa,
        valor: Decimal,
        observacao: Optional[str],
    ) -> MovimentoCaixa:
        return MovimentoCaixa(
            caixa_id=CaixaService._get_caixa_id(caixa),
            tipo=tipo,
            valor=valor,
            observacao=observacao,
            criado_em=datetime.now(),
        )

    @staticmethod
    def _get_caixa_id(caixa: Caixa) -> int:
        if caixa.id is None:
            raise ApplicationError("dados_invalidos", "Caixa inválido", 400)
        return caixa.id
