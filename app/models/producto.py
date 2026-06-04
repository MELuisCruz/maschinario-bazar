"""Productos: catálogo con código de barras, precio, IVA y existencia."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Identity,
    Index,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="ck_productos_precio_no_negativo"),
        Index("idx_productos_codigo", "codigo_barras"),
        Index("idx_productos_nombre", "nombre"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    sku: Mapped[str | None] = mapped_column(Text, unique=True)
    codigo_barras: Mapped[str | None] = mapped_column(Text, unique=True)  # 1D/2D, var.
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    iva_tasa: Mapped[Decimal] = mapped_column(
        Numeric(4, 3), nullable=False, server_default=text("0.160")
    )  # 0.000 si exento/0%
    existencia: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), nullable=False, server_default=text("0")
    )
    controla_stock: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
