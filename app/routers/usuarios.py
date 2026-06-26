"""Gestión de cajeros y roles — solo administrador (PRD §2).

Permite al admin dar de alta cajeros y elevar/degradar su rol. Protegido con
`require_admin`; no permite dejar al sistema sin administrador activo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, templates
from app.models import Cajero
from app.services import cajeros as cajeros_svc

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _render(
    request, session, admin, *, error=None, msg=None, status=200
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "usuarios.html",
        {
            "cajero": admin,
            "active_nav": "usuarios",
            "usuarios": cajeros_svc.listar(session),
            "error": error,
            "msg": msg,
        },
        status_code=status,
    )


@router.get("", response_class=HTMLResponse)
def usuarios_home(
    request: Request,
    session: Session = Depends(get_session),
    admin: Cajero = Depends(require_admin),
):
    return _render(request, session, admin)


@router.post("/alta", response_class=HTMLResponse)
def alta(
    request: Request,
    usuario: str = Form(...),
    nombre: str = Form(...),
    pin: str = Form(...),
    rol: str = Form("cajero"),
    session: Session = Depends(get_session),
    admin: Cajero = Depends(require_admin),
):
    try:
        cajeros_svc.crear_cajero(
            session,
            usuario=usuario,
            nombre=nombre,
            pin=pin,
            rol=rol if rol in ("cajero", "administrador") else "cajero",
        )
        session.commit()
        return _render(
            request, session, admin, msg=f"Cajero «{usuario.strip()}» creado."
        )
    except cajeros_svc.UsuarioDuplicado:
        session.rollback()
        return _render(
            request,
            session,
            admin,
            error="Ya existe un cajero con ese usuario.",
            status=400,
        )


@router.post("/{cajero_id}/rol", response_class=HTMLResponse)
def cambiar_rol(
    cajero_id: int,
    request: Request,
    rol: str = Form(...),
    session: Session = Depends(get_session),
    admin: Cajero = Depends(require_admin),
):
    objetivo = session.get(Cajero, cajero_id)
    if objetivo is None:
        return _render(
            request, session, admin, error="Cajero no encontrado.", status=404
        )
    try:
        cajeros_svc.cambiar_rol(session, objetivo, rol)
        session.commit()
        return _render(
            request,
            session,
            admin,
            msg=f"Rol de «{objetivo.usuario}» actualizado a {rol}.",
        )
    except cajeros_svc.UltimoAdmin:
        session.rollback()
        propio = objetivo.id == admin.id
        return _render(
            request,
            session,
            admin,
            error=(
                "No puedes quitarte tu propio rol: eres el único administrador."
                if propio
                else "No puedes degradar al único administrador activo."
            ),
            status=400,
        )
    except ValueError:
        session.rollback()
        return _render(request, session, admin, error="Rol inválido.", status=400)


@router.post("/{cajero_id}/activo", response_class=HTMLResponse)
def set_activo(
    cajero_id: int,
    request: Request,
    activo: str = Form("true"),
    session: Session = Depends(get_session),
    admin: Cajero = Depends(require_admin),
):
    objetivo = session.get(Cajero, cajero_id)
    if objetivo is None:
        return _render(
            request, session, admin, error="Cajero no encontrado.", status=404
        )
    quiere_activo = activo.lower() not in ("false", "0", "no")
    try:
        cajeros_svc.set_activo(session, objetivo, quiere_activo)
        session.commit()
        return _render(
            request,
            session,
            admin,
            msg=f"«{objetivo.usuario}» {'activado' if quiere_activo else 'desactivado'}.",
        )
    except cajeros_svc.UltimoAdmin:
        session.rollback()
        propio = objetivo.id == admin.id
        return _render(
            request,
            session,
            admin,
            error=(
                "No puedes desactivarte: eres el único administrador."
                if propio
                else "No puedes desactivar al único administrador activo."
            ),
            status=400,
        )
