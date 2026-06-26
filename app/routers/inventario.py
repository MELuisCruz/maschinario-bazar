"""Inventario: EXISTENCIAS de los productos (PRD §3.4, AT-6.x).

Separado del Catálogo (que gestiona los productos): aquí solo se ven y ajustan
las existencias. Acceso: el cajero CONSULTA (solo lectura); solo el admin
reabastece o ajusta el stock.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, require_cajero, templates
from app.models import Cajero, Producto
from app.services import catalogo as cat

router = APIRouter(prefix="/inventario", tags=["inventario"])


def _dec(v: str, default="0") -> Decimal:
    try:
        return Decimal((v or default).strip() or default)
    except InvalidOperation:
        return Decimal(default)


def _listar(session: Session) -> list[Producto]:
    return list(
        session.scalars(
            select(Producto)
            .where(Producto.activo.is_(True))
            .order_by(Producto.nombre)
            .limit(200)
        ).all()
    )


def _render(request, session, cajero, *, msg=None, error=None, status=200):
    return templates.TemplateResponse(
        request,
        "inventario.html",
        {
            "cajero": cajero,
            "productos": _listar(session),
            "active_nav": "inventario",
            "error": error,
            "msg": msg,
        },
        status_code=status,
    )


@router.get("", response_class=HTMLResponse)
def inventario_home(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),  # el cajero consulta existencias
    msg: str | None = None,
):
    return _render(request, session, cajero, msg=msg)


@router.post("/{producto_id}/reabastecer", response_class=HTMLResponse)
def reabastecer(
    request: Request,
    producto_id: int,
    cantidad: str = Form(...),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),  # solo admin cambia existencias
):
    producto = session.get(Producto, producto_id)
    if producto is None or not producto.activo:
        return _render(request, session, cajero, error="Producto no encontrado.", status=404)
    try:
        cat.reabastecer(session, producto, _dec(cantidad), cajero_id=cajero.id)
    except ValueError as exc:
        session.rollback()
        return _render(request, session, cajero, error=str(exc), status=400)
    session.commit()
    return _render(
        request,
        session,
        cajero,
        msg=f"«{producto.nombre}»: existencia ahora {producto.existencia:g}.",
    )


@router.post("/{producto_id}/ajustar", response_class=HTMLResponse)
def ajustar(
    request: Request,
    producto_id: int,
    existencia: str = Form(...),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),  # solo admin cambia existencias
):
    """Fija la existencia a un valor exacto (registra el delta como 'ajuste')."""
    producto = session.get(Producto, producto_id)
    if producto is None or not producto.activo:
        return _render(request, session, cajero, error="Producto no encontrado.", status=404)
    nueva = _dec(existencia)
    if nueva < 0:
        return _render(
            request, session, cajero, error="La existencia no puede ser negativa.", status=400
        )
    cat.ajustar_stock(session, producto, nueva, cajero_id=cajero.id)
    session.commit()
    return _render(
        request,
        session,
        cajero,
        msg=f"«{producto.nombre}»: existencia ajustada a {producto.existencia:g}.",
    )
