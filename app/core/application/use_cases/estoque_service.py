from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from core.domain.enums import OrigemMovimentoEstoque, TipoMovimentoEstoque
from core.domain.exceptions import ApplicationError, NotFoundError
from core.domain.models import MovimentoEstoque, Produto
from core.interfaces.adapters.repositories.i_movimento_estoque_repository import (
    IMovimentoEstoqueRepository,
)
from core.interfaces.adapters.repositories.i_produto_repository import (
    IProdutoRepository,
)


class EstoqueService:
    def __init__(
        self,
        produto_repository: IProdutoRepository,
        movimento_repository: IMovimentoEstoqueRepository,
    ):
        self.produto_repository = produto_repository
        self.movimento_repository = movimento_repository

    def list(
        self,
        ativo: Optional[bool] = None,
        categoria_id: Optional[int] = None,
        nome: Optional[str] = None,
    ) -> List[Produto]:
        return [
            produto
            for produto in self.produto_repository.list(
                ativo=ativo,
                categoria_id=categoria_id,
                nome=nome,
            )
            if produto.controla_estoque
        ]

    def list_baixo(self) -> List[Produto]:
        return [
            produto
            for produto in self.list(ativo=True)
            if produto.quantidade_estoque <= produto.estoque_minimo
        ]

    def list_negativo(self) -> List[Produto]:
        return [
            produto
            for produto in self.list(ativo=True)
            if produto.quantidade_estoque < Decimal("0")
        ]

    def list_movimentos(self, produto_id: int) -> List[MovimentoEstoque]:
        self._get_produto(produto_id)
        return self.movimento_repository.list_by_produto(produto_id)

    def adicionar_entrada(
        self,
        produto_id: int,
        quantidade: Decimal,
        observacao: Optional[str] = None,
    ) -> MovimentoEstoque:
        if quantidade <= Decimal("0"):
            raise ApplicationError(
                code="quantidade_invalida",
                message="Quantidade inválida",
                status_code=400,
            )

        produto = self._get_produto_operavel(produto_id)
        estoque_antes = produto.quantidade_estoque
        estoque_depois = estoque_antes + quantidade

        return self._registrar_movimento(
            produto=produto,
            tipo=TipoMovimentoEstoque.ENTRADA,
            origem=OrigemMovimentoEstoque.ENTRADA_MANUAL,
            quantidade=quantidade,
            estoque_antes=estoque_antes,
            estoque_depois=estoque_depois,
            observacao=observacao,
        )

    def ajustar(
        self,
        produto_id: int,
        novo_estoque: Decimal,
        observacao: Optional[str] = None,
    ) -> MovimentoEstoque:
        if novo_estoque < Decimal("0"):
            raise ApplicationError(
                code="novo_estoque_invalido",
                message="Novo estoque inválido",
                status_code=400,
            )

        produto = self._get_produto_operavel(produto_id)
        estoque_antes = produto.quantidade_estoque
        diferenca = novo_estoque - estoque_antes

        return self._registrar_movimento(
            produto=produto,
            tipo=TipoMovimentoEstoque.AJUSTE,
            origem=OrigemMovimentoEstoque.AJUSTE_MANUAL,
            quantidade=diferenca,
            estoque_antes=estoque_antes,
            estoque_depois=novo_estoque,
            observacao=observacao,
        )

    def baixar_por_venda(
        self,
        produto: Produto,
        quantidade_baixada: Decimal,
        referencia_id: Optional[int] = None,
        observacao: Optional[str] = None,
        commit: bool = False,
    ) -> Optional[MovimentoEstoque]:
        if quantidade_baixada <= Decimal("0"):
            raise ApplicationError(
                code="quantidade_invalida",
                message="Quantidade inválida",
                status_code=400,
            )

        if not produto.controla_estoque:
            return None

        estoque_antes = produto.quantidade_estoque
        estoque_depois = estoque_antes - quantidade_baixada

        return self._registrar_movimento(
            produto=produto,
            tipo=TipoMovimentoEstoque.SAIDA_VENDA,
            origem=OrigemMovimentoEstoque.COMANDA,
            quantidade=quantidade_baixada,
            estoque_antes=estoque_antes,
            estoque_depois=estoque_depois,
            observacao=observacao,
            referencia_id=referencia_id,
            commit=commit,
        )

    def devolver_por_cancelamento(
        self,
        produto: Produto,
        quantidade_devolvida: Decimal,
        referencia_id: Optional[int] = None,
        origem: OrigemMovimentoEstoque = OrigemMovimentoEstoque.COMANDA,
        observacao: Optional[str] = None,
        commit: bool = False,
    ) -> Optional[MovimentoEstoque]:
        if quantidade_devolvida <= Decimal("0"):
            raise ApplicationError(
                code="quantidade_invalida",
                message="Quantidade inválida",
                status_code=400,
            )

        if not produto.controla_estoque:
            return None

        estoque_antes = produto.quantidade_estoque
        estoque_depois = estoque_antes + quantidade_devolvida

        return self._registrar_movimento(
            produto=produto,
            tipo=TipoMovimentoEstoque.DEVOLUCAO_CANCELAMENTO,
            origem=origem,
            quantidade=quantidade_devolvida,
            estoque_antes=estoque_antes,
            estoque_depois=estoque_depois,
            observacao=observacao,
            referencia_id=referencia_id,
            commit=commit,
        )

    def _registrar_movimento(
        self,
        produto: Produto,
        tipo: TipoMovimentoEstoque,
        origem: OrigemMovimentoEstoque,
        quantidade: Decimal,
        estoque_antes: Decimal,
        estoque_depois: Decimal,
        observacao: Optional[str],
        referencia_id: Optional[int] = None,
        commit: bool = True,
    ) -> MovimentoEstoque:
        produto_id = self._get_produto_id(produto)
        produto.quantidade_estoque = estoque_depois
        produto.atualizado_em = datetime.now()

        movimento = MovimentoEstoque(
            produto_id=produto_id,
            tipo=tipo,
            origem=origem,
            quantidade=quantidade,
            estoque_antes=estoque_antes,
            estoque_depois=estoque_depois,
            referencia_id=referencia_id,
            observacao=observacao,
            produto=produto,
        )

        try:
            self.produto_repository.save(produto)
            self.movimento_repository.create(movimento)
            if commit:
                self.movimento_repository.commit()
                self.movimento_repository.refresh(movimento)
        except Exception:
            self.movimento_repository.rollback()
            raise

        return movimento

    def _get_produto(self, produto_id: int) -> Produto:
        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None:
            raise NotFoundError(
                code="produto_nao_encontrado",
                message="Produto não encontrado",
            )
        return produto

    def _get_produto_operavel(self, produto_id: int) -> Produto:
        produto = self._get_produto(produto_id)

        if not produto.ativo:
            raise ApplicationError(
                code="produto_inativo",
                message="Produto inativo",
                status_code=400,
            )

        if not produto.controla_estoque:
            raise ApplicationError(
                code="produto_sem_controle_estoque",
                message="Produto não controla estoque",
                status_code=400,
            )

        return produto

    @staticmethod
    def _get_produto_id(produto: Produto) -> int:
        if produto.id is None:
            raise ApplicationError(
                code="dados_invalidos",
                message="Produto inválido",
                status_code=400,
            )
        return produto.id
