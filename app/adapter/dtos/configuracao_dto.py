from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.domain.models import ConfiguracaoSistema


class ConfiguracaoRequest(BaseModel):
    nome_bar: str = Field(alias="nomeBar", min_length=1, max_length=120)
    dias_para_alerta_fiado: int = Field(alias="diasParaAlertaFiado")
    permitir_estoque_negativo: bool = Field(alias="permitirEstoqueNegativo")
    observacao: Optional[str] = Field(default=None, alias="observacao", max_length=500)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nome_bar")
    @classmethod
    def validate_nome_bar(cls, value: str) -> str:
        nome_bar = value.strip()
        if not nome_bar:
            raise ValueError("Nome do bar obrigatório")
        return nome_bar


class ConfiguracaoPatchRequest(BaseModel):
    nome_bar: Optional[str] = Field(default=None, alias="nomeBar", max_length=120)
    dias_para_alerta_fiado: Optional[int] = Field(
        default=None, alias="diasParaAlertaFiado"
    )
    permitir_estoque_negativo: Optional[bool] = Field(
        default=None, alias="permitirEstoqueNegativo"
    )
    observacao: Optional[str] = Field(default=None, alias="observacao", max_length=500)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nome_bar")
    @classmethod
    def validate_nome_bar(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        nome_bar = value.strip()
        if not nome_bar:
            raise ValueError("Nome do bar obrigatório")
        return nome_bar


class ConfiguracaoResponse(BaseModel):
    id: int
    nome_bar: str = Field(alias="nomeBar")
    dias_para_alerta_fiado: int = Field(alias="diasParaAlertaFiado")
    permitir_estoque_negativo: bool = Field(alias="permitirEstoqueNegativo")
    observacao: Optional[str]
    senha_configurada: bool = Field(alias="senhaConfigurada")
    criado_em: datetime = Field(alias="criadoEm")
    atualizado_em: datetime = Field(alias="atualizadoEm")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_model(
        cls,
        configuracao: ConfiguracaoSistema,
    ) -> "ConfiguracaoResponse":
        if configuracao.id is None:
            raise ValueError("Configuração sem id")

        return cls(
            id=configuracao.id,
            nomeBar=configuracao.nome_bar,
            diasParaAlertaFiado=configuracao.dias_para_alerta_fiado,
            permitirEstoqueNegativo=configuracao.permitir_estoque_negativo,
            observacao=configuracao.observacao,
            senhaConfigurada=bool(configuracao.senha_acesso_hash),
            criadoEm=configuracao.criado_em,
            atualizadoEm=configuracao.atualizado_em,
        )
