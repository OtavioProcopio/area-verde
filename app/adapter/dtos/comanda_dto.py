from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.enums import StatusComanda
from core.domain.models import Comanda, ItemComanda


class CriarComandaRequest(BaseModel):
    nome_cliente: str = Field(alias="nomeCliente", min_length=1, max_length=160)
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nome_cliente")
    @classmethod
    def validate_nome_cliente(cls, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise ValueError("Nome obrigatório")
        return nome


class AdicionarItemComandaRequest(BaseModel):
    produto_id: int = Field(alias="produtoId")
    quantidade: Decimal

    model_config = ConfigDict(populate_by_name=True)


class AlterarQuantidadeItemRequest(BaseModel):
    quantidade: Decimal = Field(default=Decimal("1"))


class CancelarComandaRequest(BaseModel):
    motivo: Optional[str] = Field(default=None, max_length=500)


class ItemComandaResponse(BaseModel):
    id: int
    produto_id: Optional[int] = Field(alias="produtoId")
    nome_produto: str = Field(alias="nomeProduto")
    quantidade: float
    preco_unitario: float = Field(alias="precoUnitario")
    quantidade_baixada_estoque: float = Field(alias="quantidadeBaixadaEstoque")
    total_item: float = Field(alias="totalItem")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, item: ItemComanda) -> "ItemComandaResponse":
        if item.id is None:
            raise ValueError("Item sem id")

        return cls(
            id=item.id,
            produtoId=item.produto_id,
            nomeProduto=item.nome_produto_snapshot,
            quantidade=float(item.quantidade),
            precoUnitario=float(item.preco_unitario_snapshot),
            quantidadeBaixadaEstoque=float(item.quantidade_baixada_estoque),
            totalItem=float(item.total_item),
        )


class ComandaResumoResponse(BaseModel):
    id: int
    nome_cliente: str = Field(alias="nomeCliente")
    status: StatusComanda
    total: float
    aberta_em: datetime = Field(alias="abertaEm")
    quantidade_itens: int = Field(alias="quantidadeItens")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, comanda: Comanda) -> "ComandaResumoResponse":
        if comanda.id is None:
            raise ValueError("Comanda sem id")

        return cls(
            id=comanda.id,
            nomeCliente=comanda.nome_cliente,
            status=comanda.status,
            total=float(comanda.total),
            abertaEm=comanda.aberta_em,
            quantidadeItens=len(comanda.itens),
        )


class ComandaDetalheResponse(BaseModel):
    id: int
    nome_cliente: str = Field(alias="nomeCliente")
    status: StatusComanda
    total: float
    aberta_em: datetime = Field(alias="abertaEm")
    fechada_em: Optional[datetime] = Field(alias="fechadaEm")
    cancelada_em: Optional[datetime] = Field(alias="canceladaEm")
    observacao: Optional[str]
    itens: list[ItemComandaResponse]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, comanda: Comanda) -> "ComandaDetalheResponse":
        if comanda.id is None:
            raise ValueError("Comanda sem id")

        return cls(
            id=comanda.id,
            nomeCliente=comanda.nome_cliente,
            status=comanda.status,
            total=float(comanda.total),
            abertaEm=comanda.aberta_em,
            fechadaEm=comanda.fechada_em,
            canceladaEm=comanda.cancelada_em,
            observacao=comanda.observacao,
            itens=[ItemComandaResponse.from_model(item) for item in comanda.itens],
        )
