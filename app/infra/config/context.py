from contextvars import ContextVar
from typing import Optional

from sqlmodel import Session

db_session_context: ContextVar[Optional[Session]] = ContextVar(
    "db_session_context", default=None
)
