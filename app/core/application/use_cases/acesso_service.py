from datetime import datetime

from core.domain.exceptions import ApplicationError
from core.domain.models import ConfiguracaoSistema
from core.interfaces.adapters.repositories.i_configuracao_sistema_repository import (
    IConfiguracaoSistemaRepository,
)
from infra.security.passwords import hash_password, verify_password


class AcessoService:
    def __init__(
        self,
        configuracao_repository: IConfiguracaoSistemaRepository,
    ):
        self.configuracao_repository = configuracao_repository

    def validar_senha(self, senha: str) -> None:
        configuracao = self._get_configuracao()
        self._ensure_senha_configurada(configuracao)
        if not verify_password(senha, configuracao.senha_acesso_hash):
            raise ApplicationError(
                code="senha_invalida",
                message="Senha inválida",
                status_code=401,
            )

    def definir_ou_alterar_senha(
        self,
        nova_senha: str,
        senha_atual: str | None = None,
    ) -> ConfiguracaoSistema:
        configuracao = self._get_configuracao()
        senha_normalizada = self._normalize_password(nova_senha)

        if configuracao.senha_acesso_hash:
            if senha_atual is None:
                raise ApplicationError(
                    code="senha_atual_obrigatoria",
                    message="Senha atual obrigatória",
                    status_code=400,
                )
            if not verify_password(senha_atual, configuracao.senha_acesso_hash):
                raise ApplicationError(
                    code="senha_atual_invalida",
                    message="Senha atual inválida",
                    status_code=401,
                )

        configuracao.senha_acesso_hash = hash_password(senha_normalizada)

        try:
            self.configuracao_repository.save(configuracao)
            self.configuracao_repository.commit()
            self.configuracao_repository.refresh(configuracao)
        except Exception:
            self.configuracao_repository.rollback()
            raise

        return configuracao

    def _get_configuracao(self) -> ConfiguracaoSistema:
        configuracao = self.configuracao_repository.get_atual()
        if configuracao is not None:
            return configuracao

        now = datetime.now()
        configuracao = ConfiguracaoSistema(
            senha_acesso_hash="",
            dias_para_alerta_fiado=7,
            permitir_estoque_negativo=True,
            nome_bar="Area Verde",
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

    @staticmethod
    def _ensure_senha_configurada(configuracao: ConfiguracaoSistema) -> None:
        if not configuracao.senha_acesso_hash:
            raise ApplicationError(
                code="senha_nao_configurada",
                message="Senha de acesso ainda não configurada",
                status_code=400,
            )

    @staticmethod
    def _normalize_password(password: str) -> str:
        senha = password.strip()
        if len(senha) < 4:
            raise ApplicationError(
                code="nova_senha_invalida",
                message="Nova senha inválida",
                status_code=400,
            )
        return senha
