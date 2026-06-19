"""Configuración del ticket — edición por el administrador.

Pantalla solo-admin para editar los textos del ticket (establecimiento, evento,
domicilio, teléfono, mensaje de pie). Persiste en la tabla `configuracion`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, templates
from app.models import Cajero
from app.services import configuracion as cfg_svc

router = APIRouter(prefix="/configuracion", tags=["configuracion"])


def _render(request: Request, session: Session, cajero: Cajero, msg=None):
    return templates.TemplateResponse(
        request,
        "configuracion.html",
        {
            "cajero": cajero,
            "active_nav": "configuracion",
            "cfg": cfg_svc.get_config(session),
            "msg": msg,
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
        },
    )
    session.commit()
    return _render(request, session, cajero, msg="Configuración del ticket guardada.")
