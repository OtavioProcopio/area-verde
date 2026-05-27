from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from core.domain.enums import FormaPagamento, StatusComanda


class PagamentoResponse(BaseModel):
    id: int
    comanda_id: int = Field(alias="comandaId")
    forma_pagamento: FormaPagamento = Field(alias="formaPagamento")
    valor: Decimal
    criado_em: datetime = Field(alias="criadoEm")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


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
    pagamentos: List[PagamentoResponse] = []

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
