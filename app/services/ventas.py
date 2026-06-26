"""Lógica de venta: líneas, descuentos y totales (PRD §3.1, AT-2.x).

Modelo de IVA = incluido (ver `money`). El stock NO se descuenta aquí; eso
ocurre al confirmar el cobro (AT-6.3). Una venta abierta cancelada no afecta
stock ni caja (AT-2.7).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Producto, Venta, VentaLinea
from app.services import divisas
from app.services.money import LineaCalc, compute_totales, line_importe


class ProductoNoEncontrado(Exception):
    """El código escaneado no existe en el catálogo (AT-2.2)."""


@dataclass
class AltaResultado:
    linea: VentaLinea | None
    aviso: str | None = None  # mensaje (p. ej. bloqueo por falta de existencia)
    bloqueado: bool = False  # True si NO se agregó por falta de stock


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


def buscar_productos(session: Session, q: str, limit: int = 8) -> list[Producto]:
    """Coincidencias por nombre, SKU o código de barras (para el desplegable de
    venta). Búsqueda parcial, insensible a mayúsculas; solo productos activos."""
    q = (q or "").strip()
    if len(q) < 2:
        return []
    # Escapa comodines LIKE para que el texto del usuario sea literal.
    seguro = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    patron = f"%{seguro}%"
    return list(
        session.scalars(
            select(Producto)
            .where(
                Producto.activo.is_(True),
                or_(
                    Producto.nombre.ilike(patron, escape="\\"),
                    Producto.sku.ilike(patron, escape="\\"),
                    Producto.codigo_barras.ilike(patron, escape="\\"),
                ),
            )
            .order_by(Producto.nombre)
            .limit(limit)
        )
    )


def agregar_por_codigo(session: Session, venta: Venta, codigo: str) -> AltaResultado:
    """Agrega producto por código; incrementa cantidad si ya existe (AT-2.3)."""
    producto = _buscar_producto(session, codigo)
    if producto is None:
        raise ProductoNoEncontrado(codigo)
    return _agregar_producto(session, venta, producto)


def agregar_por_id(session: Session, venta: Venta, producto_id: int) -> AltaResultado:
    """Agrega un producto elegido del desplegable de coincidencias (por nombre)."""
    producto = session.scalar(
        select(Producto).where(
            Producto.id == producto_id, Producto.activo.is_(True)
        )
    )
    if producto is None:
        raise ProductoNoEncontrado(str(producto_id))
    return _agregar_producto(session, venta, producto)


def _agregar_producto(
    session: Session, venta: Venta, producto: Producto
) -> AltaResultado:
    """Núcleo de alta: suma 1 unidad (o incrementa) respetando el stock."""
    linea = next((ln for ln in venta.lineas if ln.producto_id == producto.id), None)
    actual = Decimal(linea.cantidad) if linea is not None else Decimal("0")

    # Bloqueo de sobreventa: no se permite agregar más unidades que la existencia
    # disponible (decisión del titular 18-jun-2026: bloquear, no solo avisar).
    # Los productos con controla_stock=False no tienen tope.
    if producto.controla_stock and actual + 1 > Decimal(producto.existencia):
        disp = max(Decimal("0"), Decimal(producto.existencia))
        if disp <= 0:
            aviso = f"«{producto.nombre}» agotado: no se agregó."
        else:
            aviso = (
                f"«{producto.nombre}»: solo quedan {disp:g} "
                f"(ya hay {actual:g} en la venta)."
            )
        return AltaResultado(linea=linea, aviso=aviso, bloqueado=True)

    if linea is None:
        linea = VentaLinea(
            venta_id=venta.id,
            producto_id=producto.id,
            descripcion=producto.nombre,  # snapshot (invariante DATA_MODEL §3)
            cantidad=Decimal("1"),
            precio_unit=producto.precio,  # snapshot (MXN)
            divisa="MXN",
            iva_tasa=producto.iva_tasa,  # snapshot
            descuento=Decimal("0"),
            importe=line_importe(Decimal("1"), producto.precio),
        )
        venta.lineas.append(linea)
    else:
        linea.cantidad = linea.cantidad + Decimal("1")  # AT-2.3

    session.flush()
    recompute(session, venta)
    return AltaResultado(linea=linea, aviso=None)


# SKU reservado del producto singleton "Producto especial" (oculto: activo=False).
ESPECIAL_SKU = "__ESPECIAL__"
REF_MAX = 50
NOTAS_MAX = 100


def get_or_create_especial(session: Session) -> Producto:
    """Producto singleton para ventas especiales (precio ad-hoc en caja).

    Oculto del catálogo (`activo=False`) y sin control de stock. Se busca por
    SKU reservado ignorando `activo`; las líneas snapshotean su propio precio.
    """
    p = session.scalar(select(Producto).where(Producto.sku == ESPECIAL_SKU))
    if p is None:
        p = Producto(
            sku=ESPECIAL_SKU,
            nombre="Producto especial",
            precio=Decimal("0"),
            iva_tasa=Decimal("0.160"),
            existencia=Decimal("0"),
            controla_stock=False,
            activo=False,  # no aparece en catálogo ni en la hoja imprimible
        )
        session.add(p)
        session.flush()
    return p


def agregar_especial(
    session: Session,
    venta: Venta,
    referencia: str,
    descripcion: str,
    precio: Decimal,
    divisa: str = "MXN",
) -> VentaLinea:
    """Agrega una línea de producto especial (precio ad-hoc, IVA 16% incluido).

    `referencia` (≤50) sale en el ticket como «Producto especial: ref»;
    `descripcion` (≤100) son notas internas de trazabilidad (no se imprimen).
    `precio` se captura en `divisa` (MXN/USD/EUR) y se convierte a MXN. Siempre
    crea una línea nueva (cada especial es distinto). No toca stock.
    """
    referencia = (referencia or "").strip()[:REF_MAX]
    descripcion = (descripcion or "").strip()[:NOTAS_MAX]
    precio = Decimal(precio)
    if not referencia:
        raise ValueError("La referencia del producto especial es obligatoria.")
    if precio <= 0:
        raise ValueError("El precio del producto especial debe ser mayor a 0.")
    try:
        mxn, tc = divisas.convertir(session, precio, divisa)
    except divisas.TipoCambioNoConfigurado as exc:
        raise ValueError(str(exc)) from exc
    es_mxn = (divisa or "MXN").upper() == "MXN"
    esp = get_or_create_especial(session)
    linea = VentaLinea(
        venta_id=venta.id,
        producto_id=esp.id,
        descripcion=f"Producto especial: {referencia}",
        notas=descripcion or None,
        cantidad=Decimal("1"),
        precio_unit=mxn,
        divisa=(divisa or "MXN").upper(),
        precio_divisa=None if es_mxn else precio,
        tipo_cambio=None if es_mxn else tc,
        iva_tasa=Decimal("0.160"),
        descuento=Decimal("0"),
        importe=line_importe(Decimal("1"), mxn),
    )
    venta.lineas.append(linea)
    session.flush()
    recompute(session, venta)
    return linea


def set_divisa(session: Session, linea: VentaLinea, divisa: str) -> None:
    """Cambia SOLO la divisa de visualización del precio unitario.

    El precio en MXN (precio_unit) y el importe NO cambian; se calcula el precio
    unitario equivalente en la divisa elegida para mostrarlo. Aplica a cualquier
    línea (regla: el precio no se edita; ver `set_precio_especial`).
    """
    divisa = (divisa or "MXN").upper()
    try:
        monto_div, tc = divisas.a_divisa(session, Decimal(linea.precio_unit), divisa)
    except divisas.TipoCambioNoConfigurado as exc:
        raise ValueError(str(exc)) from exc
    linea.divisa = divisa
    if divisa == "MXN":
        linea.precio_divisa = None
        linea.tipo_cambio = None
    else:
        linea.precio_divisa = monto_div
        linea.tipo_cambio = tc
    session.flush()
    recompute(session, linea.venta)  # importe sigue en MXN (precio_unit intacto)


def set_precio_especial(
    session: Session, linea: VentaLinea, divisa: str, monto: Decimal
) -> None:
    """Edita el precio de una línea de PRODUCTO ESPECIAL (única excepción).

    El monto se captura en `divisa` y se convierte a MXN (precio_unit). El total
    siempre queda en MXN. Rechaza líneas que no sean producto especial.
    """
    if not linea.es_especial:
        raise ValueError("Solo el producto especial permite editar el precio.")
    monto = Decimal(monto)
    if monto <= 0:
        raise ValueError("El precio debe ser mayor a 0.")
    divisa = (divisa or "MXN").upper()
    try:
        mxn, tc = divisas.convertir(session, monto, divisa)
    except divisas.TipoCambioNoConfigurado as exc:
        raise ValueError(str(exc)) from exc
    linea.precio_unit = mxn
    linea.divisa = divisa
    if divisa == "MXN":
        linea.precio_divisa = None
        linea.tipo_cambio = None
    else:
        linea.precio_divisa = monto
        linea.tipo_cambio = tc
    session.flush()
    recompute(session, linea.venta)


def set_cantidad(session: Session, linea: VentaLinea, cantidad: Decimal) -> None:
    venta = session.get(Venta, linea.venta_id)
    cantidad = Decimal(cantidad)
    if cantidad > 0:
        # Tope por existencia: no permitir fijar más unidades que el stock.
        producto = session.get(Producto, linea.producto_id)
        if producto is not None and producto.controla_stock:
            cantidad = min(cantidad, max(Decimal("0"), Decimal(producto.existencia)))
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
