from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from adapter.dtos.comanda_dto import ItemComandaResponse
from adapter.dtos.pagamento_dto import PagamentoResponse
from core.domain.enums import FormaPagamento, StatusComanda
from core.domain.models import Cliente, Comanda, Pagamento


class ClienteFiadoResponse(BaseModel):
    id: int
    nome: str
    apelido: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, cliente: Optional[Cliente]) -> Optional["ClienteFiadoResponse"]:
        if cliente is None:
            return None
        return cls.model_validate(cliente)


class MarcarFiadoRequest(BaseModel):
    cliente_id: Optional[int] = Field(default=None, alias="clienteId")
    vencimento_em: Optional[date] = Field(default=None, alias="vencimentoEm")
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)


class QuitarFiadoRequest(BaseModel):
    forma_pagamento: FormaPagamento = Field(alias="formaPagamento")
    valor_pago: Decimal = Field(alias="valorPago", gt=0)
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)


class PendenciaResumoResponse(BaseModel):
    comanda_id: int = Field(alias="comandaId")
    cliente: Optional[ClienteFiadoResponse] = None
    nome_cliente: str = Field(alias="nomeCliente")
    total: Decimal
    status: StatusComanda
    aberta_em: datetime = Field(alias="abertaEm")
    vencimento_em: Optional[date] = Field(alias="vencimentoEm")
    vencida: bool

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, comanda: Comanda) -> "PendenciaResumoResponse":
        if comanda.id is None:
            raise ValueError("Comanda sem id")

        hoje = date.today()
        vencida = (
            comanda.status == StatusComanda.PENDENTE
            and comanda.vencimento_em is not None
            and comanda.vencimento_em < hoje
        )
        return cls(
            comandaId=comanda.id,
            cliente=ClienteFiadoResponse.from_model(comanda.cliente),
            nomeCliente=comanda.nome_cliente,
            total=comanda.total,
            status=comanda.status,
            abertaEm=comanda.aberta_em,
            vencimentoEm=comanda.vencimento_em,
            vencida=vencida,
        )


class PendenciaDetalheResponse(PendenciaResumoResponse):
    fechada_em: Optional[datetime] = Field(default=None, alias="fechadaEm")
    cancelada_em: Optional[datetime] = Field(default=None, alias="canceladaEm")
    observacao: Optional[str] = None
    itens: list[ItemComandaResponse] = Field(default_factory=list)
    pagamentos: list[PagamentoResponse] = Field(default_factory=list)

    @classmethod
    def from_model(cls, comanda: Comanda) -> "PendenciaDetalheResponse":
        resumo = PendenciaResumoResponse.from_model(comanda)
        return cls(
            **resumo.model_dump(by_alias=True),
            fechadaEm=comanda.fechada_em,
            canceladaEm=comanda.cancelada_em,
            observacao=comanda.observacao,
            itens=[ItemComandaResponse.from_model(item) for item in comanda.itens],
            pagamentos=[
                PagamentoResponse.from_model(pagamento)
                for pagamento in comanda.pagamentos
            ],
        )


class QuitarFiadoResponse(BaseModel):
    id: int
    status: StatusComanda
    total: Decimal
    vencimento_em: Optional[date] = Field(alias="vencimentoEm")
    fechada_em: Optional[datetime] = Field(alias="fechadaEm")
    pagamentos: list[PagamentoResponse]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(
        cls,
        comanda: Comanda,
        pagamentos: list[Pagamento],
    ) -> "QuitarFiadoResponse":
        if comanda.id is None:
            raise ValueError("Comanda sem id")

        return cls(
            id=comanda.id,
            status=comanda.status,
            total=comanda.total,
            vencimentoEm=comanda.vencimento_em,
            fechadaEm=comanda.fechada_em,
            pagamentos=[
                PagamentoResponse.from_model(pagamento) for pagamento in pagamentos
            ],
        )
