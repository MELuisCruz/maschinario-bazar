"""Venta: escaneo, líneas, descuentos, totales (PRD §3.1, AT-2.x).

UI Jinja2 + HTMX (no SPA): el escaneo y las ediciones devuelven el parcial
`_venta_main` que reemplaza la zona central (tabla + panel de totales).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_turno, templates
from app.models import Cajero, Turno, VentaLinea
from app.services import ventas

router = APIRouter(prefix="/venta", tags=["venta"])


def _dec(value: str) -> Decimal:
    try:
        return Decimal((value or "0").strip())
    except InvalidOperation:
        return Decimal("0")


def _main(request: Request, venta, aviso: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "partials/_venta_main.html", {"venta": venta, "aviso": aviso}
    )


@router.get("", response_class=HTMLResponse)
def venta_home(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
) -> HTMLResponse:
    cajero, turno = ctx
    venta = ventas.get_or_create_venta(session, turno.id, cajero.id)
    session.commit()
    return templates.TemplateResponse(
        request,
        "venta.html",
        {"venta": venta, "cajero": cajero, "active_nav": "venta"},
    )


def _venta_activa(session: Session, turno: Turno):
    return ventas.get_or_create_venta(session, turno.id, turno.cajero_id)


@router.post("/scan", response_class=HTMLResponse)
def scan(
    request: Request,
    codigo: str = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    try:
        res = ventas.agregar_por_codigo(session, venta, codigo)
        aviso = res.aviso
    except ventas.ProductoNoEncontrado:
        aviso = f"Código «{codigo.strip()}» no encontrado."  # AT-2.2
    session.commit()
    return _main(request, venta, aviso)


@router.get("/buscar", response_class=HTMLResponse)
def buscar(
    request: Request,
    codigo: str = "",
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    """Desplegable de coincidencias por nombre/SKU/código (pre-query, sin agregar)."""
    productos = ventas.buscar_productos(session, codigo)
    return templates.TemplateResponse(
        request,
        "partials/_venta_sugerencias.html",
        {"productos": productos, "q": (codigo or "").strip()},
    )


@router.post("/agregar", response_class=HTMLResponse)
def agregar(
    request: Request,
    producto_id: int = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    """Agrega el producto elegido del desplegable de coincidencias."""
    _, turno = ctx
    venta = _venta_activa(session, turno)
    try:
        res = ventas.agregar_por_id(session, venta, producto_id)
        aviso = res.aviso
    except ventas.ProductoNoEncontrado:
        aviso = "El producto ya no está disponible."
    session.commit()
    return _main(request, venta, aviso)


@router.post("/especial", response_class=HTMLResponse)
def especial(
    request: Request,
    referencia: str = Form(""),
    descripcion: str = Form(""),
    precio: str = Form("0"),
    divisa: str = Form("MXN"),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),  # admin y cajero
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    aviso = None
    try:
        ventas.agregar_especial(
            session, venta, referencia, descripcion, _dec(precio), divisa
        )
    except ValueError as exc:
        aviso = str(exc)
    session.commit()
    return _main(request, venta, aviso)


@router.post("/linea/{linea_id}/divisa", response_class=HTMLResponse)
def cambiar_divisa(
    linea_id: int,
    request: Request,
    divisa: str = Form("MXN"),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),  # admin y cajero
):
    """Solo cambia la divisa de visualización del precio (no edita el precio)."""
    _, turno = ctx
    linea = _linea_de_turno(session, linea_id, turno)
    venta = _venta_activa(session, turno)
    aviso = None
    if linea is not None:
        try:
            ventas.set_divisa(session, linea, divisa)
        except ValueError as exc:
            aviso = str(exc)
    session.commit()
    return _main(request, venta, aviso)


@router.post("/linea/{linea_id}/precio-especial", response_class=HTMLResponse)
def precio_especial(
    linea_id: int,
    request: Request,
    divisa: str = Form("MXN"),
    monto: str = Form("0"),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),  # admin y cajero
):
    """Edita el precio de una línea de producto especial (única excepción)."""
    _, turno = ctx
    linea = _linea_de_turno(session, linea_id, turno)
    venta = _venta_activa(session, turno)
    aviso = None
    if linea is not None:
        try:
            ventas.set_precio_especial(session, linea, divisa, _dec(monto))
        except ValueError as exc:
            aviso = str(exc)
    session.commit()
    return _main(request, venta, aviso)


def _linea_de_turno(session: Session, linea_id: int, turno: Turno) -> VentaLinea | None:
    linea = session.get(VentaLinea, linea_id)
    if linea is None:
        return None
    venta = linea.venta
    if venta.turno_id != turno.id or venta.estado != "abierta":
        return None
    return linea


@router.post("/linea/{linea_id}/cantidad", response_class=HTMLResponse)
def cantidad(
    linea_id: int,
    request: Request,
    cantidad: str = Form(...),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    linea = _linea_de_turno(session, linea_id, turno)
    venta = _venta_activa(session, turno)
    if linea is not None:
        ventas.set_cantidad(session, linea, _dec(cantidad))
    session.commit()
    return _main(request, venta)


@router.post("/linea/{linea_id}/quitar", response_class=HTMLResponse)
def quitar(
    linea_id: int,
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    linea = _linea_de_turno(session, linea_id, turno)
    venta = _venta_activa(session, turno)
    if linea is not None:
        ventas.quitar_linea(session, linea)
    session.commit()
    return _main(request, venta)


@router.post("/linea/{linea_id}/descuento", response_class=HTMLResponse)
def descuento_linea(
    linea_id: int,
    request: Request,
    monto: str = Form("0"),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    linea = _linea_de_turno(session, linea_id, turno)
    venta = _venta_activa(session, turno)
    if linea is not None:
        ventas.aplicar_descuento_linea(session, linea, _dec(monto))
    session.commit()
    return _main(request, venta)


@router.post("/descuento", response_class=HTMLResponse)
def descuento_global(
    request: Request,
    monto: str = Form("0"),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    ventas.aplicar_descuento_global(session, venta, _dec(monto))
    session.commit()
    return _main(request, venta)


@router.post("/cancelar")
def cancelar(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    _, turno = ctx
    venta = _venta_activa(session, turno)
    ventas.cancelar(session, venta)
    session.commit()
    # HTMX: recargar la pantalla de venta (nueva venta vacía).
    return Response(status_code=204, headers={"HX-Redirect": "/venta"})
