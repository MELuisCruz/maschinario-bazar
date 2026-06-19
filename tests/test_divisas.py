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


def test_set_divisa_solo_visualiza_no_cambia_precio(db, turno, make_producto):
    # Catálogo: cambiar divisa NO toca el precio MXN ni el importe; solo muestra
    # el unitario convertido. (Regla: el precio no se edita salvo especial.)
    divisas.set_rates(db, D("20"), D("25"))
    db.commit()
    make_producto(codigo="PX", precio="100.00", existencia="5")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "PX")
    ln = v.lineas[0]
    ventas.set_divisa(db, ln, "USD")
    db.commit()
    assert ln.divisa == "USD"
    assert ln.precio_unit == D("100.00")  # MXN intacto
    assert ln.precio_divisa == D("5.00")  # 100 / 20 (solo display)
    assert ln.importe == D("100.00")  # importe siempre MXN
    ventas.set_divisa(db, ln, "MXN")
    db.commit()
    assert ln.divisa == "MXN" and ln.precio_divisa is None and ln.tipo_cambio is None


def test_set_precio_especial_rechaza_catalogo(db, turno, make_producto):
    divisas.set_rates(db, D("20"), D("25"))
    db.commit()
    make_producto(codigo="PY", precio="100.00", existencia="5")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "PY")
    ln = v.lineas[0]
    with pytest.raises(ValueError):  # no es producto especial
        ventas.set_precio_especial(db, ln, "USD", D("3"))
    db.rollback()


def test_set_precio_especial_edita_especial(db, turno):
    divisas.set_rates(db, D("18"), D("20"))
    db.commit()
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ln = ventas.agregar_especial(db, v, "Granel", "", D("10"), "MXN")
    db.commit()
    ventas.set_precio_especial(db, ln, "USD", D("3"))
    db.commit()
    assert ln.divisa == "USD" and ln.precio_unit == D("54.00")  # 3 * 18


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


def test_http_cambiar_divisa_sin_tc_avisa(op_client, db, make_producto):
    # Sin tipo de cambio configurado, cambiar la divisa de display avisa (no rompe).
    make_producto(codigo="DZ", precio="50.00", existencia="3")
    op_client.post("/venta/scan", data={"codigo": "DZ"})
    from app.models import VentaLinea

    ln = db.query(VentaLinea).first()
    r = op_client.post(f"/venta/linea/{ln.id}/divisa", data={"divisa": "USD"})
    assert r.status_code == 200
    assert "tipo de cambio" in r.text.lower()


def test_http_precio_especial_rechaza_en_catalogo(op_client, db, make_producto):
    # Intentar editar precio (endpoint de especial) en un producto de catálogo:
    # se rechaza (el precio de catálogo no se edita).
    divisas.set_rates(db, D("18"), D("20"))
    db.commit()
    make_producto(codigo="CAT", precio="50.00", existencia="3")
    op_client.post("/venta/scan", data={"codigo": "CAT"})
    from app.models import VentaLinea

    ln = db.query(VentaLinea).first()
    r = op_client.post(
        f"/venta/linea/{ln.id}/precio-especial", data={"divisa": "USD", "monto": "9"}
    )
    assert r.status_code == 200
    assert "solo el producto especial" in r.text.lower()
    db.expire_all()
    assert db.get(VentaLinea, ln.id).precio_unit == D("50.00")  # precio intacto
