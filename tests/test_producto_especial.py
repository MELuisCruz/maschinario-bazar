"""Producto especial: precio ad-hoc en caja + notas de trazabilidad.

Diseño (decisión del titular 18-jun-2026): línea «Producto especial: <ref>»
(ref ≤50 en el ticket), notas/descripción ≤100 SOLO internas, sin stock, IVA
16% incluido. Accesible por admin y cajero.
"""

from decimal import Decimal

import pytest

from app.services import cobro, ventas
from app.services.printing import construir_ticket_texto

D = Decimal


def _venta(db, turno):
    return ventas.get_or_create_venta(db, turno.id, turno.cajero_id)


def test_agregar_especial_crea_linea(db, turno):
    v = _venta(db, turno)
    ln = ventas.agregar_especial(db, v, "Artículo a granel", "lote 7", D("58.00"))
    db.commit()
    assert ln.descripcion == "Producto especial: Artículo a granel"
    assert ln.notas == "lote 7"
    assert ln.precio_unit == D("58.00")
    assert ln.iva_tasa == D("0.160")
    assert ln.cantidad == D("1")
    assert len(v.lineas) == 1


def test_especial_singleton_oculto(db):
    p1 = ventas.get_or_create_especial(db)
    p2 = ventas.get_or_create_especial(db)
    db.commit()
    assert p1.id == p2.id  # idempotente
    assert p1.activo is False  # oculto del catálogo
    assert p1.controla_stock is False  # no descuenta inventario


def test_especial_valida_referencia_y_precio(db, turno):
    v = _venta(db, turno)
    with pytest.raises(ValueError):
        ventas.agregar_especial(db, v, "  ", "x", D("10"))  # ref vacía
    with pytest.raises(ValueError):
        ventas.agregar_especial(db, v, "ref", "x", D("0"))  # precio 0
    db.rollback()


def test_especial_trunca_longitudes(db, turno):
    v = _venta(db, turno)
    ref = "R" * 80
    notas = "N" * 200
    ln = ventas.agregar_especial(db, v, ref, notas, D("5.00"))
    db.commit()
    assert ln.descripcion == "Producto especial: " + "R" * 50  # ref ≤ 50
    assert ln.notas == "N" * 100  # notas ≤ 100


def test_especial_en_ticket_con_ref_sin_notas(db, turno):
    v = _venta(db, turno)
    ventas.agregar_especial(db, v, "Artículo a granel", "lote 7 caja azul", D("58.00"))
    db.commit()
    cobro.cobrar_efectivo(db, v, D("58.00"))
    db.commit()
    txt = construir_ticket_texto(
        v, cajero_nombre="Ana", business_name="X", pagos=v.pagos
    )
    assert "Producto especial: Artículo a granel" in txt  # ref completa en el ticket
    assert "lote 7 caja azul" not in txt  # notas NO se imprimen
    assert v.estado == "pagada"


def test_especial_no_aparece_en_catalogo(op_client, db, turno):
    v = _venta(db, turno)
    ventas.agregar_especial(db, v, "Algo", "nota", D("9.00"))
    db.commit()
    r = op_client.get("/catalogo")
    assert "__ESPECIAL__" not in r.text  # el singleton está oculto


def test_http_cajero_puede_agregar_especial(basic_client):
    # require_turno (admin y cajero); basic_client es cajero no-admin con turno.
    r = basic_client.post(
        "/venta/especial",
        data={"referencia": "Granel", "descripcion": "nota interna", "precio": "33.50"},
    )
    assert r.status_code == 200
    assert "Producto especial: Granel" in r.text
    assert "nota interna" in r.text  # las notas se ven en pantalla (no en ticket)
