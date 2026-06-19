"""Gestión de credenciales de APIs externas desde Configuración (solo admin).

Hoy la única llave secreta es el Access Token de Mercado Pago. El token vive en
`.env` (gitignored); al rotarlo se valida contra la API antes de guardarlo y el
anterior queda obsoleto (la revocación efectiva del token viejo se hace en el
panel de desarrolladores de MP; aquí solo se reemplaza el que usa la app).
"""

from __future__ import annotations

import logging

import httpx

from app.config import get_settings, update_env_vars

log = logging.getLogger("pos.api_keys")

MP_LIST_URL = "https://api.mercadopago.com/terminals/v1/list"


def enmascarar(valor: str) -> str:
    """Oculta un secreto para mostrarlo sin revelarlo (p. ej. 'APP_US…2358')."""
    if not valor:
        return ""
    if len(valor) <= 10:
        return "•" * len(valor)
    return f"{valor[:6]}…{valor[-4:]}"


def _probar_mp(token: str) -> tuple[bool, str]:
    """Prueba un token de MP contra la API. Devuelve (ok, mensaje legible)."""
    try:
        r = httpx.get(
            MP_LIST_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
    except httpx.HTTPError as exc:
        log.warning("Prueba de token MP sin conexión: %s", exc)
        return False, "Sin conexión con Mercado Pago. Intenta más tarde."
    if r.status_code == 200:
        try:
            n = len((r.json().get("data") or {}).get("terminals") or [])
        except ValueError:
            n = 0
        return True, f"Token válido · terminales visibles: {n}."
    if r.status_code in (401, 403):
        return False, "Token inválido o sin permisos (401/403)."
    return False, f"Respuesta inesperada de Mercado Pago ({r.status_code})."


def estado_mp() -> dict:
    """Estado del token de MP actualmente configurado (para el testigo de la UI)."""
    token = get_settings().mp_access_token
    if not token:
        return {
            "configurada": False,
            "ok": False,
            "mensaje": "Sin token configurado.",
            "mascara": "",
        }
    ok, mensaje = _probar_mp(token)
    return {
        "configurada": True,
        "ok": ok,
        "mensaje": mensaje,
        "mascara": enmascarar(token),
    }


def actualizar_mp(token: str) -> tuple[bool, str]:
    """Valida y guarda un token nuevo de MP en .env. El anterior queda obsoleto."""
    token = (token or "").strip()
    if not token:
        return False, "El token no puede estar vacío."
    ok, mensaje = _probar_mp(token)
    if not ok:
        return False, f"No se guardó (la llave no funciona): {mensaje}"
    update_env_vars({"MP_ACCESS_TOKEN": token})
    log.info("MP_ACCESS_TOKEN rotado por admin (token nuevo validado contra MP).")
    return True, (
        "Token de Mercado Pago actualizado y validado. El anterior quedó obsoleto: "
        "revócalo en el panel de desarrolladores de MP para invalidarlo del todo."
    )
