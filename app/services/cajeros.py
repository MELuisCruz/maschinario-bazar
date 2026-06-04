"""Gestión de cajeros y permisos por rol (PRD §2: el rol determina permisos).

Solo el administrador puede crear cajeros y elevar/degradar roles. Se protege
contra dejar al sistema sin ningún administrador activo.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Cajero, RolCajero
from app.services.security import hash_pin


class UsuarioDuplicado(Exception):
    """Ya existe un cajero con ese `usuario`."""


class UltimoAdmin(Exception):
    """La operación dejaría al sistema sin ningún administrador activo."""


def es_admin(cajero: Cajero | None) -> bool:
    """True si el cajero tiene rol administrador (acepta enum o string)."""
    if cajero is None:
        return False
    rol = getattr(cajero.rol, "value", cajero.rol)
    return rol == "administrador"


def listar(session: Session) -> list[Cajero]:
    return list(session.scalars(select(Cajero).order_by(Cajero.usuario)).all())


def _admins_activos(session: Session, excluir_id: int | None = None) -> int:
    cond = [Cajero.rol == RolCajero.administrador, Cajero.activo.is_(True)]
    if excluir_id is not None:
        cond.append(Cajero.id != excluir_id)
    return session.scalar(select(func.count()).select_from(Cajero).where(*cond)) or 0


def crear_cajero(
    session: Session,
    *,
    usuario: str,
    nombre: str,
    pin: str,
    rol: str = "cajero",
) -> Cajero:
    usuario = usuario.strip()
    if session.scalar(select(Cajero).where(Cajero.usuario == usuario)):
        raise UsuarioDuplicado(usuario)
    cajero = Cajero(
        usuario=usuario,
        nombre=nombre.strip(),
        pin_hash=hash_pin(pin),
        rol=RolCajero(rol),
        activo=True,
    )
    session.add(cajero)
    session.flush()
    return cajero


def cambiar_rol(session: Session, cajero: Cajero, nuevo_rol: str) -> None:
    """Eleva (cajero→administrador) o degrada (administrador→cajero) el rol."""
    nuevo = RolCajero(nuevo_rol)
    # Degradar al último admin activo dejaría al sistema sin administrador.
    if es_admin(cajero) and nuevo != RolCajero.administrador:
        if _admins_activos(session, excluir_id=cajero.id) == 0:
            raise UltimoAdmin()
    cajero.rol = nuevo
    session.flush()


def set_activo(session: Session, cajero: Cajero, activo: bool) -> None:
    if (
        not activo
        and es_admin(cajero)
        and _admins_activos(session, excluir_id=cajero.id) == 0
    ):
        raise UltimoAdmin()
    cajero.activo = activo
    session.flush()
