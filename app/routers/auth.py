"""Autenticación de cajeros y apertura/reanudación/cierre de turno (AT-1.x).

Flujo: /login (usuario + PIN) → /turno (abrir o reanudar) → /venta.
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.deps import require_cajero, templates
from app.models import Cajero
from app.services import security, turnos

router = APIRouter(tags=["auth"])
log = logging.getLogger("pos.auth")


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"error": None})


def _login_error(request: Request, mensaje: str, status: int) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "login.html", {"error": mensaje}, status_code=status
    )


@router.post("/login")
def login_submit(
    request: Request,
    usuario: str = Form(...),
    pin: str = Form(...),
    session: Session = Depends(get_session),
):
    usuario = usuario.strip()
    settings = get_settings()

    # Anti fuerza bruta: si el usuario está bloqueado, no se evalúa el PIN.
    restante = security.login_segundos_bloqueo(usuario)
    if restante > 0:
        log.warning("login bloqueado usuario=%s (%ss restantes)", usuario, restante)
        return _login_error(
            request,
            f"Demasiados intentos. Espera {restante} s e inténtalo de nuevo.",
            429,
        )

    cajero = turnos.authenticate(session, usuario, pin)
    if cajero is None:
        # PIN/usuario inválido o cajero inactivo (AT-1.2, AT-1.4). No se crea turno.
        security.registrar_login_fallido(
            usuario,
            max_intentos=settings.login_max_intentos,
            bloqueo_seg=settings.login_bloqueo_seg,
        )
        log.warning("login fallido usuario=%s", usuario)
        return _login_error(request, "Usuario o PIN incorrecto.", 401)

    security.registrar_login_exitoso(usuario)
    log.info("login ok usuario=%s id=%s", usuario, cajero.id)
    request.session["cajero_id"] = cajero.id
    request.session.pop("turno_id", None)
    return RedirectResponse("/turno", status_code=303)


@router.get("/turno", response_class=HTMLResponse)
def turno_panel(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
) -> HTMLResponse:
    """Ofrece reanudar el turno abierto o abrir uno nuevo (AT-1.3)."""
    abierto = turnos.open_turno_for(session, cajero.id)
    return templates.TemplateResponse(
        request,
        "turno.html",
        {"cajero": cajero, "turno_abierto": abierto},
    )


@router.post("/turno/abrir")
def turno_abrir(
    request: Request,
    fondo_inicial: str = Form("0"),
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
):
    try:
        fondo = Decimal(fondo_inicial or "0")
    except InvalidOperation:
        fondo = Decimal("0")
    turno = turnos.abrir_turno(session, cajero.id, fondo)
    session.commit()
    request.session["turno_id"] = turno.id
    return RedirectResponse("/venta", status_code=303)


@router.post("/turno/reanudar")
def turno_reanudar(
    request: Request,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
):
    abierto = turnos.open_turno_for(session, cajero.id)
    if abierto is None:
        return RedirectResponse("/turno", status_code=303)
    request.session["turno_id"] = abierto.id
    return RedirectResponse("/venta", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
