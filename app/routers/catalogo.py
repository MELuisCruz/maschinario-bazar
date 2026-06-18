"""Catálogo e inventario: alta/edición, import CSV, stock (PRD §3.4, AT-6.x).

Acceso: cajero autenticado. SUPUESTO: restringir a rol administrador es una
mejora pendiente (UI_SPEC §5.5 / permisos por rol a confirmar).
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, require_cajero, templates
from app.models import Cajero, Producto
from app.services import catalogo as cat
from app.services.barcodes import code128_data_uri

router = APIRouter(prefix="/catalogo", tags=["catalogo"])


def _dec(v: str, default="0") -> Decimal:
    try:
        return Decimal((v or default).strip() or default)
    except InvalidOperation:
        return Decimal(default)


def _listar(session: Session) -> list[Producto]:
    return list(
        session.scalars(select(Producto).order_by(Producto.nombre).limit(200)).all()
    )


@router.get("", response_class=HTMLResponse)
def catalogo_home(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
    msg: str | None = None,
):
    return templates.TemplateResponse(
        request,
        "catalogo.html",
        {
            "cajero": cajero,
            "productos": _listar(session),
            "active_nav": "catalogo",
            "error": None,
            "msg": msg,
        },
    )


@router.get("/imprimible", response_class=HTMLResponse)
def imprimible(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
):
    """Hoja imprimible (PDF vía navegador) con nombre + código de barras por
    producto, para escanear en caja. Codifica el SKU (o el código de barras si
    existe) como Code128. Productos activos con código, ordenados por nombre.
    """
    productos = session.scalars(
        select(Producto).where(Producto.activo.is_(True)).order_by(Producto.nombre)
    ).all()
    items = []
    sin_codigo = 0
    for p in productos:
        codigo = p.sku or p.codigo_barras
        if not codigo:
            sin_codigo += 1
            continue
        items.append(
            {"nombre": p.nombre, "codigo": codigo, "barcode": code128_data_uri(codigo)}
        )
    return templates.TemplateResponse(
        request,
        "catalogo_imprimible.html",
        {"items": items, "sin_codigo": sin_codigo, "total": len(items)},
    )


@router.post("/alta", response_class=HTMLResponse)
def alta(
    request: Request,
    nombre: str = Form(...),
    precio: str = Form(...),
    codigo_barras: str = Form(""),
    sku: str = Form(""),
    iva_tasa: str = Form("0.160"),
    existencia: str = Form("0"),
    controla_stock: str = Form("true"),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),  # solo admin actualiza el catálogo
):
    error = None
    msg = None
    try:
        cat.crear_producto(
            session,
            nombre=nombre.strip(),
            precio=_dec(precio),
            codigo_barras=codigo_barras.strip() or None,
            sku=sku.strip() or None,
            iva_tasa=_dec(iva_tasa, "0.160"),
            existencia_inicial=_dec(existencia),
            controla_stock=controla_stock.lower() not in ("false", "0", "no"),
            cajero_id=cajero.id,
        )
        session.commit()
        msg = f"Producto «{nombre.strip()}» creado."
    except cat.CodigoDuplicado:
        session.rollback()
        error = "Ya existe un producto con ese código de barras o SKU."  # AT-6.1
    return templates.TemplateResponse(
        request,
        "catalogo.html",
        {
            "cajero": cajero,
            "productos": _listar(session),
            "active_nav": "catalogo",
            "error": error,
            "msg": msg,
        },
        status_code=400 if error else 200,
    )


@router.post("/importar", response_class=HTMLResponse)
async def importar(
    request: Request,
    archivo: UploadFile = File(...),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),  # import masivo: solo admin (req. 3)
):
    contenido = (await archivo.read()).decode("utf-8-sig", errors="replace")
    res = cat.importar_csv(session, contenido, cajero_id=cajero.id)
    session.commit()
    return templates.TemplateResponse(
        request,
        "catalogo.html",
        {
            "cajero": cajero,
            "productos": _listar(session),
            "active_nav": "catalogo",
            "error": None,
            "msg": None,
            "import_res": res,
        },
    )
