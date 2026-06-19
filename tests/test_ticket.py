"""Ticket e impresión / reimpresión (ACCEPTANCE_TESTS §9, AT-9.1..AT-9.3).

AT-10.x (foco del scan-input y debounce anti-doble lectura) son de UI/JS y se
documentan como prueba manual (§11); la lógica vive en static/js/app.js.
"""

from datetime import datetime, timezone
from decimal import Decimal

from app.services import cobro, printing, ventas

D = Decimal


def _venta_pagada(db, turno, make_producto):
    make_producto(
        codigo="TK", nombre="Cuaderno profesional", precio="116.00", existencia="10"
    )
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "TK")
    db.commit()
    cobro.cobrar_efectivo(db, v, D("200.00"))
    db.commit()
    return v


class FakePrinter:
    """Impresora ESC/POS simulada: captura comandos (§11)."""

    def __init__(self):
        self.textos = []
        self.cortes = 0
        self.codepage = None

    def charcode(self, code):
        self.codepage = code

    def text(self, t):
        self.textos.append(t)

    def cut(self):
        self.cortes += 1

    def close(self):
        pass


def test_at_9_1_ticket_tiene_campos_y_leyenda(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto)
    txt = printing.construir_ticket_texto(
        v,
        cajero_nombre="Ana Cajera",
        business_name="Maschinario · Bazar",
        pagos=v.pagos,
    )
    assert v.folio in txt
    assert "Cuaderno profesional" in txt
    assert "Subtotal:" in txt
    assert "IVA (16%):" in txt
    assert "TOTAL:" in txt
    assert "Efectivo" in txt
    assert "NOTA DE COMPRA  (no es CFDI)" in txt  # nota de compra, no CFDI


def test_at_9_2_impresora_no_disponible_no_rompe(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto)

    def factory_falla(_settings):
        raise RuntimeError("USB no encontrada")

    res = printing.imprimir_ticket(
        v,
        cajero_nombre="Ana",
        business_name="X",
        pagos=v.pagos,
        printer_factory=factory_falla,
    )
    assert res.ok is False and res.error  # no lanza; la venta sigue intacta
    assert v.estado == "pagada"


def test_imprime_y_verifica_comandos(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto)
    fake = FakePrinter()
    res = printing.imprimir_ticket(
        v,
        cajero_nombre="Ana",
        business_name="X",
        pagos=v.pagos,
        printer_factory=lambda _s: fake,
    )
    assert res.ok is True
    assert fake.cortes == 1  # se emitió el corte (GS V)
    assert fake.codepage == "CP850"  # codepage fijo para acentos (ÁÉÍÓÚ)
    assert any("TOTAL:" in t for t in fake.textos)


def test_imprimir_texto_reintenta_y_se_recupera(monkeypatch):
    # Simula que el USB vuelve al 2º intento (hueco de re-enganche de usbipd).
    monkeypatch.setattr("app.services.printing.PRINT_ESPERA_S", 0)
    intentos = {"n": 0}

    def factory(_s):
        intentos["n"] += 1
        if intentos["n"] < 2:
            raise RuntimeError("USB device not found")
        return FakePrinter()

    res = printing.imprimir_texto("hola", printer_factory=factory)
    assert res.ok is True
    assert intentos["n"] == 2  # falló 1, reintentó y funcionó


def test_imprimir_texto_se_rinde_tras_intentos(monkeypatch):
    monkeypatch.setattr("app.services.printing.PRINT_ESPERA_S", 0)
    intentos = {"n": 0}

    def factory(_s):
        intentos["n"] += 1
        raise RuntimeError("USB device not found")

    res = printing.imprimir_texto("hola", printer_factory=factory)
    assert res.ok is False and "not found" in res.error
    assert intentos["n"] == printing.PRINT_INTENTOS  # agotó los reintentos


