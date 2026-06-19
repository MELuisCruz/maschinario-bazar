"""Modelos ORM (SQLAlchemy) del POS — DATA_MODEL.md.

Reexporta `Base` (con todo el metadata cargado por los imports de abajo) para
que Alembic descubra las tablas al autogenerar migraciones. Importar este
paquete registra todas las entidades en `Base.metadata`.
"""

from app.db import Base
from app.models.cajero import Cajero
from app.models.configuracion import Configuracion
from app.models.devolucion import Devolucion, DevolucionLinea
from app.models.enums import (
    EstadoPago,
    EstadoVenta,
    MedioPago,
    RolCajero,
    TipoMovimiento,
)
from app.models.movimiento_stock import MovimientoStock
from app.models.pago import Pago
from app.models.producto import Producto
from app.models.turno import Turno
from app.models.venta import Venta, VentaLinea

__all__ = [
    "Base",
    "Cajero",
    "Configuracion",
    "Turno",
    "Producto",
    "Venta",
    "VentaLinea",
    "Pago",
    "Devolucion",
    "DevolucionLinea",
    "MovimientoStock",
    "RolCajero",
    "EstadoVenta",
    "MedioPago",
    "EstadoPago",
    "TipoMovimiento",
]
