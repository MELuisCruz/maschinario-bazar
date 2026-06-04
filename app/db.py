"""Engine y sesión de SQLAlchemy + Base declarativa (ARCHITECTURE.md §4).

El esquema concreto se implementa en `app/models/` y se versiona vía Alembic
(CLAUDE.md §7: nada de `create_all` en producción).
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa común para todos los modelos ORM."""


engine = create_engine(get_settings().database_url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """Dependencia FastAPI: una sesión por request, cerrada al terminar."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
