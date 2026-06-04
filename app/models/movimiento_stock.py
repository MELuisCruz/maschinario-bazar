"""Bitácora de existencias: la fuente de verdad del stock (DATA_MODEL.md §2, §3).

`cantidad` negativa = salida, positiva = entrada. `productos.existencia` se
mantiene consistente con la suma de movimientos.
"""

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
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import TipoMovimiento, tipo_movimiento_enum


class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"
    __table_args__ = (Index("idx_movstock_producto", "producto_id"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    producto_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("productos.id"), nullable=False
    )
    tipo: Mapped[TipoMovimiento] = mapped_column(tipo_movimiento_enum, nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    referencia: Mapped[str | None] = mapped_column(
        Text
    )  # folio venta/devolución/import
    cajero_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("cajeros.id"))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
