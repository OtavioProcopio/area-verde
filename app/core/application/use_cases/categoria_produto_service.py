from datetime import datetime
from typing import Optional

from core.domain.exceptions import ConflictError, NotFoundError
from core.domain.models import CategoriaProduto
from core.interfaces.adapters.repositories.i_categoria_produto_repository import (
    ICategoriaProdutoRepository,
)


class CategoriaProdutoService:
    def __init__(self, categoria_repository: ICategoriaProdutoRepository):
        self.categoria_repository = categoria_repository

    def create(self, nome: str) -> CategoriaProduto:
        nome_normalizado = self._normalize_nome(nome)
        self._ensure_active_nome_available(nome_normalizado)

        categoria = CategoriaProduto(nome=nome_normalizado, ativo=True)
        return self.categoria_repository.create(categoria)

    def list(self, ativo: Optional[bool] = None) -> list[CategoriaProduto]:
        return self.categoria_repository.list(ativo=ativo)

    def get_by_id(self, categoria_id: int) -> CategoriaProduto:
        categoria = self.categoria_repository.get_by_id(categoria_id)
        if categoria is None:
            raise NotFoundError(
                code="categoria_nao_encontrada",
                message="Categoria não encontrada",
            )
        return categoria

    def update(self, categoria_id: int, nome: str) -> CategoriaProduto:
        categoria = self.get_by_id(categoria_id)
        nome_normalizado = self._normalize_nome(nome)

        if categoria.ativo:
            self._ensure_active_nome_available(
                nome_normalizado, exclude_id=categoria_id
            )

        categoria.nome = nome_normalizado
        categoria.atualizado_em = datetime.now()
        return self.categoria_repository.update(categoria)

    def activate(self, categoria_id: int) -> CategoriaProduto:
        categoria = self.get_by_id(categoria_id)
        self._ensure_active_nome_available(categoria.nome, exclude_id=categoria_id)

        categoria.ativo = True
        categoria.atualizado_em = datetime.now()
        return self.categoria_repository.update(categoria)

    def deactivate(self, categoria_id: int) -> CategoriaProduto:
        categoria = self.get_by_id(categoria_id)
        categoria.ativo = False
        categoria.atualizado_em = datetime.now()
        return self.categoria_repository.update(categoria)

    def _ensure_active_nome_available(
        self, nome: str, exclude_id: Optional[int] = None
    ) -> None:
        categoria = self.categoria_repository.get_active_by_nome(
            nome, exclude_id=exclude_id
        )
        if categoria is not None:
            raise ConflictError(
                code="nome_duplicado",
                message="Já existe uma categoria ativa com esse nome",
            )

    @staticmethod
    def _normalize_nome(nome: str) -> str:
        return nome.strip()
