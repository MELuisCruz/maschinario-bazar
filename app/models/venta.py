"""Ventas y sus líneas (DATA_MODEL.md §2).

`venta_lineas` guarda snapshots inmutables de descripcion/precio_unit/iva_tasa
al momento de la venta (invariante §3).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import EstadoVenta, estado_venta_enum


class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        Index("idx_ventas_turno", "turno_id"),
        Index("idx_ventas_fecha", "creado_en"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    folio: Mapped[str] = mapped_column(Text, nullable=False, unique=True)  # imprimible
    turno_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("turnos.id"), nullable=False
    )
    cajero_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cajeros.id"), nullable=False
    )
    estado: Mapped[EstadoVenta] = mapped_column(
        estado_venta_enum, nullable=False, server_default=text("'abierta'")
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    descuento_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )  # agregado: descuentos de línea + global (informativo en ticket)
    descuento_global: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )  # descuento a la venta completa (PRD §3.1); entrada del cálculo
    iva_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    requiere_factura: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )  # casilla CFDI (público en general)
    exportada_fiscal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )  # ya incluida en export para timbrado externo
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    cerrado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    lineas: Mapped[list["VentaLinea"]] = relationship(
        back_populates="venta", cascade="all, delete-orphan", passive_deletes=True
    )
    pagos: Mapped[list["Pago"]] = relationship(  # noqa: F821
        back_populates="venta", cascade="all, delete-orphan", passive_deletes=True
    )


class VentaLinea(Base):
    __tablename__ = "venta_lineas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_venta_lineas_cantidad_positiva"),
        Index("idx_lineas_venta", "venta_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    venta_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False
    )
    producto_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("productos.id"), nullable=False
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)  # snapshot nombre
    notas: Mapped[str | None] = mapped_column(Text)  # trazabilidad (producto especial)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    precio_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )  # snapshot precio EN MXN (usado para totales)
    # Divisa de captura por línea. MXN por defecto; si es USD/EUR se guarda el
    # monto en esa divisa y el tipo de cambio aplicado (precio_unit = monto*tc).
    divisa: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'MXN'")
    )
    precio_divisa: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    tipo_cambio: Mapped[Decimal | None] = mapped_column(Numeric(14, 6))
    iva_tasa: Mapped[Decimal] = mapped_column(
        Numeric(4, 3), nullable=False
    )  # snapshot tasa
    descuento: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, server_default=text("0")
    )
    importe: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )  # (cantidad*precio_unit) - descuento

    venta: Mapped["Venta"] = relationship(back_populates="lineas")
