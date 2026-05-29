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
        self._get_produto(produto_pai_id, "produto_pai_nao_encontrado")
        return self.composicao_repository.list_by_parent(produto_pai_id)

    def _get_produto(self, produto_id: int, code: str) -> Produto:
        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None:
            raise NotFoundError(
                code=code,
                message="Produto não encontrado",
            )
        return produto

    @staticmethod
    def _ensure_produto_pai_composto(produto_pai: Produto) -> None:
        if produto_pai.tipo_produto != TipoProduto.COMPOSTO:
            raise ApplicationError(
                code="produto_pai_deve_ser_composto",
                message="Produto pai deve ser composto",
                status_code=400,
            )

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
