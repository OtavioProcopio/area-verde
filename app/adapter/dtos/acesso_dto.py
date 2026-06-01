from pydantic import BaseModel, ConfigDict, Field, field_validator


class ValidarAcessoRequest(BaseModel):
    senha: str = Field(min_length=1, max_length=120)

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, value: str) -> str:
        senha = value.strip()
        if not senha:
            raise ValueError("Senha obrigatória")
        return senha


class ValidarAcessoResponse(BaseModel):
    valido: bool


class AlterarSenhaRequest(BaseModel):
    senha_atual: str | None = Field(default=None, alias="senhaAtual", max_length=120)
    nova_senha: str = Field(alias="novaSenha", min_length=4, max_length=120)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("senha_atual")
    @classmethod
    def validate_senha_atual(cls, value: str | None) -> str | None:
        if value is None:
            return value
        senha = value.strip()
        return senha or None

    @field_validator("nova_senha")
    @classmethod
    def validate_nova_senha(cls, value: str) -> str:
        senha = value.strip()
        if len(senha) < 4:
            raise ValueError("Nova senha inválida")
        return senha


class AlterarSenhaResponse(BaseModel):
    senha_configurada: bool = Field(alias="senhaConfigurada")

    model_config = ConfigDict(populate_by_name=True)