def test_at_9_3_reimpresion_identica_mas_leyenda(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto)
    base = printing.construir_ticket_texto(
        v, cajero_nombre="Ana", business_name="X", pagos=v.pagos
    )
    fecha = datetime(2026, 6, 4, 10, 30, tzinfo=timezone.utc)
    reimp = printing.construir_ticket_texto(
        v,
        cajero_nombre="Ana",
        business_name="X",
        pagos=v.pagos,
        reimpresion=True,
        fecha_reimpresion=fecha,
    )
    # Formato configurable por defecto: DD-MM-YYYY HH:mm en UTC-6 (10:30 UTC → 04:30).
    assert "*** REIMPRESIÓN 04-06-2026 04:30 UTC-6 ***" in reimp
    # Idéntico salvo la leyenda añadida al pie.
    assert reimp.startswith(base)
    # No altera datos de la venta.
    assert v.estado == "pagada" and v.total == D("116.00")


def _fake_pago(estado, medio="tarjeta_point", **kw):
    from types import SimpleNamespace

    return SimpleNamespace(
        estado=estado,
        medio=medio,
        monto=D("20.00"),
        recibido=kw.get("recibido"),
        cambio=kw.get("cambio"),
        mp_order_id=kw.get("order", "ORD0000QAX2A1RM"),
        mp_payment_type=kw.get("tipo"),
        mp_card_brand=kw.get("marca"),
        mp_card_last4=kw.get("last4"),
    )


def _fake_venta(pagos):
    from types import SimpleNamespace

    ln = SimpleNamespace(
        cantidad=D("1"),
        descripcion="Item",
        importe=D("20.00"),
        descuento=D("0"),
        divisa="MXN",
        precio_divisa=None,
        tipo_cambio=None,
        precio_unit=D("20.00"),
    )
    return SimpleNamespace(
        folio="V-000011",
        cerrado_en=datetime(2026, 6, 19, tzinfo=timezone.utc),
        creado_en=datetime(2026, 6, 19, tzinfo=timezone.utc),
        lineas=[ln],
        subtotal=D("17.24"),
        descuento_total=D("0"),
        iva_total=D("2.76"),
        total=D("20.00"),
        pagos=pagos,
    )


def test_ticket_solo_muestra_pagos_aprobados():
    # Una venta con tarjeta puede dejar varios intentos cancelados; el ticket
    # debe mostrar SOLO el aprobado (no 5 líneas "Pago: Tarjeta").
    pagos = [
        _fake_pago("cancelado", order="ORDc1S3MM8JFR"),
        _fake_pago("cancelado", order="ORDc2J751WSGX"),
        _fake_pago("aprobado", tipo="credit_card", marca="visa", last4="3610"),
    ]
    txt = printing.construir_ticket_texto(
        _fake_venta(pagos), cajero_nombre="Ana", business_name="X"
    )
    assert txt.count("Pago: Tarjeta") == 1
    assert "S3MM8JFR" not in txt and "J751WSGX" not in txt


def test_ticket_tarjeta_muestra_tipo_marca_y_ultimos4():
    pagos = [_fake_pago("aprobado", tipo="credit_card", marca="visa", last4="3610")]
    txt = printing.construir_ticket_texto(
        _fake_venta(pagos), cajero_nombre="Ana", business_name="X"
    )
    assert "Pago: Tarjeta crédito" in txt
    assert "VISA" in txt and "****3610" in txt


def test_ticket_rechazo_contenido():
    pago = _fake_pago("rechazado", tipo="debit_card", marca="visa", last4="3610")
    txt = printing.construir_ticket_rechazo(
        _fake_venta([pago]), cajero_nombre="Ana", business_name="X", pago=pago
    )
    assert "PAGO RECHAZADO" in txt
    assert "V-000011" in txt  # folio de la venta
    assert "Monto intentado:" in txt
    assert "No se realizó ningún cargo." in txt
    # Muestra la tarjeta usada (tipo, marca, últimos 4).
    assert "Tarjeta débito" in txt and "VISA" in txt and "****3610" in txt


def test_http_reimpresion_busca_y_muestra(op_client, make_producto, db, turno):
    v = _venta_pagada(db, turno, make_producto)
    r = op_client.post("/reimpresion/buscar", data={"folio": v.folio})
    assert r.status_code == 200
    assert "NOTA DE COMPRA" in r.text and v.folio in r.text
    # Folio inexistente → aviso.
    r2 = op_client.post("/reimpresion/buscar", data={"folio": "V-999999"})
    assert "no encontrado" in r2.text.lower()
