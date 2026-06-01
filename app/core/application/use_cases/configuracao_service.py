from datetime import datetime
from typing import Optional

from core.domain.exceptions import ApplicationError
from core.domain.models import ConfiguracaoSistema
from core.interfaces.adapters.repositories.i_configuracao_sistema_repository import (
    IConfiguracaoSistemaRepository,
)

DEFAULT_DIAS_PARA_ALERTA_FIADO = 7
DEFAULT_NOME_BAR = "Area Verde"
DEFAULT_PERMITIR_ESTOQUE_NEGATIVO = True


class ConfiguracaoService:
    def __init__(
        self,
        configuracao_repository: IConfiguracaoSistemaRepository,
    ):
        self.configuracao_repository = configuracao_repository

    def get_or_create(self) -> ConfiguracaoSistema:
        configuracao = self.configuracao_repository.get_atual()
        if configuracao is not None:
            return configuracao

        now = datetime.now()
        configuracao = ConfiguracaoSistema(
            senha_acesso_hash="",
            dias_para_alerta_fiado=DEFAULT_DIAS_PARA_ALERTA_FIADO,
            permitir_estoque_negativo=DEFAULT_PERMITIR_ESTOQUE_NEGATIVO,
            nome_bar=DEFAULT_NOME_BAR,
            observacao=None,
            criado_em=now,
            atualizado_em=now,
        )

        try:
            self.configuracao_repository.create(configuracao)
            self.configuracao_repository.commit()
            self.configuracao_repository.refresh(configuracao)
        except Exception:
            self.configuracao_repository.rollback()
            raise

        return configuracao

    def update(
        self,
        nome_bar: str,
        dias_para_alerta_fiado: int,
        permitir_estoque_negativo: bool,
        observacao: Optional[str] = None,
    ) -> ConfiguracaoSistema:
        configuracao = self.get_or_create()
        self._apply_updates(
            configuracao=configuracao,
            nome_bar=nome_bar,
            dias_para_alerta_fiado=dias_para_alerta_fiado,
            permitir_estoque_negativo=permitir_estoque_negativo,
            observacao=observacao,
        )
        return self._persist(configuracao)

    def patch(
        self,
        nome_bar: Optional[str] = None,
        dias_para_alerta_fiado: Optional[int] = None,
        permitir_estoque_negativo: Optional[bool] = None,
        observacao: Optional[str] = None,
    ) -> ConfiguracaoSistema:
        configuracao = self.get_or_create()

        if nome_bar is not None:
            configuracao.nome_bar = self._normalize_nome_bar(nome_bar)
        if dias_para_alerta_fiado is not None:
            configuracao.dias_para_alerta_fiado = self._validate_dias_para_alerta(
                dias_para_alerta_fiado
            )
        if permitir_estoque_negativo is not None:
            configuracao.permitir_estoque_negativo = permitir_estoque_negativo
        if observacao is not None:
            configuracao.observacao = observacao

        configuracao.atualizado_em = datetime.now()
        return self._persist(configuracao)

    def _apply_updates(
        self,
        configuracao: ConfiguracaoSistema,
        nome_bar: str,
        dias_para_alerta_fiado: int,
        permitir_estoque_negativo: bool,
        observacao: Optional[str],
    ) -> None:
        configuracao.nome_bar = self._normalize_nome_bar(nome_bar)
        configuracao.dias_para_alerta_fiado = self._validate_dias_para_alerta(
            dias_para_alerta_fiado
        )
        configuracao.permitir_estoque_negativo = permitir_estoque_negativo
        configuracao.observacao = observacao
        configuracao.atualizado_em = datetime.now()

    def _persist(self, configuracao: ConfiguracaoSistema) -> ConfiguracaoSistema:
        try:
            self.configuracao_repository.save(configuracao)
            self.configuracao_repository.commit()
            self.configuracao_repository.refresh(configuracao)
        except Exception:
            self.configuracao_repository.rollback()
            raise

        return configuracao

    @staticmethod
    def _normalize_nome_bar(nome_bar: str) -> str:
        nome_normalizado = nome_bar.strip()
        if not nome_normalizado:
            raise ApplicationError(
                code="nome_bar_invalido",
                message="Nome do bar inválido",
                status_code=400,
            )
        return nome_normalizado

    @staticmethod
    def _validate_dias_para_alerta(dias_para_alerta_fiado: int) -> int:
        if dias_para_alerta_fiado <= 0:
            raise ApplicationError(
                code="dias_para_alerta_fiado_invalido",
                message="Dias para alerta de fiado inválido",
                status_code=400,
            )
        return dias_para_alerta_fiado
