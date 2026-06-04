"""Cobro con tarjeta — API de Orders (ACCEPTANCE_TESTS §4, AT-4.1..AT-4.7).

Integración MP contra **mocks / simulate** (nunca cobros reales), §11.
"""

from decimal import Decimal

import httpx
import pytest

from app.services import cobro, ventas
from app.services.mp_point import (
    MPClient,
    MPConflictQueued,
    MPIdempotencyReused,
    MPOffline,
    estado_desde_order,
)

D = Decimal


class FakeMP:
    """Cliente MP simulado: registra llamadas y devuelve orders programadas."""

    def __init__(self, on_create=None, order_status="created", pay_status=None):
        self.created = []
        self.canceled = []
        self.refunded = []
        self._on_create = on_create  # callable(attempt) -> raise / None
        self._order_status = order_status
        self._pay_status = pay_status
        self._attempt = 0

    def create_order(
        self,
        *,
        idempotency_key,
        external_reference,
        amount,
        terminal_id,
        description=None,
    ):
        self._attempt += 1
        if self._on_create:
            self._on_create(self._attempt)
        oid = f"ORD{self._attempt:03d}"
        self.created.append(
            {"key": idempotency_key, "ref": external_reference, "id": oid}
        )
        return {"id": oid, "status": "created"}

    def get_order(self, order_id):
        payments = (
            [{"id": "PAY1", "status": self._pay_status}] if self._pay_status else []
        )
        return {
            "id": order_id,
            "status": self._order_status,
            "transactions": {"payments": payments},
        }

    def cancel_order(self, order_id):
        self.canceled.append(order_id)
        return {"id": order_id, "status": "canceled"}

    def refund_order(self, order_id):
        self.refunded.append(order_id)
        return {"id": order_id, "status": "refunded"}


def _venta_tarjeta(db, turno, make_producto, precio="116.00"):
    make_producto(codigo="T", precio=precio, existencia="10")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "T")
    db.commit()
    return v


# --- Mapeo de estado (puro) ---


def test_estado_mapping():
    assert (
        estado_desde_order({"transactions": {"payments": [{"status": "approved"}]}})
        == "aprobado"
    )
    assert (
        estado_desde_order({"transactions": {"payments": [{"status": "rejected"}]}})
        == "rechazado"
    )
    assert estado_desde_order({"status": "expired"}) == "cancelado"
    assert estado_desde_order({"status": "created"}) == "pendiente"


# --- Orquestación ---


def test_at_4_1_iniciar_crea_order_y_pago_pendiente(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)
    fake = FakeMP()
    pago = cobro.iniciar_tarjeta(db, v, fake, "TERM01")
    db.commit()
    assert pago.estado == "pendiente"
    assert pago.mp_order_id == "ORD001"
    assert pago.mp_idempotency  # key única persistida
    assert fake.created[0]["ref"] == v.folio  # external_reference = folio


def test_at_4_2_aprobado_marca_venta_pagada(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)
    fake = FakeMP(pay_status="approved")
    pago = cobro.iniciar_tarjeta(db, v, fake, "TERM01")
    estado = cobro.conciliar_tarjeta(db, pago, fake)
    db.commit()
    assert estado == "aprobado"
    assert v.estado == "pagada"


def test_at_4_3_rechazado_no_paga(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)
    fake = FakeMP(pay_status="rejected")
    pago = cobro.iniciar_tarjeta(db, v, fake, "TERM01")
    estado = cobro.conciliar_tarjeta(db, pago, fake)
    db.commit()
    assert estado == "rechazado"
    assert v.estado == "abierta"


def test_at_4_4_ambiguo_permanece_pendiente(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)
    fake = FakeMP(order_status="created")  # sin pago aún
    pago = cobro.iniciar_tarjeta(db, v, fake, "TERM01")
    estado = cobro.conciliar_tarjeta(db, pago, fake)
    db.commit()
    assert estado == "pendiente"
    assert v.estado == "abierta"  # nunca aprobado sin confirmación


