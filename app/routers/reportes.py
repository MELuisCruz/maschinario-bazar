"""Reportes y export fiscal (PRD §3.6, §3.7, AT-8.x)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.db import get_session
from app.deps import require_admin, require_cajero, templates
from app.models import Cajero
from app.services import configuracion as cfg_svc
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


def _resolver_rango(
    session: Session, periodo: str, desde: str | None, hasta: str | None
) -> tuple[datetime, datetime]:
    """Rango por fechas locales (calendario) si vienen ambas; si no, el preset.

    Las fechas (YYYY-MM-DD) se interpretan en la zona local configurada y se
    convierten a UTC; `hasta` es inclusivo (cubre todo ese día).
    """
    if desde and hasta:
        try:
            tz_offset = cfg_svc.ticket_kwargs(session)["tz_offset"]
            tz = timezone(timedelta(hours=tz_offset))
            d = datetime.strptime(desde, "%Y-%m-%d").replace(tzinfo=tz)
            h = datetime.strptime(hasta, "%Y-%m-%d").replace(tzinfo=tz) + timedelta(
                days=1
            )
            return d.astimezone(timezone.utc), h.astimezone(timezone.utc)
        except ValueError:
            pass  # fechas inválidas → cae al preset
    return _rango(periodo)


@router.get("", response_class=HTMLResponse)
def reportes_home(
    request: Request,
    periodo: str = "hoy",
    desde: str | None = None,
    hasta: str | None = None,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_cajero),
):
    rango = _resolver_rango(session, periodo, desde, hasta)
    rep = reportes.generar(session, rango[0], rango[1])
    return templates.TemplateResponse(
        request,
        "reportes.html",
        {
            "cajero": cajero,
            "rep": rep,
            "periodo": periodo,
            "desde": desde or "",
            "hasta": hasta or "",
            "active_nav": "reportes",
        },
    )


@router.get("/export")
def export(
    periodo: str = "mes",
    desde: str | None = None,
    hasta: str | None = None,
    session: Session = Depends(get_session),
    cajero: Cajero = Depends(require_admin),
):
    """Export fiscal del periodo; marca las ventas (AT-8.2). Solo admin. La app NO timbra."""
    rango = _resolver_rango(session, periodo, desde, hasta)
    exp = fiscal_export.generar_export(session, rango[0], rango[1])
    session.commit()
    csv_text = fiscal_export.a_csv(exp)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="export_fiscal_{periodo}.csv"'
        },
    )
