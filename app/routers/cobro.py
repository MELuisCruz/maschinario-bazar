"""Cobro: efectivo y tarjeta Point (PRD §3.2, AT-3.x / AT-4.x).

Opera sobre la venta abierta del turno. Efectivo es offline; tarjeta se delega
a la API de Orders (ver router/servicio de tarjeta).
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.deps import get_mp_client, require_turno, templates
from app.models import Cajero, Pago, Turno
from app.services import cobro as cobro_svc
from app.services import configuracion as cfg_svc
from app.services import mp_point, printing, ventas
from app.services.mp_point import MPClient

router = APIRouter(prefix="/cobro", tags=["cobro"])
log = logging.getLogger("pos.cobro")


def _venta_activa(session: Session, turno: Turno):
    return ventas.get_or_create_venta(session, turno.id, turno.cajero_id)


@router.get("", response_class=HTMLResponse)
def cobro_home(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    cajero, turno = ctx
    venta = _venta_activa(session, turno)
    session.commit()
    if not venta.lineas:
        return RedirectResponse("/venta", status_code=303)
    return templates.TemplateResponse(
        request,
        "cobro.html",
        {"venta": venta, "cajero": cajero, "active_nav": "venta", "error": None},
    )


@router.post("/efectivo", response_class=HTMLResponse)
def cobrar_efectivo(
    request: Request,
    recibido: str = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    cajero, turno = ctx
    venta = _venta_activa(session, turno)
    try:
        monto = Decimal((recibido or "0").strip())
    except InvalidOperation:
        monto = Decimal("0")
    try:
        pago = cobro_svc.cobrar_efectivo(session, venta, monto)
    except cobro_svc.PagoInsuficiente:
        session.rollback()
        return templates.TemplateResponse(
            request,
            "cobro.html",
            {
                "venta": venta,
                "cajero": cajero,
                "active_nav": "venta",
                "error": "El efectivo recibido es menor al total.",
            },
            status_code=400,
        )
    except cobro_svc.VentaNoCobrable:
        # Venta vacía o ya cerrada: no se puede cobrar; volver a Venta sin romper.
        session.rollback()
        return RedirectResponse("/venta", status_code=303)
    session.commit()
    # Efectivo: imprime el ticket automáticamente (no rompe la venta si falla;
    # queda disponible para reimpresión por folio — AT-9.2).
    res = printing.imprimir_ticket(
        venta,
        cajero_nombre=cajero.nombre,
        pagos=venta.pagos,
        settings=get_settings(),
        **cfg_svc.ticket_kwargs(session),
    )
    return templates.TemplateResponse(
        request,
        "cobro_ok.html",
        {
            "venta": venta,
            "pago": pago,
            "cajero": cajero,
            "active_nav": "venta",
            "print_ok": res.ok,
            "print_error": res.error,
        },
    )


# --- Tarjeta (Point Smart 2 · API de Orders) ------------------------------


def _panel(
    request: Request,
    venta,
    *,
    state: str,
    pago=None,
    error=None,
    print_ok=None,
    print_error=None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/_tarjeta_panel.html",
        {
            "venta": venta,
            "state": state,
            "pago": pago,
            "error": error,
            "print_ok": print_ok,
            "print_error": print_error,
        },
    )


@router.get("/tarjeta/panel", response_class=HTMLResponse)
def tarjeta_panel(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    session.commit()
    return _panel(request, venta, state="idle")


@router.post("/tarjeta/iniciar", response_class=HTMLResponse)
def tarjeta_iniciar(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
    client: MPClient = Depends(get_mp_client),
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    terminal_id = get_settings().mp_terminal_id
    try:
        pago = cobro_svc.iniciar_tarjeta(session, venta, client, terminal_id)
    except mp_point.MPOffline:
        session.rollback()
        return _panel(  # AT-4.7: bloquea con aviso; el efectivo sigue disponible
            request,
            venta,
            state="offline",
            error="Sin conexión: el cobro con tarjeta no está disponible. Usa efectivo.",
        )
    except mp_point.MPError as exc:
        session.rollback()
        # Detalle al log del servidor; al cajero un mensaje accionable y sin
        # filtrar internals.
        log.warning("Error de Mercado Pago al iniciar cobro: %s", exc)
        return _panel(
            request,
            venta,
            state="error",
            error="No se pudo iniciar el cobro con tarjeta. Reintenta o usa efectivo.",
        )
    except cobro_svc.VentaNoCobrable:
        session.rollback()
        return _panel(
            request,
            venta,
            state="error",
            error="La venta no tiene saldo a cobrar con tarjeta.",
        )
    session.commit()
    return _panel(request, venta, state="waiting", pago=pago)


@router.get("/tarjeta/estado", response_class=HTMLResponse)
def tarjeta_estado(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
    client: MPClient = Depends(get_mp_client),
):
    cajero, turno = ctx
    venta = _venta_activa(session, turno)
    pago = session.scalars(
        select(Pago)
        .where(Pago.venta_id == venta.id, Pago.medio == "tarjeta_point")
        .order_by(Pago.id.desc())
    ).first()
    if pago is None:
        return _panel(request, venta, state="idle")
    try:
        estado = cobro_svc.conciliar_tarjeta(session, pago, client)
    except mp_point.MPOffline:
        session.rollback()
        # Ambigüedad/sin red: el pago permanece pendiente (AT-4.4); seguir sondeando.
        return _panel(request, venta, state="waiting", pago=pago)
    session.commit()
    if estado == "aprobado":
        # Igual que el efectivo: imprime el ticket automáticamente (no rompe si
        # falla; queda para reimprimir — AT-9.2).
        res = printing.imprimir_ticket(
            venta,
            cajero_nombre=cajero.nombre,
            pagos=venta.pagos,
            settings=get_settings(),
            **cfg_svc.ticket_kwargs(session),
        )
        return _panel(
            request,
            venta,
            state=estado,
            pago=pago,
            print_ok=res.ok,
            print_error=res.error,
        )
    return _panel(request, venta, state=estado, pago=pago)


@router.post("/tarjeta/cancelar", response_class=HTMLResponse)
def tarjeta_cancelar(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
    client: MPClient = Depends(get_mp_client),
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    pago = session.scalars(
        select(Pago)
        .where(
            Pago.venta_id == venta.id,
            Pago.medio == "tarjeta_point",
            Pago.estado == "pendiente",
        )
        .order_by(Pago.id.desc())
    ).first()
    if pago is not None:
        try:
            cobro_svc.cancelar_tarjeta(session, pago, client)
        except mp_point.MPError:
            pago.estado = "cancelado"
        session.commit()
    return _panel(request, venta, state="idle")
