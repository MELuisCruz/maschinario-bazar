"""Lógica de venta: líneas, descuentos y totales (PRD §3.1, AT-2.x).

Modelo de IVA = incluido (ver `money`). El stock NO se descuenta aquí; eso
ocurre al confirmar el cobro (AT-6.3). Una venta abierta cancelada no afecta
stock ni caja (AT-2.7).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Producto, Venta, VentaLinea
from app.services.money import LineaCalc, compute_totales, line_importe


class ProductoNoEncontrado(Exception):
    """El código escaneado no existe en el catálogo (AT-2.2)."""


@dataclass
class AltaResultado:
    linea: VentaLinea
    aviso: str | None = None  # p. ej. stock 0 (AT-2.6), no bloquea


def nuevo_folio(venta_id: int) -> str:
    """Folio legible/imprimible y válido como external_reference de MP (≤64, [-_])."""
    return f"V-{venta_id:06d}"


def get_or_create_venta(session: Session, turno_id: int, cajero_id: int) -> Venta:
    """Venta abierta del turno (o crea una nueva con folio)."""
    venta = session.scalar(
        select(Venta).where(Venta.turno_id == turno_id, Venta.estado == "abierta")
    )
    if venta is not None:
        return venta
    venta = Venta(turno_id=turno_id, cajero_id=cajero_id, folio="")
    session.add(venta)
    session.flush()  # obtiene id
    venta.folio = nuevo_folio(venta.id)
    session.flush()
    return venta


def _buscar_producto(session: Session, codigo: str) -> Producto | None:
    codigo = (codigo or "").strip()
    if not codigo:
        return None
    return session.scalar(
        select(Producto).where(
            (Producto.codigo_barras == codigo) | (Producto.sku == codigo),
            Producto.activo.is_(True),
        )
    )


def agregar_por_codigo(session: Session, venta: Venta, codigo: str) -> AltaResultado:
    """Agrega producto por código; incrementa cantidad si ya existe (AT-2.3)."""
    producto = _buscar_producto(session, codigo)
    if producto is None:
        raise ProductoNoEncontrado(codigo)

    linea = next((ln for ln in venta.lineas if ln.producto_id == producto.id), None)
    if linea is None:
        linea = VentaLinea(
            venta_id=venta.id,
            producto_id=producto.id,
            descripcion=producto.nombre,  # snapshot (invariante DATA_MODEL §3)
            cantidad=Decimal("1"),
            precio_unit=producto.precio,  # snapshot
            iva_tasa=producto.iva_tasa,  # snapshot
            descuento=Decimal("0"),
            importe=line_importe(Decimal("1"), producto.precio),
        )
        venta.lineas.append(linea)
    else:
        linea.cantidad = linea.cantidad + Decimal("1")  # AT-2.3

    session.flush()
    recompute(session, venta)

    aviso = None
    if producto.controla_stock and producto.existencia <= 0:
        aviso = f"«{producto.nombre}» sin existencia."  # AT-2.6, no bloquea
    return AltaResultado(linea=linea, aviso=aviso)


def set_cantidad(session: Session, linea: VentaLinea, cantidad: Decimal) -> None:
    venta = session.get(Venta, linea.venta_id)
    cantidad = Decimal(cantidad)
    if cantidad <= 0:
        venta.lineas.remove(linea)  # cantidad 0 = quitar línea
    else:
        linea.cantidad = cantidad
    session.flush()
    recompute(session, venta)


def quitar_linea(session: Session, linea: VentaLinea) -> Venta:
    venta = session.get(Venta, linea.venta_id)
    venta.lineas.remove(linea)
    session.flush()
    recompute(session, venta)
    return venta


def aplicar_descuento_linea(
    session: Session, linea: VentaLinea, monto: Decimal
) -> None:
    linea.descuento = max(Decimal("0"), Decimal(monto))
    session.flush()
    recompute(session, linea.venta)


def aplicar_descuento_global(session: Session, venta: Venta, monto: Decimal) -> None:
    venta.descuento_global = max(Decimal("0"), Decimal(monto))
    recompute(session, venta)


def recompute(session: Session, venta: Venta) -> None:
    """Recalcula importes de línea y totales de la venta (IVA incluido)."""
    for ln in venta.lineas:
        ln.importe = line_importe(ln.cantidad, ln.precio_unit, ln.descuento)
    totales = compute_totales(
        [LineaCalc(ln.cantidad, ln.precio_unit, ln.descuento) for ln in venta.lineas],
        venta.descuento_global,
    )
    venta.subtotal = totales.subtotal
    venta.iva_total = totales.iva_total
    venta.total = totales.total
    venta.descuento_total = totales.descuento_total
    session.flush()


def cancelar(session: Session, venta: Venta) -> None:
    """Cancela una venta abierta (AT-2.7): no toca stock ni caja."""
    venta.estado = "cancelada"
    session.flush()
