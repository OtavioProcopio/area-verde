from datetime import datetime
from decimal import Decimal

from core.domain.enums import TipoProduto
from core.domain.exceptions import ApplicationError, ConflictError, NotFoundError
from core.domain.models import Produto, ProdutoComposicao
from core.interfaces.adapters.repositories.i_produto_composicao_repository import (
    IProdutoComposicaoRepository,
)
from core.interfaces.adapters.repositories.i_produto_repository import (
    IProdutoRepository,
)


class ProdutoComposicaoService:
    def __init__(
        self,
        produto_repository: IProdutoRepository,
        composicao_repository: IProdutoComposicaoRepository,
    ):
        self.produto_repository = produto_repository
        self.composicao_repository = composicao_repository

    def add_componente(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
        quantidade_baixa: Decimal,
    ) -> ProdutoComposicao:
        self._ensure_quantidade_positiva(quantidade_baixa)
        produto_pai = self._get_produto(produto_pai_id, "produto_pai_nao_encontrado")
        componente = self._get_produto(
            produto_componente_id,
            "produto_componente_nao_encontrado",
        )

        self._ensure_produto_pai_composto(produto_pai)
        self._ensure_componente_valido(
            produto_pai=produto_pai,
            componente=componente,
        )
        self._ensure_componente_nao_duplicado(
            produto_pai_id=produto_pai_id,
            produto_componente_id=produto_componente_id,
        )

        composicao = ProdutoComposicao(
            produto_pai_id=produto_pai_id,
            produto_componente_id=produto_componente_id,
            quantidade_baixa=quantidade_baixa,
        )
        return self.composicao_repository.create(composicao)

    def list_by_parent(self, produto_pai_id: int) -> list[ProdutoComposicao]:
        produto_pai = self._get_produto(produto_pai_id, "produto_pai_nao_encontrado")
        self._ensure_produto_pai_composto(produto_pai)
        return self.composicao_repository.list_by_parent(produto_pai_id)

    def update_componente(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
        quantidade_baixa: Decimal,
    ) -> ProdutoComposicao:
        self._ensure_quantidade_positiva(quantidade_baixa)
        produto_pai = self._get_produto(produto_pai_id, "produto_pai_nao_encontrado")
        self._ensure_produto_pai_composto(produto_pai)
        composicao = self._get_composicao(
            produto_pai_id=produto_pai_id,
            produto_componente_id=produto_componente_id,
        )
        componente = self._get_produto(
            produto_componente_id,
            "produto_componente_nao_encontrado",
        )
        self._ensure_componente_valido(
            produto_pai=produto_pai,
            componente=componente,
        )

        composicao.quantidade_baixa = quantidade_baixa
        composicao.atualizado_em = datetime.now()
        return self.composicao_repository.update(composicao)

    def delete_componente(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
    ) -> None:
        produto_pai = self._get_produto(produto_pai_id, "produto_pai_nao_encontrado")
        self._ensure_produto_pai_composto(produto_pai)
        composicao = self._get_composicao(
            produto_pai_id=produto_pai_id,
            produto_componente_id=produto_componente_id,
        )
        self.composicao_repository.delete(composicao)

    def componentes_validos_para_venda(
        self,
        produto_pai: Produto,
    ) -> list[ProdutoComposicao]:
        self._ensure_produto_pai_composto(produto_pai)
        produto_pai_id = self._get_produto_id(produto_pai)
        composicoes = self.composicao_repository.list_by_parent(produto_pai_id)
        if not composicoes:
            raise ApplicationError(
                code="produto_composto_sem_composicao",
                message="Produto composto sem composição",
                status_code=400,
            )

        for composicao in composicoes:
            componente = composicao.produto_componente
            if componente is None:
                componente = self._get_produto(
                    composicao.produto_componente_id,
                    "produto_componente_nao_encontrado",
                )
            self._ensure_componente_valido(
                produto_pai=produto_pai,
                componente=componente,
            )
            self._ensure_quantidade_positiva(composicao.quantidade_baixa)

        return composicoes

    def _get_produto(self, produto_id: int, code: str) -> Produto:
        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None:
            raise NotFoundError(
                code=code,
                message="Produto não encontrado",
            )
        return produto

    def _get_composicao(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
    ) -> ProdutoComposicao:
        composicao = self.composicao_repository.get_by_parent_and_component(
            produto_pai_id=produto_pai_id,
            produto_componente_id=produto_componente_id,
        )
        if composicao is None:
            raise NotFoundError(
                code="produto_componente_nao_encontrado",
                message="Componente não encontrado na composição",
            )
        return composicao

    @staticmethod
    def _ensure_produto_pai_composto(produto_pai: Produto) -> None:
        if not produto_pai.ativo:
            raise ApplicationError(
                code="produto_pai_inativo",
                message="Produto pai inativo",
                status_code=400,
            )

        if produto_pai.tipo_produto != TipoProduto.COMPOSTO:
            raise ApplicationError(
                code="produto_pai_deve_ser_composto",
                message="Produto pai deve ser composto",
                status_code=400,
            )

    @staticmethod
    def _get_produto_id(produto: Produto) -> int:
        if produto.id is None:
            raise ApplicationError(
                code="dados_invalidos",
                message="Produto inválido",
                status_code=400,
            )
        return produto.id

    @staticmethod
    def _ensure_componente_valido(produto_pai: Produto, componente: Produto) -> None:
        if produto_pai.id == componente.id:
            raise ApplicationError(
                code="componente_igual_produto_pai",
                message="Produto composto não pode ser componente de si mesmo",
                status_code=400,
            )

        if componente.tipo_produto == TipoProduto.COMPOSTO:
            raise ApplicationError(
                code="componente_composto_nao_permitido",
                message="Produto composto não pode ser componente no MVP",
                status_code=400,
            )

        if not componente.ativo:
            raise ApplicationError(
                code="produto_componente_inativo",
                message="Produto componente inativo",
                status_code=400,
            )

        if not componente.controla_estoque:
            raise ApplicationError(
                code="produto_componente_sem_controle_estoque",
                message="Produto componente deve controlar estoque",
                status_code=400,
            )

    def _ensure_componente_nao_duplicado(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
    ) -> None:
        composicao = self.composicao_repository.get_by_parent_and_component(
            produto_pai_id=produto_pai_id,
            produto_componente_id=produto_componente_id,
        )
        if composicao is not None:
            raise ConflictError(
                code="produto_componente_duplicado",
                message="Componente já cadastrado para o produto",
            )

    @staticmethod
    def _ensure_quantidade_positiva(quantidade_baixa: Decimal) -> None:
        if quantidade_baixa <= Decimal("0"):
            raise ApplicationError(
                code="quantidade_baixa_invalida",
                message="Quantidade de baixa inválida",
                status_code=400,
            )
