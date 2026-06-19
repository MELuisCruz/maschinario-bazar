"""Catálogo e inventario (ACCEPTANCE_TESTS §6, AT-6.1, AT-6.2).

AT-6.3/AT-6.4 (descuento de stock en venta) se cubren en test_cobro_efectivo.
"""

from decimal import Decimal

import pytest

from app.models import Producto
from app.services import catalogo as cat

D = Decimal


def test_at_6_1_alta_codigo_unico_y_rechazo_duplicado(db):
    p = cat.crear_producto(
        db,
        nombre="Foco LED",
        precio=D("45.00"),
        codigo_barras="750300",
        existencia_inicial=D("10"),
    )
    db.commit()
    assert p.id is not None
    assert p.existencia == D("10")  # registrada vía movimiento 'alta'
    with pytest.raises(cat.CodigoDuplicado):
        cat.crear_producto(db, nombre="Otro", precio=D("1.00"), codigo_barras="750300")
    db.rollback()


def test_at_6_2_import_csv_reporta_filas_invalidas(db):
    csv_text = (
        "codigo_barras,nombre,precio,existencia\n"
        "111,Cuaderno,32.50,48\n"  # válido
        "222,,10.00,5\n"  # nombre vacío → error
        "333,Pluma,abc,5\n"  # precio inválido → error
        "444,Lápiz,5.50,100\n"  # válido
    )
    res = cat.importar_csv(db, csv_text)
    db.commit()
    assert res.creados == 2
    assert len(res.errores) == 2
    filas_error = [f for f, _ in res.errores]
    assert filas_error == [3, 4]  # numeración 1-based con encabezado
    # Solo las válidas se importaron.
    assert db.query(Producto).count() == 2


def test_import_csv_actualiza_existente(db):
    cat.crear_producto(
        db,
        nombre="Viejo",
        precio=D("10.00"),
        codigo_barras="900",
        existencia_inicial=D("5"),
    )
    db.commit()
    res = cat.importar_csv(
        db, "codigo_barras,nombre,precio,existencia\n900,Nuevo,12.00,8\n"
    )
    db.commit()
    assert res.actualizados == 1
    p = db.query(Producto).filter_by(codigo_barras="900").one()
    assert p.nombre == "Nuevo" and p.precio == D("12.00")
    assert p.existencia == D("8")  # ajuste vía bitácora


def test_http_alta_y_duplicado(op_client):
    r = op_client.post(
        "/catalogo/alta",
        data={
            "nombre": "Vela",
            "precio": "6.50",
            "codigo_barras": "C1",
            "existencia": "20",
        },
    )
    assert r.status_code == 200 and "creado" in r.text
    r2 = op_client.post(
        "/catalogo/alta",
        data={"nombre": "Vela2", "precio": "7.00", "codigo_barras": "C1"},
    )
    assert r2.status_code == 400 and "Ya existe" in r2.text


def test_http_import_csv(op_client):
    csv_bytes = b"codigo_barras,nombre,precio,existencia\nZ1,Jabon,13.50,88\n"
    r = op_client.post(
        "/catalogo/importar",
        files={"archivo": ("productos.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 200 and "1 creados" in r.text


# --- Re-abastecer y eliminar (gestión de catálogo, solo admin) ---


def test_reabastecer_suma_existencia(db, make_producto):
    p = make_producto(codigo="RB", existencia="5")
    cat.reabastecer(db, p, D("10"))
    db.commit()
    assert p.existencia == D("15")


def test_reabastecer_rechaza_no_positivo(db, make_producto):
    p = make_producto(codigo="RB0", existencia="5")
    with pytest.raises(ValueError):
        cat.reabastecer(db, p, D("0"))
    db.rollback()


def test_desactivar_es_eliminacion_logica(db, make_producto):
    p = make_producto(codigo="DEL", existencia="3")
    cat.desactivar(db, p)
    db.commit()
    assert p.activo is False


def test_http_reabastecer_admin(op_client, db, make_producto):
    p = make_producto(codigo="HRB", existencia="2")
    r = op_client.post(f"/catalogo/{p.id}/reabastecer", data={"cantidad": "8"})
    assert r.status_code == 200
    db.expire_all()
    assert db.get(Producto, p.id).existencia == D("10")


def test_http_eliminar_admin(op_client, db, make_producto):
    p = make_producto(codigo="HDEL", existencia="1")
    r = op_client.post(f"/catalogo/{p.id}/eliminar")
    assert r.status_code == 200
    db.expire_all()
    prod = db.get(Producto, p.id)
    assert prod.activo is False  # eliminación lógica
    # Ya no aparece en el listado del catálogo.
    assert "HDEL" not in r.text


def test_http_reabastecer_no_admin_bloqueado(basic_client, db, make_producto):
    p = make_producto(codigo="NRB", existencia="2")
    r = basic_client.post(f"/catalogo/{p.id}/reabastecer", data={"cantidad": "5"})
    assert r.status_code == 403


def test_http_eliminar_no_admin_bloqueado(basic_client, db, make_producto):
    p = make_producto(codigo="NDEL", existencia="2")
    r = basic_client.post(f"/catalogo/{p.id}/eliminar")
    assert r.status_code == 403
