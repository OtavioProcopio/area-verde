from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.domain.enums import TipoProduto, UnidadeEstoque
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import CategoriaProduto, Produto
from core.interfaces.adapters.repositories.i_categoria_produto_repository import (
    ICategoriaProdutoRepository,
)
from core.interfaces.adapters.repositories.i_produto_repository import (
    IProdutoRepository,
)


@dataclass(frozen=True)
class StockData:
    unidade_estoque: UnidadeEstoque
    quantidade_estoque: Decimal
    quantidade_baixa_por_venda: Decimal
    estoque_minimo: Decimal


class ProdutoService:
    def __init__(
        self,
        produto_repository: IProdutoRepository,
        categoria_repository: ICategoriaProdutoRepository,
    ):
        self.produto_repository = produto_repository
        self.categoria_repository = categoria_repository

    def create(
        self,
        nome: str,
        categoria_id: int,
        preco_venda: Decimal,
        controla_estoque: bool,
        tipo_produto: TipoProduto = TipoProduto.SIMPLES,
        unidade_estoque: Optional[UnidadeEstoque] = None,
        quantidade_estoque: Optional[Decimal] = None,
        quantidade_baixa_por_venda: Optional[Decimal] = None,
        estoque_minimo: Optional[Decimal] = None,
    ) -> Produto:
        categoria = self._get_active_categoria(categoria_id)
        estoque = self._build_stock_data(
            controla_estoque=controla_estoque,
            unidade_estoque=unidade_estoque,
            quantidade_estoque=quantidade_estoque,
            quantidade_baixa_por_venda=quantidade_baixa_por_venda,
            estoque_minimo=estoque_minimo,
        )
        self._ensure_preco_valido(preco_venda)

        produto = Produto(
            nome=nome.strip(),
            categoria_id=self._get_categoria_id(categoria),
            preco_venda=preco_venda,
            tipo_produto=tipo_produto,
            controla_estoque=controla_estoque,
            unidade_estoque=estoque.unidade_estoque,
            quantidade_estoque=estoque.quantidade_estoque,
            quantidade_baixa_por_venda=estoque.quantidade_baixa_por_venda,
            estoque_minimo=estoque.estoque_minimo,
            ativo=True,
        )

        return self.produto_repository.create(produto)

    def list(
        self,
        ativo: Optional[bool] = None,
        categoria_id: Optional[int] = None,
        nome: Optional[str] = None,
    ) -> list[Produto]:
        return self.produto_repository.list(
            ativo=ativo,
            categoria_id=categoria_id,
            nome=nome,
        )

    def get_by_id(self, produto_id: int) -> Produto:
        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None:
            raise NotFoundError(
                code="produto_nao_encontrado",
                message="Produto não encontrado",
            )
        return produto

    def update(
        self,
        produto_id: int,
        nome: str,
        categoria_id: int,
        preco_venda: Decimal,
        controla_estoque: bool,
        tipo_produto: TipoProduto = TipoProduto.SIMPLES,
        unidade_estoque: Optional[UnidadeEstoque] = None,
        quantidade_estoque: Optional[Decimal] = None,
        quantidade_baixa_por_venda: Optional[Decimal] = None,
        estoque_minimo: Optional[Decimal] = None,
    ) -> Produto:
        produto = self.get_by_id(produto_id)
        categoria = self._get_active_categoria(categoria_id)
        estoque = self._build_stock_data(
            controla_estoque=controla_estoque,
            unidade_estoque=unidade_estoque,
            quantidade_estoque=quantidade_estoque,
            quantidade_baixa_por_venda=quantidade_baixa_por_venda,
            estoque_minimo=estoque_minimo,
        )
        self._ensure_preco_valido(preco_venda)

        produto.nome = nome.strip()
        produto.categoria_id = self._get_categoria_id(categoria)
        produto.preco_venda = preco_venda
        produto.tipo_produto = tipo_produto
        produto.controla_estoque = controla_estoque
        produto.unidade_estoque = estoque.unidade_estoque
        produto.quantidade_estoque = estoque.quantidade_estoque
        produto.quantidade_baixa_por_venda = estoque.quantidade_baixa_por_venda
        produto.estoque_minimo = estoque.estoque_minimo
        produto.atualizado_em = datetime.now()

        return self.produto_repository.update(produto)

    def activate(self, produto_id: int) -> Produto:
        produto = self.get_by_id(produto_id)
        self._get_active_categoria(produto.categoria_id)

        produto.ativo = True
        produto.atualizado_em = datetime.now()
        return self.produto_repository.update(produto)

    def deactivate(self, produto_id: int) -> Produto:
        produto = self.get_by_id(produto_id)
        produto.ativo = False
        produto.atualizado_em = datetime.now()
        return self.produto_repository.update(produto)

    def _get_active_categoria(self, categoria_id: int) -> CategoriaProduto:
        categoria = self.categoria_repository.get_by_id(categoria_id)
        if categoria is None:
            raise NotFoundError(
                code="categoria_nao_encontrada",
                message="Categoria não encontrada",
            )

        if not categoria.ativo:
            raise ApplicationError(
                code="categoria_inativa",
                message="Categoria inativa",
                status_code=400,
            )

        return categoria

    @staticmethod
    def _get_categoria_id(categoria: CategoriaProduto) -> int:
        if categoria.id is None:
            raise ApplicationError(
                code="dados_invalidos",
                message="Categoria inválida",
                status_code=400,
            )
        return categoria.id

    @staticmethod
    def _ensure_preco_valido(preco_venda: Decimal) -> None:
        if preco_venda < Decimal("0"):
            raise ApplicationError(
                code="preco_invalido",
                message="Preço inválido",
                status_code=400,
            )

    def _build_stock_data(
        self,
        controla_estoque: bool,
        unidade_estoque: Optional[UnidadeEstoque],
        quantidade_estoque: Optional[Decimal],
        quantidade_baixa_por_venda: Optional[Decimal],
        estoque_minimo: Optional[Decimal],
    ) -> StockData:
        if not controla_estoque:
            return StockData(
                unidade_estoque=UnidadeEstoque.UNIDADE,
                quantidade_estoque=Decimal("0"),
                quantidade_baixa_por_venda=Decimal("0"),
                estoque_minimo=Decimal("0"),
            )

        if unidade_estoque is None:
            raise ApplicationError(
                code="unidade_estoque_invalida",
                message="Unidade de estoque inválida",
                status_code=400,
            )

        quantidade = quantidade_estoque or Decimal("0")
        estoque_minimo_normalizado = estoque_minimo or Decimal("0")

        if quantidade < Decimal("0"):
            raise ApplicationError(
                code="dados_invalidos",
                message="Quantidade de estoque inválida",
                status_code=400,
            )

        if estoque_minimo_normalizado < Decimal("0"):
            raise ApplicationError(
                code="dados_invalidos",
                message="Estoque mínimo inválido",
                status_code=400,
            )

        if quantidade_baixa_por_venda is None or quantidade_baixa_por_venda <= Decimal(
            "0"
        ):
            raise ApplicationError(
                code="quantidade_baixa_invalida",
                message="Quantidade de baixa inválida",
                status_code=400,
            )

        return StockData(
            unidade_estoque=unidade_estoque,
            quantidade_estoque=quantidade,
            quantidade_baixa_por_venda=quantidade_baixa_por_venda,
            estoque_minimo=estoque_minimo_normalizado,
        )
