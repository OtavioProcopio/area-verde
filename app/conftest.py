import os
import sys

import pytest
from dependency_injector import providers
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.domain import models  # noqa: E402, F401
from infra.config.container import Container  # noqa: E402


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_session(test_engine):
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def test_container(test_engine):
    container = Container()
    container.engine.override(providers.Object(test_engine))
    return container
