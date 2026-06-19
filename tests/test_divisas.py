"""Conversión de divisa por línea (USD/EUR → MXN), tipo de cambio manual.

Diseño (titular 18-jun-2026): TC manual (admin) con sugerencia desde API; el
total siempre en MXN; el ticket muestra divisa + tipo de cambio. Accesible por
admin y cajero.
"""

from decimal import Decimal

import pytest

from app.services import cobro, divisas, ventas
from app.services.printing import construir_ticket_texto

D = Decimal


def test_rates_default_cero_y_set(db):
    r = divisas.get_rates(db)
    assert r["MXN"] == D("1")
    assert r["USD"] == D("0") and r["EUR"] == D("0")  # sin configurar
    divisas.set_rates(db, D("17.50"), D("19.90"))
    db.commit()
    r = divisas.get_rates(db)
    assert r["USD"] == D("17.50") and r["EUR"] == D("19.90")


def test_convertir(db):
    divisas.set_rates(db, D("17.50"), D("20"))
    db.commit()
    assert divisas.convertir(db, D("5"), "USD") == (D("87.50"), D("17.50"))
    assert divisas.convertir(db, D("100"), "MXN") == (D("100"), D("1"))


def test_convertir_sin_tipo_de_cambio_falla(db):
    with pytest.raises(divisas.TipoCambioNoConfigurado):
        divisas.convertir(db, D("5"), "USD")  # rate 0
    db.rollback()


def test_especial_en_divisa(db, turno):
    divisas.set_rates(db, D("17.50"), D("20"))
    db.commit()
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ln = ventas.agregar_especial(db, v, "Importado", "", D("10"), "USD")
    db.commit()
    assert ln.divisa == "USD"
    assert ln.precio_divisa == D("10.00")
    assert ln.tipo_cambio == D("17.50")
    assert ln.precio_unit == D("175.00")  # 10 * 17.50 → total en MXN


def test_set_precio_divisa_por_linea_ida_y_vuelta(db, turno, make_producto):
    divisas.set_rates(db, D("18"), D("20"))
    db.commit()
    make_producto(codigo="PX", precio="100.00", existencia="5")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "PX")
    ln = v.lineas[0]
    ventas.set_precio_divisa(db, ln, "USD", D("3"))
    db.commit()
    assert ln.divisa == "USD" and ln.precio_unit == D("54.00")  # 3 * 18
    ventas.set_precio_divisa(db, ln, "MXN", D("99"))
    db.commit()
    assert ln.divisa == "MXN"
    assert ln.precio_unit == D("99.00")
    assert ln.precio_divisa is None and ln.tipo_cambio is None


def test_ticket_muestra_divisa_y_tc(db, turno):
    divisas.set_rates(db, D("17.35"), D("20"))
    db.commit()
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_especial(db, v, "Import", "", D("5"), "USD")
    db.commit()
    cobro.cobrar_efectivo(db, v, v.total)
    db.commit()
    txt = construir_ticket_texto(
        v, cajero_nombre="Ana", business_name="X", pagos=v.pagos
    )
    assert "USD 5.00 @ 17.3500 = $86.75" in txt


def test_actualizar_desde_api(db, monkeypatch):
    monkeypatch.setattr(
        divisas,
        "fetch_api_rates",
        lambda: {"USD": D("18.1234"), "EUR": D("20.5"), "fecha": "test"},
    )
    divisas.actualizar_desde_api(db)
    db.commit()
    r = divisas.get_rates(db)
    assert r["USD"] == D("18.1234") and r["EUR"] == D("20.5")
    assert divisas.fecha_actualizacion(db) == "test"


def test_http_especial_divisa_cajero(basic_client, db):
    divisas.set_rates(db, D("17.50"), D("20"))
    db.commit()
    r = basic_client.post(
        "/venta/especial",
        data={"referencia": "Imp", "descripcion": "", "precio": "4", "divisa": "USD"},
    )
    assert r.status_code == 200
    assert "USD" in r.text  # la línea muestra la divisa


def test_http_precio_divisa_sin_tc_avisa(op_client, db, make_producto):
    # Sin tipo de cambio configurado, intentar precio en USD avisa (no rompe).
    make_producto(codigo="DZ", precio="50.00", existencia="3")
    op_client.post("/venta/scan", data={"codigo": "DZ"})
    from app.models import VentaLinea

    ln = db.query(VentaLinea).first()
    r = op_client.post(
        f"/venta/linea/{ln.id}/divisa", data={"divisa": "USD", "monto": "2"}
    )
    assert r.status_code == 200
    assert "tipo de cambio" in r.text.lower()
