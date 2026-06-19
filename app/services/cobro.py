"""Cobro: efectivo y tarjeta (PRD §3.2, AT-3.x / AT-4.x).

Invariante (DATA_MODEL.md §3): una venta pasa a `pagada` solo cuando la suma de
pagos `aprobado` cubre el total. El efectivo opera **offline** (no toca red).
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Pago, Venta
from app.services import mp_point, stock
from app.services.money import cambio_efectivo, q2


class PagoInsuficiente(Exception):
    """El efectivo recibido es menor al total (AT-3.2)."""


class VentaNoCobrable(Exception):
    """La venta no está abierta o no tiene líneas."""


def _total_aprobado(session: Session, venta: Venta) -> Decimal:
    pagos = session.scalars(
        select(Pago).where(Pago.venta_id == venta.id, Pago.estado == "aprobado")
    ).all()
    return q2(sum((p.monto for p in pagos), Decimal("0")))


def _finalizar_si_cubierta(session: Session, venta: Venta) -> None:
    """Marca `pagada` y descuenta stock cuando los pagos aprobados cubren el total."""
    if venta.estado == "pagada":
        return
    if _total_aprobado(session, venta) >= venta.total:
        stock.descontar_venta(session, venta)  # AT-6.3
        venta.estado = "pagada"
        venta.cerrado_en = datetime.now(timezone.utc)
        session.flush()


def cobrar_efectivo(session: Session, venta: Venta, recibido: Decimal) -> Pago | None:
    """Registra un pago en efectivo y cierra la venta si queda cubierta (AT-3.1).

    Si el total es 0 (venta 100% descontada) NO se registra pago —violaría el
    CHECK `monto > 0`— y la venta se cierra directamente; devuelve None.
    """
    if venta.estado != "abierta" or not venta.lineas:
        raise VentaNoCobrable()
    if venta.total <= 0:
        _finalizar_si_cubierta(session, venta)  # 0 >= 0 → cierra sin pago
        return None
    recibido = q2(recibido)
    if recibido < venta.total:  # AT-3.2: nunca pagada por debajo del total
        raise PagoInsuficiente()

    pago = Pago(
        venta_id=venta.id,
        medio="efectivo",
        monto=venta.total,
        recibido=recibido,
        cambio=cambio_efectivo(venta.total, recibido),
        estado="aprobado",  # el efectivo se aprueba en el acto (offline)
    )
    session.add(pago)
    session.flush()
    _finalizar_si_cubierta(session, venta)
    return pago


# --- Tarjeta (Mercado Pago Point · API de Orders) -------------------------


def _cancelar_order_previa_en_terminal(session: Session, client) -> None:
    """Cancela la última order en espera de la terminal (AT-4.5, INTEGRATION §6)."""
    previo = session.scalars(
        select(Pago)
        .where(
            Pago.medio == "tarjeta_point",
            Pago.estado == "pendiente",
            Pago.mp_order_id.is_not(None),
        )
        .order_by(Pago.id.desc())
    ).first()
    if previo is not None:
        try:
            client.cancel_order(previo.mp_order_id)
        except mp_point.MPError:
            pass  # mejor esfuerzo; la nueva key evita el doble cobro
        previo.estado = "cancelado"
        session.flush()


def iniciar_tarjeta(session: Session, venta: Venta, client, terminal_id: str) -> Pago:
    """Crea la order en Point y persiste un pago pendiente (AT-4.1).

    Maneja 409 `already_queued` (cancela la previa y reintenta) y 409
    `idempotency_key_already_used` (genera key nueva y reintenta).
    """
    if venta.estado != "abierta" or not venta.lineas:
        raise VentaNoCobrable()
    if venta.total <= 0:  # una venta sin saldo no se cobra con tarjeta
        raise VentaNoCobrable()

    key = mp_point.new_idempotency_key()
    try:
        order = client.create_order(
            idempotency_key=key,
            external_reference=venta.folio,
            amount=venta.total,
            terminal_id=terminal_id,
        )
    except mp_point.MPConflictQueued:
        _cancelar_order_previa_en_terminal(session, client)  # AT-4.5
        key = mp_point.new_idempotency_key()
        order = client.create_order(
            idempotency_key=key,
            external_reference=venta.folio,
            amount=venta.total,
            terminal_id=terminal_id,
        )
    except mp_point.MPIdempotencyReused:
        key = mp_point.new_idempotency_key()  # AT-4.6
        order = client.create_order(
            idempotency_key=key,
            external_reference=venta.folio,
            amount=venta.total,
            terminal_id=terminal_id,
        )

    pago = Pago(
        venta_id=venta.id,
        medio="tarjeta_point",
        monto=venta.total,
        estado="pendiente",  # nunca aprobado sin confirmación (AT-4.4)
        mp_order_id=order.get("id"),
        mp_idempotency=key,
    )
    session.add(pago)
    session.flush()
    return pago


def conciliar_tarjeta(session: Session, pago: Pago, client) -> str:
    """Consulta el estado de la order (GET) y resuelve el pago (AT-4.2..4.4).

    Solo el resultado del GET marca `aprobado`; ante respuesta ambigua/timeout
    el pago permanece `pendiente` (la excepción se propaga al llamador).
    """
    order = client.get_order(pago.mp_order_id)
    estado = mp_point.estado_desde_order(order)
    pago.estado = estado
    if estado == "aprobado":
        # Guarda tipo (crédito/débito), marca y últimos 4 para el ticket.
        datos = mp_point.datos_tarjeta_desde_order(order)
        pago.mp_payment_type = datos.get("tipo")
        pago.mp_card_brand = datos.get("marca")
        pago.mp_card_last4 = datos.get("last4")
    session.flush()
    if estado == "aprobado":
        venta = session.get(Venta, pago.venta_id)
        _finalizar_si_cubierta(session, venta)  # AT-4.2 → venta pagada
    return estado


def cancelar_tarjeta(session: Session, pago: Pago, client) -> None:
    """Cancela la order y deja el pago cancelado (INTEGRATION §6)."""
    client.cancel_order(pago.mp_order_id)
    pago.estado = "cancelado"
    session.flush()
