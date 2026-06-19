"""Dependencias compartidas: plantillas, sesión y guardas de acceso.

La sesión (cookie firmada, SessionMiddleware) guarda `cajero_id` y `turno_id`.
Las guardas levantan excepciones que `main.py` traduce a redirecciones.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.models import Cajero, Turno
from app.models.enums import etiqueta_estado, etiqueta_medio
from app.services.cajeros import es_admin
from app.services.mp_point import MPClient

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Variables/funciones disponibles en todas las plantillas.
templates.env.globals["business_name"] = get_settings().app_business_name
templates.env.globals["es_admin"] = es_admin
templates.env.globals["etiqueta_estado"] = etiqueta_estado
templates.env.globals["etiqueta_medio"] = etiqueta_medio


def get_mp_client() -> MPClient:
    """Cliente de Mercado Pago Point construido desde la config."""
    s = get_settings()
    return MPClient(s.mp_access_token)


class NotAuthenticated(Exception):
    """No hay cajero en sesión → redirigir a /login."""


class NotAuthorized(Exception):
    """Cajero autenticado pero sin permiso (rol insuficiente) → 403."""


class NoOpenTurno(Exception):
    """Hay cajero pero no turno abierto → redirigir a /turno."""


def current_cajero(
    request: Request, session: Session = Depends(get_session)
) -> Cajero | None:
    """Cajero de la sesión, o None."""
    cajero_id = request.session.get("cajero_id")
    if not cajero_id:
        return None
    return session.get(Cajero, cajero_id)


def require_cajero(request: Request, session: Session = Depends(get_session)) -> Cajero:
    """Exige cajero autenticado."""
    cajero = current_cajero(request, session)
    if cajero is None:
        raise NotAuthenticated()
    return cajero


def require_turno(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
) -> tuple[Cajero, Turno]:
    """Exige cajero autenticado **y** turno abierto en sesión."""
    turno_id = request.session.get("turno_id")
    turno = session.get(Turno, turno_id) if turno_id else None
    if turno is None or turno.cerrado_en is not None:
        raise NoOpenTurno()
    return cajero, turno


def require_admin(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
) -> Cajero:
    """Exige cajero autenticado con rol administrador (PRD §2)."""
    if not es_admin(cajero):
        raise NotAuthorized()
    return cajero
