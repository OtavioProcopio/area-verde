from typing import Optional

from sqlmodel import Session, select

from core.domain.models import ProdutoComposicao


class ProdutoComposicaoRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, composicao: ProdutoComposicao) -> ProdutoComposicao:
        self.session.add(composicao)
        self.session.commit()
        self.session.refresh(composicao)
        return composicao

    def add(self, composicao: ProdutoComposicao) -> ProdutoComposicao:
        self.session.add(composicao)
        self.session.flush()
        return composicao

    def refresh(self, composicao: ProdutoComposicao) -> None:
        self.session.refresh(composicao)

    def update(self, composicao: ProdutoComposicao) -> ProdutoComposicao:
        self.session.add(composicao)
        self.session.commit()
        self.session.refresh(composicao)
        return composicao

    def delete(self, composicao: ProdutoComposicao) -> None:
        self.session.delete(composicao)
        self.session.commit()

    def get_by_parent_and_component(
        self,
        produto_pai_id: int,
        produto_componente_id: int,
    ) -> Optional[ProdutoComposicao]:
        statement = select(ProdutoComposicao).where(
            ProdutoComposicao.produto_pai_id == produto_pai_id,
            ProdutoComposicao.produto_componente_id == produto_componente_id,
        )
        return self.session.exec(statement).first()

    def list_by_parent(self, produto_pai_id: int) -> list[ProdutoComposicao]:
        statement = select(ProdutoComposicao).where(
            ProdutoComposicao.produto_pai_id == produto_pai_id
        )
        return list(self.session.exec(statement).all())