def test_at_4_5_already_queued_cancela_previa_y_reintenta(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)
    # Pago previo pendiente con order en espera.
    previo = cobro.iniciar_tarjeta(db, v, FakeMP(), "TERM01")
    db.commit()

    def primer_intento_409(attempt):
        if attempt == 1:
            raise MPConflictQueued("already_queued_order_for_terminal")

    fake = FakeMP(on_create=primer_intento_409)
    pago = cobro.iniciar_tarjeta(db, v, fake, "TERM01")
    db.commit()
    assert previo.mp_order_id in fake.canceled  # canceló la previa
    assert pago.estado == "pendiente" and pago.mp_order_id == "ORD002"


def test_at_4_6_idempotency_reusada_genera_key_nueva(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)

    def primer_intento_409(attempt):
        if attempt == 1:
            raise MPIdempotencyReused("idempotency_key_already_used")

    fake = FakeMP(on_create=primer_intento_409)
    pago = cobro.iniciar_tarjeta(db, v, fake, "TERM01")
    db.commit()
    # Reintentó con éxito (segunda key) y persistió un pago pendiente.
    assert pago.estado == "pendiente"
    assert len(fake.created) == 1  # solo el intento exitoso quedó registrado


def test_at_4_7_offline_bloquea(db, turno, make_producto):
    v = _venta_tarjeta(db, turno, make_producto)

    class Offline(FakeMP):
        def create_order(self, **kw):
            raise MPOffline("sin red")

    with pytest.raises(MPOffline):
        cobro.iniciar_tarjeta(db, v, Offline(), "TERM01")


# --- Cliente HTTP real contra transporte simulado ---


def test_client_create_order_ok():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Idempotency-Key"]
        assert request.headers["Authorization"] == "Bearer tok"
        return httpx.Response(201, json={"id": "ORD9", "status": "created"})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    c = MPClient("tok", base_url="https://mp.test", http=http)
    order = c.create_order(
        idempotency_key="k1",
        external_reference="V-1",
        amount=D("116.00"),
        terminal_id="T",
    )
    assert order["id"] == "ORD9"


def test_client_409_already_queued_mapea_excepcion():
    def handler(request):
        return httpx.Response(
            409, json={"errors": [{"code": "already_queued_order_for_terminal"}]}
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    c = MPClient("tok", base_url="https://mp.test", http=http)
    with pytest.raises(MPConflictQueued):
        c.create_order(
            idempotency_key="k",
            external_reference="V-1",
            amount=D("1.00"),
            terminal_id="T",
        )


def test_client_offline_connecterror():
    def handler(request):
        raise httpx.ConnectError("no route")

    http = httpx.Client(transport=httpx.MockTransport(handler))
    c = MPClient("tok", base_url="https://mp.test", http=http)
    with pytest.raises(MPOffline):
        c.get_order("ORD1")


def test_http_offline_no_rompe_efectivo(op_client, make_producto, monkeypatch):
    # AT-4.7 vía HTTP: con el cliente offline, tarjeta se bloquea y efectivo sigue.
    from app.main import app
    from app.deps import get_mp_client

    class Offline:
        def create_order(self, **kw):
            raise MPOffline("sin red")

    app.dependency_overrides[get_mp_client] = lambda: Offline()
    make_producto(codigo="OFF", precio="20.00", existencia="3")
    op_client.post("/venta/scan", data={"codigo": "OFF"})
    r = op_client.post("/cobro/tarjeta/iniciar")
    assert "Sin conexión" in r.text  # bloqueo con aviso
    # Efectivo sigue disponible:
    ok = op_client.post("/cobro/efectivo", data={"recibido": "20"})
    assert ok.status_code == 200 and "cobrada" in ok.text.lower()
    app.dependency_overrides.pop(get_mp_client, None)
