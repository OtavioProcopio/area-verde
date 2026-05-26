from typing import Optional, Protocol

from core.domain.models import Produto


class IProdutoRepository(Protocol):
    def create(self, produto: Produto) -> Produto: ...

    def update(self, produto: Produto) -> Produto: ...

    def get_by_id(self, produto_id: int) -> Optional[Produto]: ...

    def list(
        self,
        ativo: Optional[bool] = None,
        categoria_id: Optional[int] = None,
        nome: Optional[str] = None,
    ) -> list[Produto]: ...
