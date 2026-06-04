"""Autenticación de cajeros y ciclo de vida del turno (PRD §3.8, AT-1.x).

Reglas:
- Solo cajeros `activo=True` con PIN correcto autentican (AT-1.2, AT-1.4).
- Un cajero con turno abierto **reanuda**, no abre otro (AT-1.3).
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cajero, Turno
from app.services.security import verify_pin


def authenticate(session: Session, usuario: str, pin: str) -> Cajero | None:
    """Devuelve el cajero si existe, está activo y el PIN es correcto."""
    cajero = session.scalar(select(Cajero).where(Cajero.usuario == usuario))
    if cajero is None or not cajero.activo:
        return None
    if not verify_pin(pin, cajero.pin_hash):
        return None
    return cajero


def open_turno_for(session: Session, cajero_id: int) -> Turno | None:
    """Turno abierto (cerrado_en IS NULL) del cajero, si existe."""
    return session.scalar(
        select(Turno).where(Turno.cajero_id == cajero_id, Turno.cerrado_en.is_(None))
    )


def abrir_turno(session: Session, cajero_id: int, fondo_inicial: Decimal) -> Turno:
    """Abre un turno; si ya hay uno abierto lo reanuda en vez de duplicar (AT-1.3)."""
    existente = open_turno_for(session, cajero_id)
    if existente is not None:
        return existente
    turno = Turno(cajero_id=cajero_id, fondo_inicial=Decimal(fondo_inicial))
    session.add(turno)
    session.flush()
    return turno
