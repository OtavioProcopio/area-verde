from typing import Optional

from sqlalchemy import text
from sqlmodel import Session, select

from core.domain.models import ConfiguracaoSistema


class ConfiguracaoSistemaRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_atual(self) -> Optional[ConfiguracaoSistema]:
        statement = select(ConfiguracaoSistema).order_by(text("id")).limit(1)
        return self.session.exec(statement).first()

    def create(self, configuracao: ConfiguracaoSistema) -> ConfiguracaoSistema:
        self.session.add(configuracao)
        self.session.flush()
        return configuracao

    def save(self, configuracao: ConfiguracaoSistema) -> ConfiguracaoSistema:
        self.session.add(configuracao)
        return configuracao

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, configuracao: ConfiguracaoSistema) -> None:
        self.session.refresh(configuracao)
