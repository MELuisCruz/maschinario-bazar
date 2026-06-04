"""Cobro en efectivo (ACCEPTANCE_TESTS §3, AT-3.1..AT-3.3) y descuento de stock."""

from decimal import Decimal

import pytest

from app.models import Producto
from app.services import cobro, ventas

D = Decimal


def _venta_con(
    db,
    turno,
    make_producto,
    codigo="EF",
    precio="116.00",
    existencia="10",
    controla=True,
):
    make_producto(
        codigo=codigo, precio=precio, existencia=existencia, controla_stock=controla
    )
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, codigo)
    db.commit()
    return v


def test_at_3_1_cobro_efectivo_cambio_y_pagada(db, turno, make_producto):
    v = _venta_con(db, turno, make_producto, precio="179.80")
    pago = cobro.cobrar_efectivo(db, v, D("200.00"))
    db.commit()
    assert pago.cambio == D("20.20")
    assert pago.estado == "aprobado"
    assert v.estado == "pagada"
    assert v.cerrado_en is not None


def test_at_3_2_recibido_menor_no_permite(db, turno, make_producto):
    v = _venta_con(db, turno, make_producto, precio="100.00")
    with pytest.raises(cobro.PagoInsuficiente):
        cobro.cobrar_efectivo(db, v, D("99.99"))
    db.rollback()
    assert v.estado == "abierta"  # nunca pagada por debajo del total


def test_at_3_3_efectivo_opera_offline(db, turno, make_producto):
    # El efectivo no toca red: el mismo flujo funciona sin MP. Si tocara red,
    # importar/usar el cliente MP fallaría; aquí no se invoca.
    v = _venta_con(db, turno, make_producto, precio="50.00")
    pago = cobro.cobrar_efectivo(db, v, D("50.00"))
    db.commit()
    assert v.estado == "pagada" and pago.cambio == D("0.00")


def test_at_6_3_cobro_descuenta_stock(db, turno, make_producto):
    v = _venta_con(
        db, turno, make_producto, codigo="STK", precio="10.00", existencia="5"
    )
    cobro.cobrar_efectivo(db, v, D("10.00"))
    db.commit()
    p = db.query(Producto).filter_by(codigo_barras="STK").one()
    assert p.existencia == D("4")  # 5 - 1


def test_at_6_4_sin_control_no_descuenta(db, turno, make_producto):
    v = _venta_con(
        db,
        turno,
        make_producto,
        codigo="NOSTK",
        precio="10.00",
        existencia="5",
        controla=False,
    )
    cobro.cobrar_efectivo(db, v, D("10.00"))
    db.commit()
    p = db.query(Producto).filter_by(codigo_barras="NOSTK").one()
    assert p.existencia == D("5")  # no controla stock → intacto


def test_http_cobro_efectivo(op_client, make_producto):
    make_producto(codigo="H", precio="20.00", existencia="3")
    op_client.post("/venta/scan", data={"codigo": "H"})
    r = op_client.post("/cobro/efectivo", data={"recibido": "50"})
    assert r.status_code == 200
    assert "cobrada" in r.text.lower()
