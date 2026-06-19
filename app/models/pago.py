"""Pagos: uno o varios por venta (efectivo, tarjeta Point) (DATA_MODEL.md §2).

`mp_order_id` es único cuando existe (índice parcial). Un pago con tarjeta nunca
se marca 'aprobado' sin confirmación de Mercado Pago (invariante §3).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
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
from app.models.enums import EstadoPago, MedioPago, estado_pago_enum, medio_pago_enum


class Pago(Base):
    __tablename__ = "pagos"
    __table_args__ = (
        CheckConstraint("monto > 0", name="ck_pagos_monto_positivo"),
        Index("idx_pagos_venta", "venta_id"),
        Index(
            "idx_pagos_mp_order",
            "mp_order_id",
            unique=True,
            postgresql_where=text("mp_order_id IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    venta_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False
    )
    medio: Mapped[MedioPago] = mapped_column(medio_pago_enum, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    recibido: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # efectivo
    cambio: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # efectivo
    estado: Mapped[EstadoPago] = mapped_column(
        estado_pago_enum, nullable=False, server_default=text("'pendiente'")
    )
    mp_order_id: Mapped[str | None] = mapped_column(Text)  # id de la order en MP
    mp_idempotency: Mapped[str | None] = mapped_column(Text)  # llave de idempotencia
    # Datos de la tarjeta (de la order aprobada) para el ticket: tipo (crédito/
    # débito), marca (visa/master/…) y últimos 4 dígitos.
    mp_payment_type: Mapped[str | None] = mapped_column(Text)
    mp_card_brand: Mapped[str | None] = mapped_column(Text)
    mp_card_last4: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    venta: Mapped["Venta"] = relationship(back_populates="pagos")  # noqa: F821
