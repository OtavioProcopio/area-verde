from typing import Optional, Protocol

from core.domain.models import ProdutoComposicao


class IProdutoComposicaoRepository(Protocol):
    def create(self, composicao: ProdutoComposicao) -> ProdutoComposicao: ...

    def get_by_parent_and_component(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
    ) -> Optional[ProdutoComposicao]: ...

    def list_by_parent(self, produto_pai_id: int) -> list[ProdutoComposicao]: ...
