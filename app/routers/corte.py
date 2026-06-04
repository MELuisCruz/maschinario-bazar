"""Corte de caja / turno: arqueo y totales por medio (PRD §3.2, AT-7.x)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_turno, templates
from app.models import Cajero, Turno
from app.services import corte as corte_svc

router = APIRouter(prefix="/corte", tags=["corte"])


@router.get("", response_class=HTMLResponse)
def corte_home(
    request: Request,
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    cajero, turno = ctx
    res = corte_svc.resumen(session, turno)
    abiertas = corte_svc.ventas_abiertas(session, turno.id)
    return templates.TemplateResponse(
        request,
        "corte.html",
        {
            "cajero": cajero,
            "turno": turno,
            "res": res,
            "abiertas": abiertas,
            "active_nav": "corte",
            "error": None,
        },
    )


@router.post("/cerrar", response_class=HTMLResponse)
def cerrar(
    request: Request,
    efectivo_contado: str = Form("0"),
    notas: str = Form(""),
    session: Session = Depends(get_session),
    ctx: tuple[Cajero, Turno] = Depends(require_turno),
):
    cajero, turno = ctx
    try:
        contado = Decimal((efectivo_contado or "0").strip())
    except InvalidOperation:
        contado = Decimal("0")
    try:
        res, dif = corte_svc.cerrar_turno(session, turno, contado, notas or None)
    except corte_svc.VentasAbiertas:
        session.rollback()
        res = corte_svc.resumen(session, turno)
        return templates.TemplateResponse(
            request,
            "corte.html",
            {
                "cajero": cajero,
                "turno": turno,
                "res": res,
                "abiertas": corte_svc.ventas_abiertas(session, turno.id),
                "active_nav": "corte",
                "error": "Hay ventas abiertas; resuélvelas antes de cerrar.",
            },
            status_code=400,
        )
    session.commit()
    request.session.pop("turno_id", None)  # turno cerrado: fuera de sesión
    return templates.TemplateResponse(
        request,
        "corte_ok.html",
        {"cajero": cajero, "turno": turno, "res": res, "dif": dif},
    )
