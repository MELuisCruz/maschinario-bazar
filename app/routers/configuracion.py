"""Configuración del ticket — edición por el administrador.

Pantalla solo-admin para editar los textos del ticket (establecimiento, evento,
domicilio, teléfono, mensaje de pie). Persiste en la tabla `configuracion`.
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, templates
from app.models import Cajero
from app.services import api_keys
from app.services import configuracion as cfg_svc
from app.services import divisas
from app.services import impresora_admin

router = APIRouter(prefix="/configuracion", tags=["configuracion"])
log = logging.getLogger("pos.configuracion")


def _api_mp_panel(request: Request, msg=None, error=None):
    return templates.TemplateResponse(
        request,
        "partials/_api_mp_estado.html",
        {"mp": api_keys.estado_mp(), "msg": msg, "error": error},
    )


def _impresora_panel(request: Request, estado=None):
    return templates.TemplateResponse(
        request,
        "partials/_impresora_estado.html",
        {"impresora": estado or impresora_admin.estado()},
    )


def _render(request: Request, session: Session, cajero: Cajero, msg=None, error=None):
    rates = divisas.get_rates(session)
    return templates.TemplateResponse(
        request,
        "configuracion.html",
        {
            "cajero": cajero,
            "active_nav": "configuracion",
            "cfg": cfg_svc.get_config(session),
            "fx_usd": rates["USD"],
            "fx_eur": rates["EUR"],
            "fx_fecha": divisas.fecha_actualizacion(session),
            "msg": msg,
            "error": error,
        },
    )


@router.get("", response_class=HTMLResponse)
def configuracion_home(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),
):
    return _render(request, session, cajero)


@router.post("", response_class=HTMLResponse)
def guardar(
    request: Request,
    ticket_establecimiento: str = Form(""),
    ticket_evento: str = Form(""),
    ticket_domicilio: str = Form(""),
    ticket_telefono: str = Form(""),
    ticket_pie: str = Form(""),
    ticket_fecha_formato: str = Form(""),
    ticket_tz_offset: str = Form(""),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),
):
    cfg_svc.set_config(
        session,
        {
            "ticket_establecimiento": ticket_establecimiento,
            "ticket_evento": ticket_evento,
            "ticket_domicilio": ticket_domicilio,
            "ticket_telefono": ticket_telefono,
            "ticket_pie": ticket_pie,
            "ticket_fecha_formato": ticket_fecha_formato,
            "ticket_tz_offset": ticket_tz_offset,
        },
    )
    session.commit()
    return _render(request, session, cajero, msg="Configuración del ticket guardada.")


@router.post("/fx", response_class=HTMLResponse)
def guardar_fx(
    request: Request,
    fx_usd_mxn: str = Form(""),
    fx_eur_mxn: str = Form(""),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),
):
    """Guarda los tipos de cambio manuales (MXN por unidad)."""
    try:
        usd = Decimal((fx_usd_mxn or "0").strip() or "0")
        eur = Decimal((fx_eur_mxn or "0").strip() or "0")
    except InvalidOperation:
        usd = eur = Decimal("0")
    divisas.set_rates(session, usd, eur)
    session.commit()
    return _render(request, session, cajero, msg="Tipos de cambio guardados.")


@router.post("/fx-actualizar", response_class=HTMLResponse)
def fx_actualizar(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),
):
    """Trae los tipos de cambio sugeridos desde la API pública y los guarda."""
    try:
        api = divisas.actualizar_desde_api(session)
        session.commit()
        msg = (
            f"Tipos de cambio actualizados desde API: "
            f"USD={api['USD']}, EUR={api['EUR']} ({api.get('fecha', '')})."
        )
        return _render(request, session, cajero, msg=msg)
    except Exception:  # sin internet / API caída
        session.rollback()
        # Se registra el detalle en el servidor; al usuario un mensaje genérico
        # (no se filtran detalles internos al cliente).
        log.exception("Fallo al consultar la API de tipo de cambio")
        return _render(
            request,
            session,
            cajero,
            error="No se pudo consultar la API de tipo de cambio. Intenta más tarde.",
        )


# --- APIs / credenciales (HTMX) -------------------------------------------


@router.get("/api/mp/estado", response_class=HTMLResponse)
def api_mp_estado(
    request: Request,
    cajero: Cajero = Depends(require_admin),
):
    """Testigo del estado del token de Mercado Pago (carga diferida en la UI)."""
    return _api_mp_panel(request)


@router.post("/api/mp", response_class=HTMLResponse)
def api_mp_actualizar(
    request: Request,
    mp_token: str = Form(""),
    cajero: Cajero = Depends(require_admin),
):
    """Rota el Access Token de Mercado Pago (valida antes de guardar)."""
    ok, mensaje = api_keys.actualizar_mp(mp_token)
    if ok:
        log.info("Token MP rotado desde Configuración por cajero id=%s", cajero.id)
        return _api_mp_panel(request, msg=mensaje)
    return _api_mp_panel(request, error=mensaje)


# --- Impresora (HTMX) -----------------------------------------------------


@router.get("/impresora/estado", response_class=HTMLResponse)
def impresora_estado(
    request: Request,
    cajero: Cajero = Depends(require_admin),
):
    """Testigo del estado de la impresora (verde disponible / rojo no)."""
    return _impresora_panel(request)


@router.post("/impresora/reconectar", response_class=HTMLResponse)
def impresora_reconectar(
    request: Request,
    cajero: Cajero = Depends(require_admin),
):
    """Reintenta el puente USB de la impresora y devuelve el estado nuevo."""
    log.info("Reconexión de impresora solicitada por cajero id=%s", cajero.id)
    return _impresora_panel(request, estado=impresora_admin.reconectar())
