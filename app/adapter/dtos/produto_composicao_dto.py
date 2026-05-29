from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.domain.enums import TipoProduto, UnidadeEstoque
from core.domain.models import Produto, ProdutoComposicao


class ProdutoComposicaoCreateRequest(BaseModel):
    produto_componente_id: int = Field(alias="produtoComponenteId")
    quantidade_baixa: Decimal = Field(alias="quantidadeBaixa")

    model_config = ConfigDict(populate_by_name=True)


class ProdutoComposicaoUpdateRequest(BaseModel):
    quantidade_baixa: Decimal = Field(alias="quantidadeBaixa")

    model_config = ConfigDict(populate_by_name=True)


class ProdutoComposicaoComponenteResponse(BaseModel):
    id: int
    produto_componente_id: int = Field(alias="produtoComponenteId")
    nome_produto_componente: str = Field(alias="nomeProdutoComponente")
    unidade_estoque: UnidadeEstoque = Field(alias="unidadeEstoque")
    quantidade_baixa: str = Field(alias="quantidadeBaixa")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(
        cls,
        composicao: ProdutoComposicao,
    ) -> "ProdutoComposicaoComponenteResponse":
        if composicao.id is None:
            raise ValueError("Composição sem id")

        if composicao.produto_componente is None:
            raise ValueError("Composição sem componente carregado")

        return cls(
            id=composicao.id,
            produtoComponenteId=composicao.produto_componente_id,
            nomeProdutoComponente=composicao.produto_componente.nome,
            unidadeEstoque=composicao.produto_componente.unidade_estoque,
            quantidadeBaixa=f"{composicao.quantidade_baixa:.3f}",
        )


class ProdutoComposicaoResponse(BaseModel):
    produto_id: int = Field(alias="produtoId")
    tipo_produto: TipoProduto = Field(alias="tipoProduto")
    componentes: list[ProdutoComposicaoComponenteResponse]

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_models(
        cls,
        produto: Produto,
        composicoes: list[ProdutoComposicao],
    ) -> "ProdutoComposicaoResponse":
        if produto.id is None:
            raise ValueError("Produto sem id")

        return cls(
            produtoId=produto.id,
            tipoProduto=produto.tipo_produto,
            componentes=[
                ProdutoComposicaoComponenteResponse.from_model(composicao)
                for composicao in composicoes
            ],
        )
