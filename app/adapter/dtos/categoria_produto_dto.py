from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.models import CategoriaProduto


class CategoriaProdutoRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise ValueError("Nome obrigatório")
        return nome


class CategoriaProdutoResponse(BaseModel):
    id: int
    nome: str
    ativo: bool
    criado_em: datetime = Field(alias="criadoEm")
    atualizado_em: datetime = Field(alias="atualizadoEm")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(cls, categoria: CategoriaProduto) -> "CategoriaProdutoResponse":
        if categoria.id is None:
            raise ValueError("Categoria sem id")

        return cls(
            id=categoria.id,
            nome=categoria.nome,
            ativo=categoria.ativo,
            criadoEm=categoria.criado_em,
            atualizadoEm=categoria.atualizado_em,
        )


class CategoriaProdutoResumoResponse(BaseModel):
    id: int
    nome: str

    @classmethod
    def from_model(
        cls, categoria: CategoriaProduto
    ) -> "CategoriaProdutoResumoResponse":
        if categoria.id is None:
            raise ValueError("Categoria sem id")

        return cls(id=categoria.id, nome=categoria.nome)
