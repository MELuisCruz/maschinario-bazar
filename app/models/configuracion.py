"""Configuración clave-valor de la app, editable por el administrador.

Guarda textos editables (p. ej. los del ticket). Los valores por defecto viven
en `app/services/configuracion.py`; aquí solo el almacenamiento.
"""

from __future__ import annotations

from sqlalchemy import Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Configuracion(Base):
    __tablename__ = "configuracion"

    clave: Mapped[str] = mapped_column(Text, primary_key=True)
    valor: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
