"""Corte de caja / turno (PRD §3.2, AT-7.x).

Efectivo esperado = fondo inicial + ventas en efectivo − devoluciones en
efectivo, desglosado por medio de pago. No se cierra con ventas abiertas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Devolucion, Pago, Turno, Venta
from app.services.money import q2


class VentasAbiertas(Exception):
    """No se puede cerrar el turno con ventas abiertas (AT-7.3)."""


@dataclass
class ResumenTurno:
    fondo_inicial: Decimal
    por_medio: dict[str, Decimal]
    ventas_efectivo: Decimal
    devoluciones_efectivo: Decimal
    esperado_efectivo: Decimal
    num_tickets: int
    total_ventas: Decimal = field(default=Decimal("0.00"))


def _venta_es_efectivo(session: Session, venta_id: int) -> bool:
    """Una venta se reembolsa en efectivo si no tuvo pago aprobado con tarjeta."""
    tarjeta = session.scalar(
        select(func.count())
        .select_from(Pago)
        .where(
            Pago.venta_id == venta_id,
            Pago.medio == "tarjeta_point",
            Pago.estado == "aprobado",
        )
    )
    return not tarjeta


def ventas_abiertas(session: Session, turno_id: int) -> int:
    """Ventas abiertas con al menos una línea (las vacías no bloquean)."""
    return (
        session.scalar(
            select(func.count(func.distinct(Venta.id)))
            .select_from(Venta)
            .join(Venta.lineas)
            .where(Venta.turno_id == turno_id, Venta.estado == "abierta")
        )
        or 0
    )


def resumen(session: Session, turno: Turno) -> ResumenTurno:
    # Pagos aprobados por medio, de ventas del turno.
    filas = session.execute(
        select(Pago.medio, func.coalesce(func.sum(Pago.monto), 0))
        .join(Venta, Venta.id == Pago.venta_id)
        .where(Venta.turno_id == turno.id, Pago.estado == "aprobado")
        .group_by(Pago.medio)
    ).all()
    por_medio = {medio: q2(monto) for medio, monto in filas}
    ventas_efectivo = por_medio.get("efectivo", Decimal("0.00"))

    # Devoluciones en efectivo del turno.
    devs = session.scalars(
        select(Devolucion).where(Devolucion.turno_id == turno.id)
    ).all()
    devoluciones_efectivo = q2(
        sum(
            (d.monto for d in devs if _venta_es_efectivo(session, d.venta_id)),
            Decimal("0"),
        )
    )

    num_tickets = (
        session.scalar(
            select(func.count())
            .select_from(Venta)
            .where(
                Venta.turno_id == turno.id,
                Venta.estado.in_(("pagada", "devuelta_parcial", "devuelta_total")),
            )
        )
        or 0
    )

    esperado = q2(turno.fondo_inicial + ventas_efectivo - devoluciones_efectivo)
    total_ventas = q2(sum(por_medio.values(), Decimal("0")))

    return ResumenTurno(
        fondo_inicial=q2(turno.fondo_inicial),
        por_medio=por_medio,
        ventas_efectivo=ventas_efectivo,
        devoluciones_efectivo=devoluciones_efectivo,
        esperado_efectivo=esperado,
        num_tickets=num_tickets,
        total_ventas=total_ventas,
    )


def diferencia(esperado: Decimal, contado: Decimal) -> Decimal:
    """contado − esperado (positivo = sobrante; negativo = faltante)."""
    return q2(Decimal(contado) - Decimal(esperado))


def cerrar_turno(
    session: Session, turno: Turno, efectivo_contado: Decimal, notas: str | None = None
) -> tuple[ResumenTurno, Decimal]:
    """Cierra el turno y devuelve (resumen, diferencia). Bloquea si hay ventas abiertas."""
    if ventas_abiertas(session, turno.id) > 0:
        raise VentasAbiertas()
    res = resumen(session, turno)
    dif = diferencia(res.esperado_efectivo, efectivo_contado)
    turno.efectivo_contado = q2(efectivo_contado)
    turno.notas = notas
    turno.cerrado_en = datetime.now(timezone.utc)
    session.flush()
    return res, dif
