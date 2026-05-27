from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.domain.enums import FormaPagamento, StatusCaixa, TipoMovimentoCaixa
from core.domain.models import Caixa, MovimentoCaixa, Pagamento


class AbrirCaixaRequest(BaseModel):
    valor_inicial: Decimal = Field(alias="valorInicial", ge=0)
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)


class MovimentoCaixaRequest(BaseModel):
    valor: Decimal = Field(gt=0)
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)


class FecharCaixaRequest(BaseModel):
    dinheiro_informado: Decimal = Field(alias="dinheiroInformado", ge=0)
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)


class PagamentoCaixaResponse(BaseModel):
    id: int
    caixa_id: int = Field(alias="caixaId")
    comanda_id: int = Field(alias="comandaId")
    forma_pagamento: FormaPagamento = Field(alias="formaPagamento")
    valor: Decimal
    observacao: Optional[str] = None
    criado_em: datetime = Field(alias="criadoEm")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_model(cls, pagamento: Pagamento) -> "PagamentoCaixaResponse":
        return cls.model_validate(pagamento)


class MovimentoCaixaResponse(BaseModel):
    id: int
    caixa_id: int = Field(alias="caixaId")
    tipo: TipoMovimentoCaixa
    valor: Decimal
    observacao: Optional[str] = None
    criado_em: datetime = Field(alias="criadoEm")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_model(cls, movimento: MovimentoCaixa) -> "MovimentoCaixaResponse":
        return cls.model_validate(movimento)


class CaixaResumoResponse(BaseModel):
    id: int
    data: date
    status: StatusCaixa
    valor_inicial: Decimal = Field(alias="valorInicial")
    dinheiro_esperado: Decimal = Field(alias="dinheiroEsperado")
    dinheiro_informado: Optional[Decimal] = Field(
        default=None, alias="dinheiroInformado"
    )
    diferenca: Optional[Decimal] = None
    aberto_em: datetime = Field(alias="abertoEm")
    fechado_em: Optional[datetime] = Field(default=None, alias="fechadoEm")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_model(cls, caixa: Caixa) -> "CaixaResumoResponse":
        return cls.model_validate(caixa)


class CaixaDetalheResponse(CaixaResumoResponse):
    pagamentos: List[PagamentoCaixaResponse] = Field(default_factory=list)
    movimentos: List[MovimentoCaixaResponse] = Field(default_factory=list)

    @classmethod
    def from_model(cls, caixa: Caixa) -> "CaixaDetalheResponse":
        response = cls.model_validate(caixa)
        response.pagamentos = [
            PagamentoCaixaResponse.from_model(pagamento)
            for pagamento in sorted(caixa.pagamentos, key=lambda item: item.criado_em)
        ]
        response.movimentos = [
            MovimentoCaixaResponse.from_model(movimento)
            for movimento in sorted(caixa.movimentos, key=lambda item: item.criado_em)
        ]
        return response
