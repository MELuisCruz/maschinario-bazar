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


@dataclass
class ImportResult:
    creados: int = 0
    actualizados: int = 0
    errores: list[tuple[int, str]] = field(default_factory=list)


def _existe(
    session: Session,
    codigo_barras: str | None,
    sku: str | None,
    excluir_id: int | None = None,
) -> bool:
    cond = []
    if codigo_barras:
        cond.append(Producto.codigo_barras == codigo_barras)
    if sku:
        cond.append(Producto.sku == sku)
    if not cond:
        return False
    q = select(Producto.id).where(or_(*cond))
    if excluir_id is not None:
        q = q.where(Producto.id != excluir_id)
    return session.scalar(q) is not None


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
    if _existe(session, codigo_barras, sku):
        raise CodigoDuplicado(codigo_barras or sku)
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
            codigo = (row.get("codigo_barras") or "").strip() or None
            if not nombre:
                raise ValueError("nombre vacío")
            try:
                precio = Decimal((row.get("precio") or "").strip())
            except InvalidOperation:
                raise ValueError("precio inválido")
            if precio < 0:
                raise ValueError("precio negativo")
            iva = Decimal((row.get("iva_tasa") or "0.160").strip() or "0.160")
            existencia = Decimal((row.get("existencia") or "0").strip() or "0")
            controla = (row.get("controla_stock") or "true").strip().lower() not in (
                "false",
                "0",
                "no",
            )
            sku = (row.get("sku") or "").strip() or None

            existente = None
            if codigo:
                existente = session.scalar(
                    select(Producto).where(Producto.codigo_barras == codigo)
                )
            if existente is None:
                crear_producto(
                    session,
                    nombre=nombre,
                    precio=precio,
                    codigo_barras=codigo,
                    sku=sku,
                    iva_tasa=iva,
                    existencia_inicial=existencia,
                    controla_stock=controla,
                    cajero_id=cajero_id,
                )
                res.creados += 1
            else:
                existente.nombre = nombre
                existente.precio = precio
                existente.iva_tasa = iva
                existente.controla_stock = controla
                if sku:
                    existente.sku = sku
                # Ajuste de existencia vía bitácora (movimiento 'import').
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
