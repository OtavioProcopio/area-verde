from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from adapter.dtos.categoria_produto_dto import CategoriaProdutoResumoResponse
from core.domain.enums import TipoProduto, UnidadeEstoque
from core.domain.models import Produto


class ProdutoRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=160)
    categoria_id: int = Field(alias="categoriaId")
    preco_venda: Decimal = Field(alias="precoVenda")
    tipo_produto: TipoProduto = Field(default=TipoProduto.SIMPLES, alias="tipoProduto")
    controla_estoque: bool = Field(alias="controlaEstoque")
    unidade_estoque: Optional[UnidadeEstoque] = Field(
        default=None, alias="unidadeEstoque"
    )
    quantidade_estoque: Optional[Decimal] = Field(
        default=None, alias="quantidadeEstoque"
    )
    quantidade_baixa_por_venda: Optional[Decimal] = Field(
        default=None, alias="quantidadeBaixaPorVenda"
    )
    estoque_minimo: Optional[Decimal] = Field(default=None, alias="estoqueMinimo")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise ValueError("Nome obrigatório")
        return nome


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    categoria: CategoriaProdutoResumoResponse
    preco_venda: float = Field(alias="precoVenda")
    tipo_produto: TipoProduto = Field(alias="tipoProduto")
    controla_estoque: bool = Field(alias="controlaEstoque")
    unidade_estoque: UnidadeEstoque = Field(alias="unidadeEstoque")
    quantidade_estoque: float = Field(alias="quantidadeEstoque")
    quantidade_baixa_por_venda: float = Field(alias="quantidadeBaixaPorVenda")
    estoque_minimo: float = Field(alias="estoqueMinimo")
    ativo: bool
    criado_em: datetime = Field(alias="criadoEm")
    atualizado_em: datetime = Field(alias="atualizadoEm")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, produto: Produto) -> "ProdutoResponse":
        if produto.id is None:
            raise ValueError("Produto sem id")

        if produto.categoria is None:
            raise ValueError("Produto sem categoria carregada")

        return cls(
            id=produto.id,
            nome=produto.nome,
            categoria=CategoriaProdutoResumoResponse.from_model(produto.categoria),
            precoVenda=float(produto.preco_venda),
            tipoProduto=produto.tipo_produto,
            controlaEstoque=produto.controla_estoque,
            unidadeEstoque=produto.unidade_estoque,
            quantidadeEstoque=float(produto.quantidade_estoque),
            quantidadeBaixaPorVenda=float(produto.quantidade_baixa_por_venda),
            estoqueMinimo=float(produto.estoque_minimo),
            ativo=produto.ativo,
            criadoEm=produto.criado_em,
            atualizadoEm=produto.atualizado_em,
        )
