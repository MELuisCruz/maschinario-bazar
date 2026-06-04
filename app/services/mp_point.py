"""Cliente de Mercado Pago — API de Orders para Point (INTEGRATION_MP_POINT.md).

Cubre crear / consultar / cancelar / reembolsar order. El efectivo NO pasa por
aquí. Invariante: el estado terminal de aprobación se determina por la respuesta
de MP (GET), nunca se asume (AT-4.4).

Los literales exactos del enum de estados de la order son `SUPUESTO` (se fijan al
implementar contra la doc vigente); aquí se mapea por **comportamiento**.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import httpx

from app.services.money import q2

API_BASE = "https://api.mercadopago.com"


class MPError(Exception):
    """Error genérico de la integración MP."""


class MPOffline(MPError):
    """Sin conexión: no se pudo alcanzar a MP (AT-4.7)."""


class MPUnauthorized(MPError):
    """401: Access Token incorrecto."""


class MPConflictQueued(MPError):
    """409 already_queued_order_for_terminal: la terminal ya tiene una order."""


class MPIdempotencyReused(MPError):
    """409 idempotency_key_already_used: key reusada con cuerpo distinto."""


def new_idempotency_key() -> str:
    """Una llave nueva por **intento** de cobro (INTEGRATION §4)."""
    return str(uuid.uuid4())


def estado_desde_order(order: dict) -> str:
    """Mapea la order de MP a `pagos.estado` por comportamiento (INTEGRATION §5).

    aprobado/finalizado → 'aprobado'; rechazado → 'rechazado';
    cancelado/expirado → 'cancelado'; cualquier otro → 'pendiente'.
    """
    status = (order.get("status") or "").lower()
    pagos = (order.get("transactions") or {}).get("payments") or []
    pay_status = {(p.get("status") or "").lower() for p in pagos}

    if "approved" in pay_status or status in {
        "processed",
        "finished",
        "approved",
        "paid",
    }:
        return "aprobado"
    if "rejected" in pay_status or status in {"rejected", "failed"}:
        return "rechazado"
    if status in {"canceled", "cancelled", "expired"}:
        return "cancelado"
    return "pendiente"


def _extract_code(data: dict) -> str:
    if not isinstance(data, dict):
        return ""
    errors = data.get("errors")
    if isinstance(errors, list) and errors:
        return (errors[0] or {}).get("code", "") or ""
    return data.get("code") or data.get("error") or ""


class MPClient:
    """Cliente HTTP fino sobre la API de Orders."""

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = API_BASE,
        http: httpx.Client | None = None,
    ):
        self._token = access_token
        self._base = base_url.rstrip("/")
        self._http = http or httpx.Client(timeout=10.0)

    def _headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            h["X-Idempotency-Key"] = idempotency_key
        return h

    def _request(
        self, method: str, path: str, *, idempotency_key=None, json=None
    ) -> dict:
        try:
            resp = self._http.request(
                method,
                f"{self._base}{path}",
                headers=self._headers(idempotency_key),
                json=json,
            )
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
            raise MPOffline(str(exc)) from exc
        return self._handle(resp)

    @staticmethod
    def _handle(resp: httpx.Response) -> dict:
        if resp.status_code < 300:
            return resp.json() if resp.content else {}
        try:
            data = resp.json()
        except ValueError:
            data = {}
        code = _extract_code(data)
        if resp.status_code == 401:
            raise MPUnauthorized(code or "unauthorized")
        if resp.status_code == 409 and code == "already_queued_order_for_terminal":
            raise MPConflictQueued(code)
        if resp.status_code == 409 and code == "idempotency_key_already_used":
            raise MPIdempotencyReused(code)
        raise MPError(f"{resp.status_code} {code}".strip())

    # --- Operaciones (INTEGRATION §4–§7) ---

    def create_order(
        self,
        *,
        idempotency_key: str,
        external_reference: str,
        amount: Decimal,
        terminal_id: str,
        description: str | None = None,
    ) -> dict:
        body = {
            "type": "point",
            "external_reference": external_reference,
            "expiration_time": "PT5M",
            "transactions": {"payments": [{"amount": str(q2(amount))}]},
            "config": {
                "point": {"terminal_id": terminal_id, "print_on_terminal": "no_ticket"},
                "payment_method": {
                    "default_installments": 1,
                    "installments_cost": "seller",
                },
            },
            "description": description or f"Venta {external_reference}",
        }
        return self._request(
            "POST", "/v1/orders", idempotency_key=idempotency_key, json=body
        )

    def get_order(self, order_id: str) -> dict:
        return self._request("GET", f"/v1/orders/{order_id}")

    def cancel_order(self, order_id: str) -> dict:
        return self._request("POST", f"/v1/orders/{order_id}/cancel")

    def refund_order(self, order_id: str) -> dict:
        return self._request("POST", f"/v1/orders/{order_id}/refund")
