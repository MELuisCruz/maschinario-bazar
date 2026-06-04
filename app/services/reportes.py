"""Reportes de ventas por periodo / medio / cajero (PRD §3.7, AT-8.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Cajero, Pago, Venta
from app.services.money import q2

_VENDIDAS = ("pagada", "devuelta_parcial", "devuelta_total")


@dataclass
class Reporte:
    desde: datetime
    hasta: datetime
    num_tickets: int = 0
    total: Decimal = field(default=Decimal("0.00"))
    iva: Decimal = field(default=Decimal("0.00"))
    ticket_promedio: Decimal = field(default=Decimal("0.00"))
    por_medio: dict[str, Decimal] = field(default_factory=dict)
    por_cajero: dict[str, Decimal] = field(default_factory=dict)


def generar(
    session: Session, desde: datetime, hasta: datetime, cajero_id: int | None = None
) -> Reporte:
    cond = [
        Venta.estado.in_(_VENDIDAS),
        Venta.creado_en >= desde,
        Venta.creado_en < hasta,
    ]
    if cajero_id:
        cond.append(Venta.cajero_id == cajero_id)

    ventas = session.scalars(select(Venta).where(*cond)).all()
    num = len(ventas)
    total = q2(sum((v.total for v in ventas), Decimal("0")))
    iva = q2(sum((v.iva_total for v in ventas), Decimal("0")))
    promedio = q2(total / num) if num else Decimal("0.00")

    # Por medio de pago (pagos aprobados de esas ventas).
    medio_rows = session.execute(
        select(Pago.medio, func.coalesce(func.sum(Pago.monto), 0))
        .join(Venta, Venta.id == Pago.venta_id)
        .where(Pago.estado == "aprobado", *cond)
        .group_by(Pago.medio)
    ).all()
    por_medio = {m: q2(v) for m, v in medio_rows}

    # Por cajero.
    cajero_rows = session.execute(
        select(Cajero.nombre, func.coalesce(func.sum(Venta.total), 0))
        .join(Cajero, Cajero.id == Venta.cajero_id)
        .where(*cond)
        .group_by(Cajero.nombre)
    ).all()
    por_cajero = {n: q2(v) for n, v in cajero_rows}

    return Reporte(
        desde=desde,
        hasta=hasta,
        num_tickets=num,
        total=total,
        iva=iva,
        ticket_promedio=promedio,
        por_medio=por_medio,
        por_cajero=por_cajero,
    )
