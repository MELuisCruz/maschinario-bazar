"""Tipos ENUM de PostgreSQL (DATA_MODEL.md §2).

Se definen como `enum.Enum` de Python con `values_callable` para que SQLAlchemy
persista el **valor** (p. ej. 'cajero'), no el nombre del miembro. El nombre del
tipo ENUM en Postgres se fija explícitamente para que coincida con el DDL.
"""

from __future__ import annotations

import enum

from sqlalchemy import Enum as SAEnum


class RolCajero(str, enum.Enum):
    cajero = "cajero"
    administrador = "administrador"


class EstadoVenta(str, enum.Enum):
    abierta = "abierta"
    pagada = "pagada"
    cancelada = "cancelada"
    devuelta_parcial = "devuelta_parcial"
    devuelta_total = "devuelta_total"


class MedioPago(str, enum.Enum):
    efectivo = "efectivo"
    tarjeta_point = "tarjeta_point"


class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    aprobado = "aprobado"
    rechazado = "rechazado"
    cancelado = "cancelado"


class TipoMovimiento(str, enum.Enum):
    venta = "venta"
    devolucion = "devolucion"
    ajuste = "ajuste"
    import_ = "import"  # 'import' es palabra reservada; el valor SQL es "import"
    alta = "alta"


# --- Etiquetas legibles para mostrar en UI/ticket (no usar el .value crudo) ---
ESTADO_VENTA_LABEL = {
    "abierta": "Abierta",
    "pagada": "Pagada",
    "cancelada": "Cancelada",
    "devuelta_parcial": "Devuelta parcial",
    "devuelta_total": "Devuelta total",
}
MEDIO_PAGO_LABEL = {
    "efectivo": "Efectivo",
    "tarjeta_point": "Tarjeta (Point)",
}


def _valor(v) -> str:
    """Valor string de un enum o de un string (tolerante a ambos)."""
    return getattr(v, "value", v) if v is not None else ""


def etiqueta_estado(v) -> str:
    s = _valor(v)
    return ESTADO_VENTA_LABEL.get(s, s)


def etiqueta_medio(v) -> str:
    s = _valor(v)
    return MEDIO_PAGO_LABEL.get(s, s)


def _pg_enum(py_enum: type[enum.Enum], name: str) -> SAEnum:
    """ENUM nativo de Postgres que persiste el valor del miembro."""
    return SAEnum(
        py_enum,
        name=name,
        values_callable=lambda e: [m.value for m in e],
        native_enum=True,
    )


rol_cajero_enum = _pg_enum(RolCajero, "rol_cajero")
estado_venta_enum = _pg_enum(EstadoVenta, "estado_venta")
medio_pago_enum = _pg_enum(MedioPago, "medio_pago")
estado_pago_enum = _pg_enum(EstadoPago, "estado_pago")
tipo_movimiento_enum = _pg_enum(TipoMovimiento, "tipo_movimiento")
