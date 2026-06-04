"""Control de stock básico (PRD §3.4, DATA_MODEL.md §3, AT-6.3/6.4).

La bitácora `movimientos_stock` es la fuente de verdad; `productos.existencia`
se mantiene consistente con la suma de movimientos. Productos con
`controla_stock=False` no descuentan ni reintegran.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import MovimientoStock, Producto, Venta


def registrar_movimiento(
    session: Session,
    producto: Producto,
    tipo: str,
    cantidad: Decimal,
    referencia: str | None = None,
    cajero_id: int | None = None,
) -> MovimientoStock:
    """Registra un movimiento (cantidad con signo) y ajusta la existencia."""
    mov = MovimientoStock(
        producto_id=producto.id,
        tipo=tipo,
        cantidad=Decimal(cantidad),
        referencia=referencia,
        cajero_id=cajero_id,
    )
    session.add(mov)
    producto.existencia = producto.existencia + Decimal(cantidad)
    session.flush()
    return mov


def descontar_venta(session: Session, venta: Venta) -> None:
    """Descuenta el stock de las líneas de una venta (AT-6.3).

    Productos con `controla_stock=False` no descuentan (AT-6.4).
    """
    for linea in venta.lineas:
        producto = session.get(Producto, linea.producto_id)
        if producto is None or not producto.controla_stock:
            continue
        registrar_movimiento(
            session,
            producto,
            tipo="venta",
            cantidad=-Decimal(linea.cantidad),
            referencia=venta.folio,
            cajero_id=venta.cajero_id,
        )


def reintegrar(
    session: Session,
    producto: Producto,
    cantidad: Decimal,
    referencia: str | None,
    cajero_id: int | None,
) -> None:
    """Reintegra existencia (devolución, AT-5.4). No-op si no controla stock."""
    if not producto.controla_stock:
        return
    registrar_movimiento(
        session,
        producto,
        tipo="devolucion",
        cantidad=Decimal(cantidad),
        referencia=referencia,
        cajero_id=cajero_id,
    )
