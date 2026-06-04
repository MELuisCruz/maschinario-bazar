"""Devolución (ACCEPTANCE_TESTS §5, AT-5.1..AT-5.4)."""

from decimal import Decimal

import pytest

from app.models import Producto
from app.services import cobro, devoluciones, ventas
from tests.test_cobro_tarjeta import FakeMP

D = Decimal


def _venta_pagada(
    db, turno, make_producto, codigo="DV", precio="100.00", existencia="10", cant=2
):
    make_producto(codigo=codigo, precio=precio, existencia=existencia)
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    for _ in range(cant):
        ventas.agregar_por_codigo(db, v, codigo)
    db.commit()
    cobro.cobrar_efectivo(db, v, v.total)
    db.commit()
    return v


def test_at_5_1_devolucion_parcial_y_estado(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto, cant=2)
    linea = v.lineas[0]
    dev = devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(linea.id, D("1"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
    )
    db.commit()
    assert dev.monto == D("100.00")
    assert v.estado == "devuelta_parcial"


def test_at_5_1_devolucion_total(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto, cant=2)
    linea = v.lineas[0]
    devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(linea.id, D("2"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
    )
    db.commit()
    assert v.estado == "devuelta_total"


def test_at_5_2_no_devolver_mas_de_lo_vendido(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto, cant=2)
    linea = v.lineas[0]
    with pytest.raises(devoluciones.ExcedeVendido):
        devoluciones.crear_devolucion(
            db,
            v,
            [devoluciones.ItemDevolucion(linea.id, D("3"))],
            cajero_id=turno.cajero_id,
            turno_id=turno.id,
        )
    db.rollback()


def test_at_5_2_acumulado_excede(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto, cant=2)
    linea = v.lineas[0]
    devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(linea.id, D("1"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
    )
    db.commit()
    # Ya se devolvió 1 de 2; intentar 2 más debe exceder.
    with pytest.raises(devoluciones.ExcedeVendido):
        devoluciones.crear_devolucion(
            db,
            v,
            [devoluciones.ItemDevolucion(linea.id, D("2"))],
            cajero_id=turno.cajero_id,
            turno_id=turno.id,
        )
    db.rollback()


def test_at_5_3_refund_tarjeta(db, turno, make_producto):
    # Venta pagada con tarjeta.
    make_producto(codigo="TJ", precio="116.00", existencia="5")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "TJ")
    db.commit()
    fake = FakeMP(pay_status="approved")
    pago = cobro.iniciar_tarjeta(db, v, fake, "T")
    cobro.conciliar_tarjeta(db, pago, fake)
    db.commit()
    assert v.estado == "pagada"

    linea = v.lineas[0]
    devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(linea.id, D("1"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
        client=fake,
    )
    db.commit()
    assert pago.mp_order_id in fake.refunded  # se invocó refund (AT-5.3)


def test_at_5_4_reintegra_stock(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto, codigo="ST", existencia="10", cant=2)
    p = db.query(Producto).filter_by(codigo_barras="ST").one()
    assert p.existencia == D("8")  # 10 - 2 vendidos
    linea = v.lineas[0]
    devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(linea.id, D("2"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
    )
    db.commit()
    db.refresh(p)
    assert p.existencia == D("10")  # reintegrado


def test_http_devolucion_flow(op_client, make_producto, db, turno):
    from app.services import cobro, ventas

    make_producto(codigo="HTTPDV", precio="50.00", existencia="5")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "HTTPDV")
    db.commit()
    cobro.cobrar_efectivo(db, v, v.total)
    db.commit()
    folio = v.folio

    r = op_client.post("/devolucion/buscar", data={"folio": folio})
    assert r.status_code == 200 and folio in r.text
    linea_id = v.lineas[0].id
    r2 = op_client.post(
        "/devolucion/confirmar", data={"folio": folio, f"cant_{linea_id}": "1"}
    )
    assert "Devolución registrada" in r2.text
