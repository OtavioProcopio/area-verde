from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.domain.enums import FormaPagamento, StatusComanda
from core.domain.models import Comanda, Pagamento


class PagamentoResponse(BaseModel):
    id: int
    caixa_id: Optional[int] = Field(default=None, alias="caixaId")
    comanda_id: int = Field(alias="comandaId")
    forma_pagamento: FormaPagamento = Field(alias="formaPagamento")
    valor: Decimal
    observacao: Optional[str] = None
    criado_em: datetime = Field(alias="criadoEm")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_model(cls, pagamento: Pagamento) -> "PagamentoResponse":
        return cls.model_validate(pagamento)


class FecharComandaRequest(BaseModel):
    forma_pagamento: FormaPagamento = Field(alias="formaPagamento")
    valor_pago: Decimal = Field(alias="valorPago", gt=0)
    observacao: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class FecharComandaResponse(BaseModel):
    id: int
    nome_cliente: str = Field(alias="nomeCliente")
    status: StatusComanda
    total: Decimal
    aberta_em: datetime = Field(alias="abertaEm")
    fechada_em: Optional[datetime] = Field(None, alias="fechadaEm")
    cancelada_em: Optional[datetime] = Field(None, alias="canceladaEm")
    observacao: Optional[str] = None
    pagamentos: List[PagamentoResponse] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_model(
        cls, comanda: Comanda, pagamentos: list[Pagamento]
    ) -> "FecharComandaResponse":
        response = cls.model_validate(comanda)
        response.pagamentos = [
            PagamentoResponse.from_model(pagamento) for pagamento in pagamentos
        ]
        return response
