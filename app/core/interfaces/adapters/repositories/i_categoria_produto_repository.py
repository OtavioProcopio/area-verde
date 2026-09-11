from typing import Optional, Protocol

from core.domain.models import CategoriaProduto


class ICategoriaProdutoRepository(Protocol):
    def create(self, categoria: CategoriaProduto) -> CategoriaProduto: ...

    def update(self, categoria: CategoriaProduto) -> CategoriaProduto: ...

    def get_by_id(self, categoria_id: int) -> Optional[CategoriaProduto]: ...

    def get_active_by_nome(
        self, nome: str, exclude_id: Optional[int] = None
    ) -> Optional[CategoriaProduto]: ...

    def list(self, ativo: Optional[bool] = None) -> list[CategoriaProduto]: ...
