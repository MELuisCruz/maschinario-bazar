"""Cálculo monetario centralizado (CLAUDE.md §6, ACCEPTANCE_TESTS AT-2.4/2.5).

Política única: redondeo **HALF_UP a 2 decimales**.

Modelo de IVA = **incluido** (decisión del titular 2026-06-03): el `precio`
capturado del producto YA incluye el IVA 16% (precio al público). Por tanto:
    total    = Σ(precio·cantidad) − descuentos          (bruto, lo que se cobra)
    subtotal = total / (1 + tasa)                        (base neta de IVA)
    iva      = total − subtotal
Se honra la identidad `subtotal + iva = total` del desglose (AT-2.4).

SUPUESTO: IVA incluido y descuento en monto fijo. Si el titular cambia a IVA
por fuera o descuento %, solo se ajusta este módulo.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
IVA_RATE_DEFAULT = Decimal("0.16")


def q2(value: Decimal | int | float | str) -> Decimal:
    """Cuantiza a 2 decimales con HALF_UP (política monetaria del proyecto)."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def line_importe(
    cantidad: Decimal, precio_unit: Decimal, descuento: Decimal = Decimal("0")
) -> Decimal:
    """Importe de una línea: (cantidad·precio) − descuento de línea, ≥ 0."""
    bruto = q2(Decimal(cantidad) * Decimal(precio_unit))
    importe = bruto - q2(descuento)
    return importe if importe > 0 else Decimal("0.00")


@dataclass(frozen=True)
class TotalesVenta:
    """Resultado del cálculo de una venta (todos en MXN, 2 decimales)."""

    subtotal: Decimal  # base neta de IVA (= total / 1.16)
    descuento_total: Decimal  # suma de descuentos por línea + global (bruto)
    iva_total: Decimal  # IVA contenido en el total
    total: Decimal  # bruto a cobrar (IVA incluido)


@dataclass(frozen=True)
class LineaCalc:
    """Entrada mínima de una línea para el cálculo de totales."""

    cantidad: Decimal
    precio_unit: Decimal
    descuento: Decimal = Decimal("0")


def compute_totales(
    lineas: list[LineaCalc],
    descuento_global: Decimal = Decimal("0"),
    iva_rate: Decimal = IVA_RATE_DEFAULT,
) -> TotalesVenta:
    """Calcula los totales de la venta en el modelo de IVA incluido.

    `descuento_global` se topa a la suma de importes (no deja total negativo).
    """
    suma_importes = sum(
        (line_importe(ln.cantidad, ln.precio_unit, ln.descuento) for ln in lineas),
        Decimal("0.00"),
    )
    descuento_lineas = sum((q2(ln.descuento) for ln in lineas), Decimal("0.00"))

    desc_global = q2(descuento_global)
    if desc_global > suma_importes:
        desc_global = suma_importes  # tope: nunca total negativo

    total = q2(suma_importes - desc_global)
    subtotal = q2(total / (Decimal("1") + iva_rate))
    iva_total = q2(total - subtotal)
    descuento_total = q2(descuento_lineas + desc_global)

    return TotalesVenta(
        subtotal=subtotal,
        descuento_total=descuento_total,
        iva_total=iva_total,
        total=total,
    )


def cambio_efectivo(total: Decimal, recibido: Decimal) -> Decimal:
    """Cambio = recibido − total (AT-3.1). Asume recibido ≥ total ya validado."""
    return q2(Decimal(recibido) - Decimal(total))
