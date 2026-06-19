"""Ticket y reimpresión por folio (THERMAL_TICKET_SPEC §5, AT-9.x).

La reimpresión emite un ticket idéntico al original más la leyenda al pie; no
altera datos de la venta ni del pago.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.deps import require_turno, templates
from app.models import Cajero, Turno, Venta
from app.services import configuracion as cfg_svc
from app.services import printing

router = APIRouter(prefix="/reimpresion", tags=["reimpresion"])


def _buscar(session: Session, folio: str) -> Venta | None:
    return session.scalar(select(Venta).where(Venta.folio == (folio or "").strip()))


def _cajero_nombre(session: Session, venta: Venta) -> str:
    c = session.get(Cajero, venta.cajero_id)
    return c.nombre if c else "—"


def _ticket_cfg(session: Session) -> dict[str, str]:
    """Campos editables del ticket (admin) en los nombres que espera printing."""
    c = cfg_svc.get_config(session)
    return {
        "business_name": c["ticket_establecimiento"],
        "evento": c["ticket_evento"],
        "domicilio": c["ticket_domicilio"],
        "telefono": c["ticket_telefono"],
        "pie": c["ticket_pie"],
    }


@router.get("", response_class=HTMLResponse)
def reimpresion_home(
    request: Request,
    folio: str = "",
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    cajero, _ = ctx
    preview = None
    venta = _buscar(session, folio) if folio else None
    if venta is not None:
        preview = printing.construir_ticket_texto(
            venta,
            cajero_nombre=_cajero_nombre(session, venta),
            pagos=venta.pagos,
            **_ticket_cfg(session),
        )
    return templates.TemplateResponse(
        request,
        "reimpresion.html",
        {
            "cajero": cajero,
            "active_nav": "reimpresion",
            "folio": folio,
            "venta": venta,
            "preview": preview,
            "aviso": None,
            "msg": None,
        },
    )


@router.post("/buscar", response_class=HTMLResponse)
def buscar(
    request: Request,
    folio: str = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    venta = _buscar(session, folio)
    return _render_preview(request, session, venta, folio)


@router.post("/imprimir", response_class=HTMLResponse)
def imprimir(
    request: Request,
    folio: str = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    venta = _buscar(session, folio)
    msg = aviso = None
    if venta is not None:
        res = printing.imprimir_ticket(
            venta,
            cajero_nombre=_cajero_nombre(session, venta),
            pagos=venta.pagos,
            reimpresion=True,
            fecha_reimpresion=datetime.now(timezone.utc),
            settings=get_settings(),
            **_ticket_cfg(session),
        )
        if res.ok:
            msg = "Ticket reenviado a la impresora."
        else:
            # Impresora no disponible: no rompe nada; el ticket sigue disponible.
            aviso = f"Impresora no disponible ({res.error}). Reintenta más tarde."
    return _render_preview(request, session, venta, folio, msg=msg, aviso=aviso)


def _render_preview(
    request, session, venta, folio, msg=None, aviso=None
) -> HTMLResponse:
    preview = None
    if venta is None:
        aviso = aviso or f"Folio «{folio.strip()}» no encontrado."
    else:
        preview = printing.construir_ticket_texto(
            venta,
            cajero_nombre=_cajero_nombre(session, venta),
            pagos=venta.pagos,
            **_ticket_cfg(session),
        )
    return templates.TemplateResponse(
        request,
        "partials/_reimpresion_preview.html",
        {
            "venta": venta,
            "preview": preview,
            "folio": folio,
            "msg": msg,
            "aviso": aviso,
        },
    )
