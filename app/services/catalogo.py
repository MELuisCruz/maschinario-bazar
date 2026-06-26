"""Catálogo e inventario: alta/edición, import CSV y ajuste de stock (AT-6.x).

El stock se mueve siempre por la bitácora `movimientos_stock` (fuente de
verdad). Import CSV: upsert por `codigo_barras`; filas inválidas se reportan
por fila y NO bloquean a las válidas (regla elegida v1).
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Producto
from app.services import stock


class CodigoDuplicado(Exception):
    """Ya existe un producto con ese código de barras o SKU (AT-6.1)."""


# Valores "placeholder" que la gente escribe en lugar de dejar la celda vacía.
# Para codigo_barras/sku se tratan como SIN valor: si se tomaran literales, todas
# las filas con "N/A" compartirían clave y el upsert las colapsaría en un solo
# producto (bug: solo se cargaba 1 fila de todo el CSV).
_PLACEHOLDERS_VACIO = {"n/a", "na", "n.a.", "-", "--", "none", "null", "s/n", "sin"}


def _clave_opcional(valor: str | None) -> str | None:
    """Normaliza una clave opcional (codigo_barras/sku): placeholders → None."""
    v = (valor or "").strip()
    return None if v.lower() in _PLACEHOLDERS_VACIO else (v or None)


@dataclass
class ImportResult:
    creados: int = 0
    actualizados: int = 0
    errores: list[tuple[int, str]] = field(default_factory=list)


def _buscar_por_clave(
    session: Session, codigo_barras: str | None, sku: str | None
) -> Producto | None:
    """Producto (activo o eliminado) que ya use ese código de barras o SKU."""
    cond = []
    if codigo_barras:
        cond.append(Producto.codigo_barras == codigo_barras)
    if sku:
        cond.append(Producto.sku == sku)
    if not cond:
        return None
    return session.scalar(select(Producto).where(or_(*cond)))


def crear_producto(
    session: Session,
    *,
    nombre: str,
    precio: Decimal,
    codigo_barras: str | None = None,
    sku: str | None = None,
    iva_tasa: Decimal = Decimal("0.160"),
    existencia_inicial: Decimal = Decimal("0"),
    controla_stock: bool = True,
    cajero_id: int | None = None,
) -> Producto:
    existente = _buscar_por_clave(session, codigo_barras, sku)
    if existente is not None:
        if existente.activo:
            raise CodigoDuplicado(codigo_barras or sku)  # AT-6.1: duplicado real
        # Re-alta de un producto eliminado (lógico): se REUTILIZA el registro
        # para conservar su historial (ventas y movimientos lo referencian por
        # FK). Antes esto fallaba como "ya existe" aunque estuviera oculto.
        existente.activo = True
        existente.nombre = nombre
        existente.precio = Decimal(precio)
        existente.iva_tasa = Decimal(iva_tasa)
        existente.controla_stock = controla_stock
        if codigo_barras:
            existente.codigo_barras = codigo_barras
        if sku:
            existente.sku = sku
        session.flush()
        # Deja la existencia en la cantidad indicada al re-darlo de alta.
        ajustar_stock(session, existente, Decimal(existencia_inicial), cajero_id)
        return existente
    p = Producto(
        nombre=nombre,
        precio=Decimal(precio),
        codigo_barras=codigo_barras or None,
        sku=sku or None,
        iva_tasa=Decimal(iva_tasa),
        existencia=Decimal("0"),
        controla_stock=controla_stock,
        activo=True,
    )
    session.add(p)
    session.flush()
    if Decimal(existencia_inicial) != 0:
        stock.registrar_movimiento(
            session,
            p,
            "alta",
            Decimal(existencia_inicial),
            referencia="alta",
            cajero_id=cajero_id,
        )
    return p


def editar_producto(
    session: Session,
    producto: Producto,
    *,
    nombre: str,
    precio: Decimal,
    iva_tasa: Decimal = Decimal("0.160"),
    controla_stock: bool = True,
    codigo_barras: str | None = None,
    sku: str | None = None,
) -> Producto:
    """Edita los datos de un producto (NO su existencia; eso es de Inventario).

    Permite cambiar SKU/código de barras, validando que el nuevo valor no esté
    en uso por OTRO producto (la unicidad cubre activos e inactivos)."""
    codigo_barras = codigo_barras or None
    sku = sku or None
    for col, valor in (("codigo_barras", codigo_barras), ("sku", sku)):
        if valor is not None:
            otro = session.scalar(
                select(Producto.id).where(
                    getattr(Producto, col) == valor, Producto.id != producto.id
                )
            )
            if otro is not None:
                raise CodigoDuplicado(valor)
    producto.nombre = nombre
    producto.precio = Decimal(precio)
    producto.iva_tasa = Decimal(iva_tasa)
    producto.controla_stock = controla_stock
    producto.codigo_barras = codigo_barras
    producto.sku = sku
    session.flush()
    return producto


def ajustar_stock(
    session: Session,
    producto: Producto,
    nueva_existencia: Decimal,
    cajero_id: int | None = None,
) -> None:
    """Ajuste manual: registra el delta como movimiento 'ajuste'."""
    delta = Decimal(nueva_existencia) - Decimal(producto.existencia)
    if delta != 0:
        stock.registrar_movimiento(
            session, producto, "ajuste", delta, referencia="ajuste", cajero_id=cajero_id
        )


def reabastecer(
    session: Session,
    producto: Producto,
    cantidad: Decimal,
    cajero_id: int | None = None,
) -> None:
    """Suma `cantidad` (positiva) a la existencia vía movimiento 'ajuste'."""
    cantidad = Decimal(cantidad)
    if cantidad <= 0:
        raise ValueError("La cantidad a reabastecer debe ser mayor a 0.")
    stock.registrar_movimiento(
        session,
        producto,
        "ajuste",
        cantidad,
        referencia="reabasto",
        cajero_id=cajero_id,
    )


def desactivar(session: Session, producto: Producto) -> None:
    """Eliminación lógica: el producto deja de venderse y de listarse.

    No se borra físicamente para preservar el historial (ventas y movimientos
    referencian el producto por FK). El lookup de venta ya filtra activo=True.
    """
    producto.activo = False
    session.flush()


def importar_csv(
    session: Session, contenido: str, cajero_id: int | None = None
) -> ImportResult:
    """Importa/actualiza productos desde CSV. Encabezados:
    codigo_barras,nombre,precio[,iva_tasa,existencia,controla_stock,sku]."""
    res = ImportResult()
    reader = csv.DictReader(io.StringIO(contenido))
    # Fila 1 = encabezados; los datos empiezan en la fila 2.
    for i, row in enumerate(reader, start=2):
        try:
            nombre = (row.get("nombre") or "").strip()
            codigo = _clave_opcional(row.get("codigo_barras"))
            if not nombre:
                raise ValueError("nombre vacío")
            try:
                precio = Decimal((row.get("precio") or "").strip())
            except InvalidOperation:
                raise ValueError("precio inválido")
            if precio < 0:
                raise ValueError("precio negativo")
            iva = Decimal((row.get("iva_tasa") or "0.160").strip() or "0.160")
            # Existencia OPCIONAL: si la columna falta/está vacía, los items
            # nuevos arrancan en 1 y los existentes NO cambian su stock.
            existencia_raw = (row.get("existencia") or "").strip()
            if existencia_raw:
                try:
                    existencia = Decimal(existencia_raw)
                except InvalidOperation:
                    raise ValueError("existencia inválida")
                if existencia < 0:
                    raise ValueError("existencia negativa")
            else:
                existencia = None  # se decide según alta/actualización
            controla = (row.get("controla_stock") or "true").strip().lower() not in (
                "false",
                "0",
                "no",
            )
            sku = _clave_opcional(row.get("sku"))

            # Upsert por código de barras O por SKU (soporta items solo-SKU).
            existente = None
            if codigo:
                existente = session.scalar(
                    select(Producto).where(Producto.codigo_barras == codigo)
                )
            if existente is None and sku:
                existente = session.scalar(select(Producto).where(Producto.sku == sku))
            if existente is None:
                crear_producto(
                    session,
                    nombre=nombre,
                    precio=precio,
                    codigo_barras=codigo,
                    sku=sku,
                    iva_tasa=iva,
                    # Default 1 para items nuevos sin cantidad en el CSV.
                    existencia_inicial=(
                        existencia if existencia is not None else Decimal("1")
                    ),
                    controla_stock=controla,
                    cajero_id=cajero_id,
                )
                res.creados += 1
            else:
                existente.activo = True  # re-importar reactiva un eliminado
                existente.nombre = nombre
                existente.precio = precio
                existente.iva_tasa = iva
                existente.controla_stock = controla
                if sku:
                    existente.sku = sku
                if codigo and not existente.codigo_barras:
                    existente.codigo_barras = codigo
                # Ajuste de existencia solo si el CSV trae la cantidad.
                if existencia is not None:
                    delta = existencia - Decimal(existente.existencia)
                    if delta != 0:
                        stock.registrar_movimiento(
                            session,
                            existente,
                            "import",
                            delta,
                            referencia="import",
                            cajero_id=cajero_id,
                        )
                res.actualizados += 1
        except Exception as exc:  # fila inválida: reporta y continúa
            res.errores.append((i, str(exc)))
    session.flush()
    return res
