"""Corte de caja / turno (ACCEPTANCE_TESTS §7, AT-7.1..AT-7.3)."""

from decimal import Decimal

import pytest

from app.services import cobro, corte, devoluciones, ventas

D = Decimal


def _vender_efectivo(db, turno, make_producto, codigo, precio, recibido=None):
    make_producto(codigo=codigo, precio=precio, existencia="50")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, codigo)
    db.commit()
    cobro.cobrar_efectivo(db, v, Decimal(recibido or precio))
    db.commit()
    return v


def test_at_7_1_esperado_y_desglose(db, turno, make_producto):
    # fondo 500 (fixture) + 2 ventas efectivo (100 + 50) = 650 esperado.
    _vender_efectivo(db, turno, make_producto, "A", "100.00")
    _vender_efectivo(db, turno, make_producto, "B", "50.00")
    res = corte.resumen(db, turno)
    assert res.fondo_inicial == D("500.00")
    assert res.por_medio.get("efectivo") == D("150.00")
    assert res.esperado_efectivo == D("650.00")
    assert res.num_tickets == 2


def test_at_7_1_devolucion_efectivo_resta(db, turno, make_producto):
    v = _vender_efectivo(db, turno, make_producto, "C", "100.00")
    devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(v.lineas[0].id, D("1"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
    )
    db.commit()
    res = corte.resumen(db, turno)
    # 500 + 100 (venta) - 100 (devolución efectivo) = 500
    assert res.devoluciones_efectivo == D("100.00")
    assert res.esperado_efectivo == D("500.00")


def test_at_7_2_diferencia_faltante_y_sobrante(db, turno, make_producto):
    _vender_efectivo(db, turno, make_producto, "D", "100.00")  # esperado 600
    res, dif = corte.cerrar_turno(db, turno, D("590.00"), notas="falta")
    db.commit()
    assert res.esperado_efectivo == D("600.00")
    assert dif == D("-10.00")  # faltante
    assert turno.efectivo_contado == D("590.00")
    assert turno.cerrado_en is not None


def test_at_7_3_bloquea_con_ventas_abiertas(db, turno, make_producto):
    # Venta con líneas, sin cobrar (abierta).
    make_producto(codigo="OPEN", precio="20.00", existencia="5")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "OPEN")
    db.commit()
    assert corte.ventas_abiertas(db, turno.id) == 1
    with pytest.raises(corte.VentasAbiertas):
        corte.cerrar_turno(db, turno, D("500.00"))
    db.rollback()


def test_http_corte(op_client, make_producto):
    r = op_client.get("/corte")
    assert r.status_code == 200 and "EFECTIVO ESPERADO" in r.text
    r2 = op_client.post("/corte/cerrar", data={"efectivo_contado": "500", "notas": ""})
    assert r2.status_code == 200 and "Turno cerrado" in r2.text
