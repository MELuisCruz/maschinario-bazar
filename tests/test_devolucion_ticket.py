"""Ticket de devolución + etiquetas legibles de estado/medio."""

from decimal import Decimal

from sqlalchemy import select

from app.models import Venta, VentaLinea
from app.models.enums import EstadoVenta, MedioPago, etiqueta_estado, etiqueta_medio
from app.services import cobro, devoluciones, printing, ventas

D = Decimal


def _venta_pagada(db, turno, make_producto):
    make_producto(codigo="DT", precio="100.00", existencia="10")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, "DT")
    ventas.agregar_por_codigo(db, v, "DT")
    db.commit()
    cobro.cobrar_efectivo(db, v, v.total)
    db.commit()
    return v


def test_etiquetas_legibles():
    assert etiqueta_estado("devuelta_parcial") == "Devuelta parcial"
    assert etiqueta_estado(EstadoVenta.pagada) == "Pagada"
    assert etiqueta_medio(MedioPago.efectivo) == "Efectivo"
    assert etiqueta_medio("tarjeta_point") == "Tarjeta (Point)"
    assert etiqueta_estado(None) == ""  # tolerante


def test_construir_ticket_devolucion(db, turno, make_producto):
    v = _venta_pagada(db, turno, make_producto)
    ln = v.lineas[0]
    dev = devoluciones.crear_devolucion(
        db,
        v,
        [devoluciones.ItemDevolucion(ln.id, D("1"))],
        cajero_id=turno.cajero_id,
        turno_id=turno.id,
    )
    db.commit()
    txt = printing.construir_ticket_devolucion(
        dev, v, cajero_nombre="Ana", business_name="Bazar", medio="Efectivo"
    )
    assert "COMPROBANTE DE DEVOLUCIÓN" in txt
    assert v.folio in txt
    assert "TOTAL DEVUELTO:" in txt
    assert "Reembolso:" in txt and "Efectivo" in txt
    assert "Producto demo" in txt  # descripción de la línea devuelta


def test_http_confirmar_imprime_y_estado_legible(op_client, db, make_producto):
    make_producto(codigo="HD", precio="50.00", existencia="5")
    op_client.post("/venta/scan", data={"codigo": "HD"})
    op_client.post("/venta/scan", data={"codigo": "HD"})
    op_client.post("/cobro/efectivo", data={"recibido": "100"})
    db.expire_all()
    venta = db.scalar(
        select(Venta).where(Venta.estado == "pagada").order_by(Venta.id.desc())
    )
    linea = db.scalar(select(VentaLinea).where(VentaLinea.venta_id == venta.id))
    r = op_client.post(
        "/devolucion/confirmar",
        data={"folio": venta.folio, f"cant_{linea.id}": "1"},
    )
    assert r.status_code == 200
    assert "Devuelta parcial" in r.text  # etiqueta legible (no 'devuelta_parcial')
    # En tests no hay impresora física → aviso (no rompe).
    assert "Impresora no disponible" in r.text
