"""Configuración del ticket — edición por el administrador.

Pantalla solo-admin para editar los textos del ticket (establecimiento, evento,
domicilio, teléfono, mensaje de pie). Persiste en la tabla `configuracion`.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, templates
from app.models import Cajero
from app.services import configuracion as cfg_svc
from app.services import divisas

router = APIRouter(prefix="/configuracion", tags=["configuracion"])


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
    fx_usd_mxn: str = Form(""),
    fx_eur_mxn: str = Form(""),
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
    # Tipos de cambio manuales (MXN por unidad). Inválidos → 0 (se ignoran al usar).
    try:
        usd = Decimal((fx_usd_mxn or "0").strip() or "0")
        eur = Decimal((fx_eur_mxn or "0").strip() or "0")
    except InvalidOperation:
        usd = eur = Decimal("0")
    divisas.set_rates(session, usd, eur)
    session.commit()
    return _render(request, session, cajero, msg="Configuración guardada.")


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
    except Exception as exc:  # sin internet / API caída
        session.rollback()
        return _render(
            request,
            session,
            cajero,
            error=f"No se pudo consultar la API de tipo de cambio: {exc}",
        )
