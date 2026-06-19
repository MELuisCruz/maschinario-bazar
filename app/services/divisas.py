"""Conversión de divisas por línea (MXN base).

Decisiones (titular 18-jun-2026): el tipo de cambio es **manual** (lo fija el
admin en Configuración) y la API pública solo lo **sugiere/actualiza**. El total
de la venta SIEMPRE se concilia en MXN. Monedas soportadas: MXN, USD, EUR.

Los tipos de cambio se guardan como filas de la tabla `configuracion`
(`fx_usd_mxn`, `fx_eur_mxn` = MXN por 1 unidad de la divisa).
"""

from __future__ import annotations

from decimal import Decimal

import httpx
from sqlalchemy.orm import Session

from app.models import Configuracion

MONEDAS = ("MXN", "USD", "EUR")
_API_URL = "https://open.er-api.com/v6/latest/USD"  # gratis, sin API key

_FX_KEYS = {"USD": "fx_usd_mxn", "EUR": "fx_eur_mxn"}


class TipoCambioNoConfigurado(Exception):
    """No hay tipo de cambio válido para la divisa solicitada."""


def _get(session: Session, clave: str) -> str | None:
    row = session.get(Configuracion, clave)
    return row.valor if row else None


def _set(session: Session, clave: str, valor: str) -> None:
    row = session.get(Configuracion, clave)
    if row is None:
        session.add(Configuracion(clave=clave, valor=valor))
    else:
        row.valor = valor


def get_rates(session: Session) -> dict[str, Decimal]:
    """MXN por unidad de cada divisa. MXN=1; USD/EUR de la config (0 si no fijado)."""
    rates: dict[str, Decimal] = {"MXN": Decimal("1")}
    for divisa, clave in _FX_KEYS.items():
        try:
            rates[divisa] = Decimal(_get(session, clave) or "0")
        except Exception:
            rates[divisa] = Decimal("0")
    return rates


def set_rates(session: Session, usd_mxn: Decimal, eur_mxn: Decimal) -> None:
    _set(session, "fx_usd_mxn", str(Decimal(usd_mxn)))
    _set(session, "fx_eur_mxn", str(Decimal(eur_mxn)))


def fecha_actualizacion(session: Session) -> str:
    return _get(session, "fx_actualizado") or ""


def fetch_api_rates() -> dict[str, Decimal]:
    """Consulta la API pública y devuelve MXN por USD y por EUR (sugerencia)."""
    r = httpx.get(_API_URL, timeout=12)
    r.raise_for_status()
    data = r.json()
    if data.get("result") != "success":
        raise RuntimeError("La API de tipo de cambio no respondió 'success'.")
    rates = data["rates"]
    usd_mxn = Decimal(str(rates["MXN"]))
    eur_mxn = usd_mxn / Decimal(str(rates["EUR"]))  # MXN por EUR vía base USD
    return {
        "USD": usd_mxn.quantize(Decimal("0.0001")),
        "EUR": eur_mxn.quantize(Decimal("0.0001")),
        "fecha": data.get("time_last_update_utc", ""),
    }


def actualizar_desde_api(session: Session) -> dict[str, Decimal]:
    """Trae los tipos de cambio de la API y los guarda (los deja editables)."""
    api = fetch_api_rates()
    set_rates(session, api["USD"], api["EUR"])
    _set(session, "fx_actualizado", str(api.get("fecha", "")))
    return api


def _rate(session: Session, divisa: str) -> Decimal:
    divisa = (divisa or "MXN").upper()
    if divisa not in MONEDAS:
        raise TipoCambioNoConfigurado(f"Divisa no soportada: {divisa}")
    rate = get_rates(session)[divisa]
    if rate <= 0:
        raise TipoCambioNoConfigurado(
            f"Define el tipo de cambio {divisa}→MXN en Configuración."
        )
    return rate


def convertir(session: Session, monto: Decimal, divisa: str) -> tuple[Decimal, Decimal]:
    """Monto EN divisa → (mxn, tipo_cambio). Para precios capturados en divisa
    (producto especial). MXN → (monto, 1)."""
    if (divisa or "MXN").upper() == "MXN":
        return Decimal(monto), Decimal("1")
    rate = _rate(session, divisa)
    return (Decimal(monto) * rate).quantize(Decimal("0.01")), rate


def a_divisa(session: Session, mxn: Decimal, divisa: str) -> tuple[Decimal, Decimal]:
    """Monto en MXN → (monto en divisa, tipo_cambio). Para MOSTRAR un precio MXN
    fijo en otra divisa (catálogo). MXN → (monto, 1)."""
    if (divisa or "MXN").upper() == "MXN":
        return Decimal(mxn), Decimal("1")
    rate = _rate(session, divisa)
    return (Decimal(mxn) / rate).quantize(Decimal("0.01")), rate
