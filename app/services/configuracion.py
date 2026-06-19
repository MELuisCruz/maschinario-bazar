"""Configuración editable de la app (clave-valor).

Centraliza los textos que el administrador puede cambiar desde la app (hoy: los
del ticket). Los valores por defecto viven aquí; la tabla solo guarda lo que el
admin haya modificado. `get_config` siempre devuelve todas las claves (mezcla
defaults + guardados), así las plantillas y el ticket nunca ven valores nulos.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Configuracion

# Claves del ticket que el admin puede editar y sus valores por defecto.
# `ticket_establecimiento` arranca del APP_BUSINESS_NAME para no romper lo previo.
TICKET_KEYS = (
    "ticket_establecimiento",
    "ticket_evento",
    "ticket_domicilio",
    "ticket_telefono",
    "ticket_pie",
    "ticket_fecha_formato",
    "ticket_tz_offset",
)

# Formato y zona horaria por defecto del timestamp del ticket.
FECHA_FORMATO_DEFAULT = "%d-%m-%Y %H:%M"
TZ_OFFSET_DEFAULT = -6  # UTC-6


def _defaults() -> dict[str, str]:
    return {
        "ticket_establecimiento": get_settings().app_business_name,
        "ticket_evento": "",
        "ticket_domicilio": "",
        "ticket_telefono": "",
        "ticket_pie": "¡Gracias por su compra!",
        "ticket_fecha_formato": FECHA_FORMATO_DEFAULT,
        "ticket_tz_offset": str(TZ_OFFSET_DEFAULT),
    }


def get_config(session: Session) -> dict[str, str]:
    """Todas las claves del ticket: defaults sobreescritos por lo guardado."""
    cfg = _defaults()
    guardados = session.scalars(
        select(Configuracion).where(Configuracion.clave.in_(TICKET_KEYS))
    ).all()
    for row in guardados:
        cfg[row.clave] = row.valor
    return cfg


def ticket_kwargs(session: Session) -> dict:
    """Config del ticket en los nombres de parámetro que espera `printing`."""
    c = get_config(session)
    try:
        tz_offset = int(c["ticket_tz_offset"])
    except (ValueError, TypeError):
        tz_offset = TZ_OFFSET_DEFAULT
    return {
        "business_name": c["ticket_establecimiento"],
        "evento": c["ticket_evento"],
        "domicilio": c["ticket_domicilio"],
        "telefono": c["ticket_telefono"],
        "pie": c["ticket_pie"],
        "fecha_formato": c["ticket_fecha_formato"] or FECHA_FORMATO_DEFAULT,
        "tz_offset": tz_offset,
    }


def set_config(session: Session, valores: dict[str, str]) -> None:
    """Upsert de las claves recibidas (solo las conocidas del ticket)."""
    for clave in TICKET_KEYS:
        if clave not in valores:
            continue
        valor = (valores[clave] or "").strip()
        row = session.get(Configuracion, clave)
        if row is None:
            session.add(Configuracion(clave=clave, valor=valor))
        else:
            row.valor = valor
