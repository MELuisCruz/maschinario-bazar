"""Devolución simple total/parcial por folio (PRD §3.3, AT-5.x).

Topa lo devuelto a lo vendido (AT-5.2), reintegra stock (AT-5.4) y reembolsa
según el medio original: efectivo desde caja, tarjeta vía refund de la order
(AT-5.3, INTEGRATION §7). SUPUESTO v1: reembolso total del pago con tarjeta.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Devolucion,
    DevolucionLinea,
    Pago,
    Producto,
    Venta,
    VentaLinea,
)
from app.services import stock
from app.services.money import q2

_DEVOLVIBLES = ("pagada", "devuelta_parcial")


class VentaNoDevolvible(Exception):
    """La venta no existe o no está en un estado devolvible."""


class ExcedeVendido(Exception):
    """Se intenta devolver más de lo vendido/restante (AT-5.2)."""


@dataclass
class ItemDevolucion:
    venta_linea_id: int
    cantidad: Decimal


def buscar_por_folio(session: Session, folio: str) -> Venta | None:
    return session.scalar(select(Venta).where(Venta.folio == (folio or "").strip()))


def cantidad_devuelta(session: Session, venta_linea_id: int) -> Decimal:
    total = session.scalar(
        select(func.coalesce(func.sum(DevolucionLinea.cantidad), 0)).where(
            DevolucionLinea.venta_linea_id == venta_linea_id
        )
    )
    return Decimal(total or 0)


def _unidad_neta(linea: VentaLinea) -> Decimal:
    """Importe neto por unidad de la línea (incluye el descuento prorrateado)."""
    if linea.cantidad == 0:
        return Decimal("0")
    return Decimal(linea.importe) / Decimal(linea.cantidad)


def crear_devolucion(
    session: Session,
    venta: Venta,
    items: list[ItemDevolucion],
    *,
    cajero_id: int,
    turno_id: int,
    client=None,
    motivo: str | None = None,
) -> Devolucion:
    if venta is None or venta.estado not in _DEVOLVIBLES:
        raise VentaNoDevolvible()

    items = [it for it in items if Decimal(it.cantidad) > 0]
    if not items:
        raise VentaNoDevolvible()

    lineas_por_id = {ln.id: ln for ln in venta.lineas}
    dev = Devolucion(
        venta_id=venta.id,
        turno_id=turno_id,
        cajero_id=cajero_id,
        monto=Decimal("0"),
        motivo=motivo,
    )
    session.add(dev)
    session.flush()

    monto_total = Decimal("0.00")
    for it in items:
        linea = lineas_por_id.get(it.venta_linea_id)
        if linea is None:
            raise VentaNoDevolvible()
        cantidad = Decimal(it.cantidad)
        restante = Decimal(linea.cantidad) - cantidad_devuelta(session, linea.id)
        if cantidad > restante:  # AT-5.2
            raise ExcedeVendido()

        importe = q2(cantidad * _unidad_neta(linea))
        session.add(
            DevolucionLinea(
                devolucion_id=dev.id,
                venta_linea_id=linea.id,
                cantidad=cantidad,
                importe=importe,
            )
        )
        monto_total += importe

        # Reintegro de stock (AT-5.4).
        producto = session.get(Producto, linea.producto_id)
        if producto is not None:
            stock.reintegrar(session, producto, cantidad, venta.folio, cajero_id)

    dev.monto = q2(monto_total)

    # Reembolso según medio original (AT-5.3).
    pago_tarjeta = session.scalar(
        select(Pago).where(
            Pago.venta_id == venta.id,
            Pago.medio == "tarjeta_point",
            Pago.estado == "aprobado",
        )
    )
    if pago_tarjeta is not None and client is not None:
        client.refund_order(pago_tarjeta.mp_order_id)
    # Efectivo: se devuelve de caja, sin API.

    _actualizar_estado_venta(session, venta)
    session.flush()
    return dev


def _actualizar_estado_venta(session: Session, venta: Venta) -> None:
    """Marca la venta como devuelta_total o devuelta_parcial."""
    total_vendido = sum((Decimal(ln.cantidad) for ln in venta.lineas), Decimal("0"))
    total_devuelto = sum(
        (cantidad_devuelta(session, ln.id) for ln in venta.lineas), Decimal("0")
    )
    if total_devuelto >= total_vendido:
        venta.estado = "devuelta_total"
    elif total_devuelto > 0:
        venta.estado = "devuelta_parcial"
