"""Devolución simple total/parcial por folio (PRD §3.3, AT-5.x).

Layout espejo de Venta: busca por folio (escaneable), topa a lo vendido,
reembolsa según medio y reintegra stock.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.deps import get_mp_client, require_turno, templates
from app.models import Cajero, Pago, Turno
from app.models.enums import etiqueta_medio
from app.services import configuracion as cfg_svc
from app.services import devoluciones, printing
from app.services.mp_point import MPClient

router = APIRouter(prefix="/devolucion", tags=["devolucion"])


def _dec(v: str) -> Decimal:
    try:
        return Decimal((v or "0").strip())
    except InvalidOperation:
        return Decimal("0")


def _lineas_ctx(session: Session, venta):
    """Líneas con su cantidad restante por devolver."""
    return [
        {
            "linea": ln,
            "restante": Decimal(ln.cantidad)
            - devoluciones.cantidad_devuelta(session, ln.id),
        }
        for ln in venta.lineas
    ]


@router.get("", response_class=HTMLResponse)
def devolucion_home(
    request: Request,
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    cajero, _ = ctx
    return templates.TemplateResponse(
        request, "devolucion.html", {"cajero": cajero, "active_nav": "devolucion"}
    )


@router.post("/buscar", response_class=HTMLResponse)
def buscar(
    request: Request,
    folio: str = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    venta = devoluciones.buscar_por_folio(session, folio)
    if venta is None or venta.estado not in ("pagada", "devuelta_parcial"):
        return templates.TemplateResponse(
            request,
            "partials/_devolucion_lineas.html",
            {
                "venta": None,
                "aviso": f"Folio «{folio.strip()}» no encontrado o no devolvible.",
            },
        )
    return templates.TemplateResponse(
        request,
        "partials/_devolucion_lineas.html",
        {"venta": venta, "lineas": _lineas_ctx(session, venta), "aviso": None},
    )


@router.post("/confirmar", response_class=HTMLResponse)
async def confirmar(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
    client: MPClient = Depends(get_mp_client),
):
    cajero, turno = ctx
    form = await request.form()
    folio = form.get("folio", "")
    venta = devoluciones.buscar_por_folio(session, folio)
    if venta is None:
        return templates.TemplateResponse(
            request,
            "partials/_devolucion_lineas.html",
            {"venta": None, "aviso": "Venta no encontrada."},
        )

    items = []
    for k, v in form.items():
        if not k.startswith("cant_") or _dec(v) <= 0:
            continue
        try:
            linea_id = int(k[5:])
        except ValueError:
            continue  # campo malformado (p. ej. 'cant_abc'): ignorar, no romper
        items.append(
            devoluciones.ItemDevolucion(venta_linea_id=linea_id, cantidad=_dec(v))
        )
    try:
        dev = devoluciones.crear_devolucion(
            session, venta, items, cajero_id=cajero.id, turno_id=turno.id, client=client
        )
    except devoluciones.ExcedeVendido:
        session.rollback()
        return templates.TemplateResponse(
            request,
            "partials/_devolucion_lineas.html",
            {
                "venta": venta,
                "lineas": _lineas_ctx(session, venta),
                "aviso": "No puedes devolver más de lo vendido.",
            },
            status_code=400,
        )
    except devoluciones.VentaNoDevolvible:
        session.rollback()
        return templates.TemplateResponse(
            request,
            "partials/_devolucion_lineas.html",
            {
                "venta": venta,
                "lineas": _lineas_ctx(session, venta),
                "aviso": "Selecciona al menos una cantidad a devolver.",
            },
            status_code=400,
        )
    session.commit()
    # Ticket de devolución: imprime automáticamente (tolerante a fallos). El
    # medio de reembolso = medio del pago aprobado de la venta original.
    pago = session.scalar(
        select(Pago).where(Pago.venta_id == venta.id, Pago.estado == "aprobado")
    )
    medio_label = etiqueta_medio(pago.medio) if pago else ""
    cfg = cfg_svc.ticket_kwargs(session)
    res = printing.imprimir_texto(
        printing.construir_ticket_devolucion(
            dev,
            venta,
            cajero_nombre=cajero.nombre,
            business_name=cfg["business_name"],
            evento=cfg["evento"],
            domicilio=cfg["domicilio"],
            telefono=cfg["telefono"],
            medio=medio_label,
            fecha_formato=cfg["fecha_formato"],
            tz_offset=cfg["tz_offset"],
        ),
        settings=get_settings(),
    )
    return templates.TemplateResponse(
        request,
        "partials/_devolucion_ok.html",
        {
            "venta": venta,
            "dev": dev,
            "medio": medio_label,
            "print_ok": res.ok,
            "print_error": res.error,
        },
    )
