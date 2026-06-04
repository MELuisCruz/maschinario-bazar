"""Reportes y export fiscal (PRD §3.6, §3.7, AT-8.x)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_cajero, templates
from app.models import Cajero
from app.services import fiscal_export, reportes

router = APIRouter(prefix="/reportes", tags=["reportes"])


def _rango(periodo: str) -> tuple[datetime, datetime]:
    ahora = datetime.now(timezone.utc)
    fin = ahora + timedelta(seconds=1)
    if periodo == "7dias":
        return ahora - timedelta(days=7), fin
    if periodo == "mes":
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return inicio_mes, fin
    # 'hoy' (default)
    inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    return inicio, fin


@router.get("", response_class=HTMLResponse)
def reportes_home(
    request: Request,
    periodo: str = "hoy",
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
):
    desde, hasta = _rango(periodo)
    rep = reportes.generar(session, desde, hasta)
    return templates.TemplateResponse(
        request,
        "reportes.html",
        {"cajero": cajero, "rep": rep, "periodo": periodo, "active_nav": "reportes"},
    )


@router.get("/export")
def export(
    periodo: str = "mes",
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
):
    """Genera el export fiscal del periodo y marca las ventas (AT-8.2). La app NO timbra."""
    desde, hasta = _rango(periodo)
    exp = fiscal_export.generar_export(session, desde, hasta)
    session.commit()
    csv_text = fiscal_export.a_csv(exp)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="export_fiscal_{periodo}.csv"'
        },
    )
