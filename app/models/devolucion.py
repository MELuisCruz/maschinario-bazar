"""Devoluciones contra una venta y su detalle (DATA_MODEL.md §2)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Devolucion(Base):
    __tablename__ = "devoluciones"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    venta_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ventas.id"), nullable=False
    )
    turno_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("turnos.id"), nullable=False
    )
    cajero_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cajeros.id"), nullable=False
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    lineas: Mapped[list["DevolucionLinea"]] = relationship(
        back_populates="devolucion", cascade="all, delete-orphan", passive_deletes=True
    )


class DevolucionLinea(Base):
    __tablename__ = "devolucion_lineas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_devolucion_lineas_cantidad_positiva"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    devolucion_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("devoluciones.id", ondelete="CASCADE"),
        nullable=False,
    )
    venta_linea_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("venta_lineas.id"), nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    devolucion: Mapped["Devolucion"] = relationship(back_populates="lineas")
