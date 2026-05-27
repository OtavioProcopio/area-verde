from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from adapter.dtos.fiado_dto import PendenciaResumoResponse
from core.domain.models import Cliente, Comanda


class ClienteRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    apelido: Optional[str] = Field(default=None, max_length=160)
    telefone: Optional[str] = Field(default=None, max_length=40)
    observacao: Optional[str] = Field(default=None, max_length=500)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise ValueError("Nome obrigatório")
        return nome


class ClienteResumoResponse(BaseModel):
    id: int
    nome: str
    apelido: Optional[str] = None
    telefone: Optional[str] = None
    ativo: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, cliente: Cliente) -> "ClienteResumoResponse":
        return cls.model_validate(cliente)


class ClienteDetalheResponse(ClienteResumoResponse):
    observacao: Optional[str] = None
    criado_em: datetime = Field(alias="criadoEm")
    atualizado_em: datetime = Field(alias="atualizadoEm")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_model(cls, cliente: Cliente) -> "ClienteDetalheResponse":
        return cls.model_validate(cliente)


class ClientePendenciasResponse(BaseModel):
    cliente: ClienteResumoResponse
    total_pendente: Decimal = Field(alias="totalPendente")
    total_vencido: Decimal = Field(alias="totalVencido")
    pendencias: list[PendenciaResumoResponse]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(
        cls,
        cliente: Cliente,
        pendencias: list[Comanda],
        total_pendente: Decimal,
        total_vencido: Decimal,
    ) -> "ClientePendenciasResponse":
        return cls(
            cliente=ClienteResumoResponse.from_model(cliente),
            totalPendente=total_pendente,
            totalVencido=total_vencido,
            pendencias=[
                PendenciaResumoResponse.from_model(comanda) for comanda in pendencias
            ],
        )
