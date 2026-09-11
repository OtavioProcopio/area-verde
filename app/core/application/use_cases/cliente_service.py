import re
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
        nome_normalizado = self._normalize_required(nome)
        telefone_normalizado = self._normalize_optional(telefone)
        self._ensure_cliente_unico(
            nome=nome_normalizado,
            telefone=telefone_normalizado,
        )
        cliente = Cliente(
            nome=nome_normalizado,
            apelido=self._normalize_optional(apelido),
            telefone=telefone_normalizado,
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
            nome_normalizado = self._normalize_required(nome)
            telefone_normalizado = self._normalize_optional(telefone)
            self._ensure_cliente_unico(
                nome=nome_normalizado,
                telefone=telefone_normalizado,
                ignore_cliente_id=cliente_id,
            )
            cliente.nome = nome_normalizado
            cliente.apelido = self._normalize_optional(apelido)
            cliente.telefone = telefone_normalizado
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
            if ativo:
                self._ensure_cliente_unico(
                    nome=cliente.nome,
                    telefone=cliente.telefone,
                    ignore_cliente_id=cliente_id,
                )
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

    def _ensure_cliente_unico(
        self,
        nome: str,
        telefone: Optional[str],
        ignore_cliente_id: Optional[int] = None,
    ) -> None:
        nome_key = self._normalize_nome_key(nome)
        telefone_key = self._normalize_telefone_key(telefone)

        for cliente in self.cliente_repository.list_ativos():
            if ignore_cliente_id is not None and cliente.id == ignore_cliente_id:
                continue

            if self._normalize_nome_key(cliente.nome) == nome_key:
                raise ApplicationError(
                    "cliente_duplicado",
                    "Já existe cliente ativo com os mesmos dados",
                    409,
                )

            if (
                telefone_key
                and self._normalize_telefone_key(cliente.telefone) == telefone_key
            ):
                raise ApplicationError(
                    "cliente_duplicado",
                    "Já existe cliente ativo com os mesmos dados",
                    409,
                )

    @staticmethod
    def _normalize_nome_key(value: str) -> str:
        return value.strip().casefold()

    @staticmethod
    def _normalize_telefone_key(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = re.sub(r"[\s().-]", "", value)
        return normalized or None
