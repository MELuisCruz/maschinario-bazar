"""Export para timbrado externo — la app NO timbra (ADR-004, AT-8.2).

Entrega las ventas del periodo (público en general) con folio, fecha, subtotal,
IVA 16% desglosado, total y medio, para la factura global a RFC genérico
XAXX010101000. Marca `exportada_fiscal=True`. El timbrado ocurre fuera.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Pago, Venta

RFC_GENERICO = "XAXX010101000"

_VENDIDAS = ("pagada", "devuelta_parcial", "devuelta_total")
CAMPOS = ["folio", "fecha", "subtotal", "iva", "total", "medio", "rfc"]


@dataclass
class ExportFiscal:
    rfc_destino: str = RFC_GENERICO
    filas: list[dict] = field(default_factory=list)
    marcadas: int = 0


def _medios_de_venta(session: Session, venta_id: int) -> str:
    medios = session.scalars(
        select(Pago.medio)
        .where(Pago.venta_id == venta_id, Pago.estado == "aprobado")
        .distinct()
    ).all()
    return "+".join(sorted(medios)) or "—"


def generar_export(session: Session, desde: datetime, hasta: datetime) -> ExportFiscal:
    """Construye el export del periodo y marca las ventas como exportadas."""
    ventas = session.scalars(
        select(Venta).where(
            Venta.estado.in_(_VENDIDAS),
            Venta.creado_en >= desde,
            Venta.creado_en < hasta,
        )
    ).all()

    exp = ExportFiscal()
    for v in ventas:
        exp.filas.append(
            {
                "folio": v.folio,
                "fecha": (v.cerrado_en or v.creado_en).strftime("%Y-%m-%d %H:%M"),
                "subtotal": f"{Decimal(v.subtotal):.2f}",
                "iva": f"{Decimal(v.iva_total):.2f}",
                "total": f"{Decimal(v.total):.2f}",
                "medio": _medios_de_venta(session, v.id),
                "rfc": RFC_GENERICO,  # factura global a público en general
            }
        )
        v.exportada_fiscal = True  # AT-8.2
        exp.marcadas += 1
    session.flush()
    return exp


def a_csv(exp: ExportFiscal) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CAMPOS)
    writer.writeheader()
    writer.writerows(exp.filas)
    return buf.getvalue()
