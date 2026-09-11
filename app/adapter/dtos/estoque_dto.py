from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from adapter.dtos.categoria_produto_dto import CategoriaProdutoResumoResponse
from core.domain.enums import (
    OrigemMovimentoEstoque,
    TipoMovimentoEstoque,
    UnidadeEstoque,
)
from core.domain.models import MovimentoEstoque, Produto


class EntradaEstoqueRequest(BaseModel):
    quantidade: Decimal
    observacao: Optional[str] = Field(default=None, max_length=500)


class AjusteEstoqueRequest(BaseModel):
    novo_estoque: Decimal = Field(alias="novoEstoque")
    observacao: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(populate_by_name=True)


class EstoqueProdutoResponse(BaseModel):
    produto_id: int = Field(alias="produtoId")
    nome: str
    categoria: CategoriaProdutoResumoResponse
    unidade_estoque: UnidadeEstoque = Field(alias="unidadeEstoque")
    quantidade_estoque: float = Field(alias="quantidadeEstoque")
    estoque_minimo: float = Field(alias="estoqueMinimo")
    estoque_baixo: bool = Field(alias="estoqueBaixo")
    estoque_negativo: bool = Field(alias="estoqueNegativo")
    ativo: bool

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, produto: Produto) -> "EstoqueProdutoResponse":
        if produto.id is None:
            raise ValueError("Produto sem id")

        if produto.categoria is None:
            raise ValueError("Produto sem categoria carregada")

        estoque_negativo = produto.quantidade_estoque < Decimal("0")
        estoque_baixo = produto.quantidade_estoque <= produto.estoque_minimo

        return cls(
            produtoId=produto.id,
            nome=produto.nome,
            categoria=CategoriaProdutoResumoResponse.from_model(produto.categoria),
            unidadeEstoque=produto.unidade_estoque,
            quantidadeEstoque=float(produto.quantidade_estoque),
            estoqueMinimo=float(produto.estoque_minimo),
            estoqueBaixo=estoque_baixo,
            estoqueNegativo=estoque_negativo,
            ativo=produto.ativo,
        )


class MovimentoEstoqueResponse(BaseModel):
    id: int
    produto_id: int = Field(alias="produtoId")
    produto_nome: str = Field(alias="produtoNome")
    tipo: TipoMovimentoEstoque
    origem: OrigemMovimentoEstoque
    quantidade: float
    estoque_antes: float = Field(alias="estoqueAntes")
    estoque_depois: float = Field(alias="estoqueDepois")
    observacao: Optional[str]
    criado_em: datetime = Field(alias="criadoEm")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, movimento: MovimentoEstoque) -> "MovimentoEstoqueResponse":
        if movimento.id is None:
            raise ValueError("Movimento sem id")

        if movimento.produto is None:
            raise ValueError("Movimento sem produto carregado")

        return cls(
            id=movimento.id,
            produtoId=movimento.produto_id,
            produtoNome=movimento.produto.nome,
            tipo=movimento.tipo,
            origem=movimento.origem,
            quantidade=float(movimento.quantidade),
            estoqueAntes=float(movimento.estoque_antes),
            estoqueDepois=float(movimento.estoque_depois),
            observacao=movimento.observacao,
            criadoEm=movimento.criado_em,
        )
