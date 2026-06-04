"""Turnos: apertura/cierre de caja por cajero, fondo y arqueo (DATA_MODEL.md §2)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Turno(Base):
    __tablename__ = "turnos"
    __table_args__ = (Index("idx_turnos_cajero", "cajero_id"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    cajero_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cajeros.id"), nullable=False
    )
    abierto_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    cerrado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fondo_inicial: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    efectivo_contado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # arqueo
    notas: Mapped[str | None] = mapped_column(Text)
