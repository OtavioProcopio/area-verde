from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.application.use_cases.ajuste_comanda_service import AjusteComandaService
from core.domain.enums import StatusComanda, TipoAjusteComanda
from core.domain.models import AjusteComanda, Comanda, ItemComanda


class CriarComandaRequest(BaseModel):
    nome_cliente: Optional[str] = Field(
        default=None,
        alias="nomeCliente",
        max_length=160,
    )
    cliente_id: Optional[int] = Field(default=None, alias="clienteId")
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_nome_ou_cliente(self) -> "CriarComandaRequest":
        if self.cliente_id is not None:
            if self.nome_cliente is not None:
                self.nome_cliente = self.nome_cliente.strip() or None
            return self

        if self.nome_cliente is None or not self.nome_cliente.strip():
            raise ValueError("Nome obrigatório")

        self.nome_cliente = self.nome_cliente.strip()
        return self


class VincularClienteComandaRequest(BaseModel):
    cliente_id: int = Field(alias="clienteId")

    model_config = ConfigDict(populate_by_name=True)


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


class AjusteComandaResponse(BaseModel):
    id: int
    tipo: TipoAjusteComanda
    valor: float
    descricao: str
    criado_em: datetime = Field(alias="criadoEm")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, ajuste: AjusteComanda) -> "AjusteComandaResponse":
        if ajuste.id is None:
            raise ValueError("Ajuste sem id")

        return cls(
            id=ajuste.id,
            tipo=ajuste.tipo,
            valor=float(ajuste.valor),
            descricao=ajuste.descricao,
            criadoEm=ajuste.criado_em,
        )


class AplicarAjusteComandaRequest(BaseModel):
    tipo: TipoAjusteComanda
    valor: Decimal
    descricao: str

    model_config = ConfigDict(populate_by_name=True)


class ComandaResumoResponse(BaseModel):
    id: int
    caixa_origem_id: Optional[int] = Field(default=None, alias="caixaOrigemId")
    cliente_id: Optional[int] = Field(default=None, alias="clienteId")
    nome_cliente: str = Field(alias="nomeCliente")
    nome_cliente_snapshot: Optional[str] = Field(
        default=None,
        alias="nomeClienteSnapshot",
    )
    status: StatusComanda
    total: float
    aberta_em: datetime = Field(alias="abertaEm")
    pendente_em: Optional[datetime] = Field(default=None, alias="pendenteEm")
    vencimento_em: Optional[date] = Field(default=None, alias="vencimentoEm")
    quantidade_itens: int = Field(alias="quantidadeItens")
    total_ajustado: float = Field(alias="totalAjustado")
    saldo_restante: float = Field(alias="saldoRestante")
    ajustes: List[AjusteComandaResponse] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, comanda: Comanda) -> "ComandaResumoResponse":
        if comanda.id is None:
            raise ValueError("Comanda sem id")

        return cls(
            id=comanda.id,
            caixaOrigemId=comanda.caixa_origem_id,
            clienteId=comanda.cliente_id,
            nomeCliente=comanda.nome_cliente,
            nomeClienteSnapshot=comanda.nome_cliente_snapshot,
            status=comanda.status,
            total=float(comanda.total),
            abertaEm=comanda.aberta_em,
            pendenteEm=comanda.pendente_em,
            vencimentoEm=comanda.vencimento_em,
            quantidadeItens=len(comanda.itens),
            totalAjustado=float(AjusteComandaService.total_ajustado(comanda)),
            saldoRestante=float(AjusteComandaService.saldo_restante(comanda)),
            ajustes=[
                AjusteComandaResponse.from_model(ajuste) for ajuste in comanda.ajustes
            ],
        )


class ComandaDetalheResponse(BaseModel):
    id: int
    caixa_origem_id: Optional[int] = Field(default=None, alias="caixaOrigemId")
    cliente_id: Optional[int] = Field(default=None, alias="clienteId")
    nome_cliente: str = Field(alias="nomeCliente")
    nome_cliente_snapshot: Optional[str] = Field(
        default=None,
        alias="nomeClienteSnapshot",
    )
    status: StatusComanda
    total: float
    aberta_em: datetime = Field(alias="abertaEm")
    fechada_em: Optional[datetime] = Field(alias="fechadaEm")
    cancelada_em: Optional[datetime] = Field(alias="canceladaEm")
    pendente_em: Optional[datetime] = Field(default=None, alias="pendenteEm")
    vencimento_em: Optional[date] = Field(default=None, alias="vencimentoEm")
    observacao: Optional[str]
    itens: list[ItemComandaResponse]
    total_ajustado: float = Field(alias="totalAjustado")
    saldo_restante: float = Field(alias="saldoRestante")
    ajustes: List[AjusteComandaResponse] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, comanda: Comanda) -> "ComandaDetalheResponse":
        if comanda.id is None:
            raise ValueError("Comanda sem id")

        return cls(
            id=comanda.id,
            caixaOrigemId=comanda.caixa_origem_id,
            clienteId=comanda.cliente_id,
            nomeCliente=comanda.nome_cliente,
            nomeClienteSnapshot=comanda.nome_cliente_snapshot,
            status=comanda.status,
            total=float(comanda.total),
            abertaEm=comanda.aberta_em,
            fechadaEm=comanda.fechada_em,
            canceladaEm=comanda.cancelada_em,
            pendenteEm=comanda.pendente_em,
            vencimentoEm=comanda.vencimento_em,
            observacao=comanda.observacao,
            itens=[ItemComandaResponse.from_model(item) for item in comanda.itens],
            totalAjustado=float(AjusteComandaService.total_ajustado(comanda)),
            saldoRestante=float(AjusteComandaService.saldo_restante(comanda)),
            ajustes=[
                AjusteComandaResponse.from_model(ajuste) for ajuste in comanda.ajustes
            ],
        )
