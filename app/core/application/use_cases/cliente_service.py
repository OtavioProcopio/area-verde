from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import Cliente, Comanda
from core.interfaces.adapters.repositories.i_cliente_repository import (
    IClienteRepository,
)
from core.interfaces.adapters.repositories.i_comanda_repository import (
    IComandaRepository,
)


class ClienteService:
    def __init__(
        self,
        cliente_repository: IClienteRepository,
        comanda_repository: IComandaRepository,
    ):
        self.cliente_repository = cliente_repository
        self.comanda_repository = comanda_repository

    def create(
        self,
        nome: str,
        apelido: Optional[str] = None,
        telefone: Optional[str] = None,
        observacao: Optional[str] = None,
    ) -> Cliente:
        now = datetime.now()
        cliente = Cliente(
            nome=self._normalize_required(nome),
            apelido=self._normalize_optional(apelido),
            telefone=self._normalize_optional(telefone),
            observacao=self._normalize_optional(observacao),
            ativo=True,
            criado_em=now,
            atualizado_em=now,
        )

        try:
            self.cliente_repository.create(cliente)
            self.cliente_repository.commit()
            self.cliente_repository.refresh(cliente)
        except Exception:
            self.cliente_repository.rollback()
            raise

        return cliente

    def listar(
        self,
        ativo: Optional[bool] = None,
        nome: Optional[str] = None,
        telefone: Optional[str] = None,
    ) -> list[Cliente]:
        return self.cliente_repository.list(ativo=ativo, nome=nome, telefone=telefone)

    def get_by_id(self, cliente_id: int) -> Cliente:
        cliente = self.cliente_repository.get_by_id(cliente_id)
        if cliente is None:
            raise NotFoundError("cliente_nao_encontrado", "Cliente não encontrado")
        return cliente

    def update(
        self,
        cliente_id: int,
        nome: str,
        apelido: Optional[str] = None,
        telefone: Optional[str] = None,
        observacao: Optional[str] = None,
    ) -> Cliente:
        try:
            cliente = self.get_by_id(cliente_id)
            cliente.nome = self._normalize_required(nome)
            cliente.apelido = self._normalize_optional(apelido)
            cliente.telefone = self._normalize_optional(telefone)
            cliente.observacao = self._normalize_optional(observacao)
            cliente.atualizado_em = datetime.now()
            self.cliente_repository.save(cliente)
            self.cliente_repository.commit()
            self.cliente_repository.refresh(cliente)
        except Exception:
            self.cliente_repository.rollback()
            raise

        return cliente

    def ativar(self, cliente_id: int) -> Cliente:
        return self._set_ativo(cliente_id, True)

    def inativar(self, cliente_id: int) -> Cliente:
        return self._set_ativo(cliente_id, False)

    def listar_pendencias(self, cliente_id: int) -> list[Comanda]:
        self.get_by_id(cliente_id)
        return self.comanda_repository.list_pendencias(cliente_id=cliente_id)

    def total_pendente(self, cliente_id: int) -> Decimal:
        pendencias = self.listar_pendencias(cliente_id)
        return sum((comanda.total for comanda in pendencias), Decimal("0.00"))

    def total_vencido(self, cliente_id: int) -> Decimal:
        hoje = datetime.now().date()
        pendencias = self.listar_pendencias(cliente_id)
        return sum(
            (
                comanda.total
                for comanda in pendencias
                if comanda.vencimento_em is not None and comanda.vencimento_em < hoje
            ),
            Decimal("0.00"),
        )

    def _set_ativo(self, cliente_id: int, ativo: bool) -> Cliente:
        try:
            cliente = self.get_by_id(cliente_id)
            cliente.ativo = ativo
            cliente.atualizado_em = datetime.now()
            self.cliente_repository.save(cliente)
            self.cliente_repository.commit()
            self.cliente_repository.refresh(cliente)
        except Exception:
            self.cliente_repository.rollback()
            raise

        return cliente

    @staticmethod
    def ensure_ativo(cliente: Cliente) -> None:
        if not cliente.ativo:
            raise ApplicationError("cliente_inativo", "Cliente inativo", 400)

    @staticmethod
    def nome_operacional(cliente: Cliente) -> str:
        return cliente.apelido or cliente.nome

    @staticmethod
    def _normalize_required(value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ApplicationError("dados_invalidos", "Nome obrigatório", 400)
        return normalized

    @staticmethod
    def _normalize_optional(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
