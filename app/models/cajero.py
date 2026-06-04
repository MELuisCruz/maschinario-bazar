"""Cajeros: operadores que se autentican y abren turno (DATA_MODEL.md §2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import RolCajero, rol_cajero_enum


class Cajero(Base):
    __tablename__ = "cajeros"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    usuario: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    pin_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rol: Mapped[RolCajero] = mapped_column(
        rol_cajero_enum, nullable=False, server_default=text("'cajero'")
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
