from dependency_injector import containers, providers
from sqlmodel import Session, create_engine

from infra.config.context import db_session_context
from infra.config.settings import settings
from infra.tools.logger import Logger


def get_db_session(engine):
    session = db_session_context.get()
    if session is None:
        return Session(bind=engine)
    return session


class Container(containers.DeclarativeContainer):
    settings = providers.Object(settings)

    engine = providers.Singleton(create_engine, url=settings.provided.database_url)
    db_session = providers.Callable(get_db_session, engine=engine)

    logger = providers.Singleton(Logger)
