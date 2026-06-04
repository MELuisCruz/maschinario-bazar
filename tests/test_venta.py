"""Venta (ACCEPTANCE_TESTS §2, AT-2.1..AT-2.7)."""

from decimal import Decimal

import pytest

from app.services import ventas

D = Decimal


def _venta(db, turno):
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    db.commit()
    return v


def test_at_2_1_escaneo_agrega_linea_con_snapshots(db, turno, make_producto):
    make_producto(codigo="ABC123", nombre="Cuaderno", precio="32.50", iva_tasa="0.160")
    v = _venta(db, turno)
    res = ventas.agregar_por_codigo(db, v, "ABC123")
    db.commit()
    assert res.linea.descripcion == "Cuaderno"  # snapshot
    assert res.linea.precio_unit == D("32.50")
    assert res.linea.iva_tasa == D("0.160")
    assert res.linea.cantidad == D("1")


def test_at_2_2_codigo_inexistente_no_agrega(db, turno, make_producto):
    make_producto(codigo="EXISTE")
    v = _venta(db, turno)
    with pytest.raises(ventas.ProductoNoEncontrado):
        ventas.agregar_por_codigo(db, v, "NOEXISTE")
    db.rollback()
    assert len(v.lineas) == 0


def test_at_2_3_mismo_producto_incrementa_cantidad(db, turno, make_producto):
    make_producto(codigo="DUP", precio="10.00")
    v = _venta(db, turno)
    ventas.agregar_por_codigo(db, v, "DUP")
    ventas.agregar_por_codigo(db, v, "DUP")
    db.commit()
    assert len(v.lineas) == 1
    assert v.lineas[0].cantidad == D("2")


def test_at_2_4_totales_iva_incluido(db, turno, make_producto):
    make_producto(codigo="IVA", precio="116.00")
    v = _venta(db, turno)
    ventas.agregar_por_codigo(db, v, "IVA")
    db.commit()
    assert v.total == D("116.00")
    assert v.subtotal == D("100.00")
    assert v.iva_total == D("16.00")
    assert v.subtotal + v.iva_total == v.total


def test_at_2_5_descuento_global_recalcula(db, turno, make_producto):
    make_producto(codigo="X", precio="116.00")
    v = _venta(db, turno)
    ventas.agregar_por_codigo(db, v, "X")
    ventas.aplicar_descuento_global(db, v, D("16.00"))
    db.commit()
    assert v.total == D("100.00")
    assert v.descuento_total == D("16.00")


def test_at_2_6_stock_cero_avisa_sin_romper(db, turno, make_producto):
    make_producto(codigo="SIN", existencia="0", controla_stock=True)
    v = _venta(db, turno)
    res = ventas.agregar_por_codigo(db, v, "SIN")
    db.commit()
    assert res.aviso is not None  # avisa
    assert len(v.lineas) == 1  # pero la línea se agrega (no rompe)


def test_at_2_7_cancelar_no_afecta_stock_ni_caja(db, turno, make_producto):
    p = make_producto(codigo="C", precio="50.00", existencia="5")
    v = _venta(db, turno)
    ventas.agregar_por_codigo(db, v, "C")
    db.commit()
    ventas.cancelar(db, v)
    db.commit()
    assert v.estado == "cancelada"
    db.refresh(p)
    assert p.existencia == D("5")  # stock intacto (se descuenta al cobrar)


def test_http_scan_y_cancelar(op_client, make_producto):
    make_producto(codigo="HTTP1", nombre="Pluma", precio="8.00")
    r = op_client.post("/venta/scan", data={"codigo": "HTTP1"})
    assert r.status_code == 200
    assert "Pluma" in r.text
    # Código inexistente → aviso, no rompe.
    r2 = op_client.post("/venta/scan", data={"codigo": "NADA"})
    assert "no encontrado" in r2.text.lower()
