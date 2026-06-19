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
    assert "*** REIMPRESIÓN 2026-06-04 10:30 ***" in reimp
    # Idéntico salvo la leyenda añadida al pie.
    assert reimp.startswith(base)
    # No altera datos de la venta.
    assert v.estado == "pagada" and v.total == D("116.00")


def test_http_reimpresion_busca_y_muestra(op_client, make_producto, db, turno):
    v = _venta_pagada(db, turno, make_producto)
    r = op_client.post("/reimpresion/buscar", data={"folio": v.folio})
    assert r.status_code == 200
    assert "NOTA DE COMPRA" in r.text and v.folio in r.text
    # Folio inexistente → aviso.
    r2 = op_client.post("/reimpresion/buscar", data={"folio": "V-999999"})
    assert "no encontrado" in r2.text.lower()
