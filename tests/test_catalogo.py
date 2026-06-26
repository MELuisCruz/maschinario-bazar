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


def test_import_csv_existencia_opcional_default_1(db):
    res = cat.importar_csv(db, "codigo_barras,nombre,precio\nNEW1,Item nuevo,9.00\n")
    db.commit()
    assert res.creados == 1
    p = db.query(Producto).filter_by(codigo_barras="NEW1").one()
    assert p.existencia == D("1")  # default 1 para items nuevos sin cantidad


def test_import_csv_update_sin_existencia_conserva_stock(db):
    cat.crear_producto(
        db, nombre="X", precio=D("5"), codigo_barras="UPD1", existencia_inicial=D("7")
    )
    db.commit()
    res = cat.importar_csv(db, "codigo_barras,nombre,precio\nUPD1,X2,6.00\n")
    db.commit()
    assert res.actualizados == 1
    p = db.query(Producto).filter_by(codigo_barras="UPD1").one()
    assert p.nombre == "X2"
    assert p.existencia == D("7")  # sin columna existencia: no toca el stock


def test_import_csv_upsert_por_sku(db):
    cat.crear_producto(
        db, nombre="SoloSku", precio=D("5"), sku="SK-1", existencia_inicial=D("3")
    )
    db.commit()
    res = cat.importar_csv(db, "sku,nombre,precio,existencia\nSK-1,SoloSku2,8.00,10\n")
    db.commit()
    assert res.actualizados == 1  # actualiza por SKU, no crea duplicado
    p = db.query(Producto).filter_by(sku="SK-1").one()
    assert p.nombre == "SoloSku2" and p.existencia == D("10")


def test_import_csv_codigo_barras_na_no_colapsa_filas(db):
    # Bug real: "N/A" literal en codigo_barras hacía que TODAS las filas
    # compartieran clave y el upsert las colapsara en un solo producto.
    # Con la normalización, "N/A" = sin código y se distinguen por SKU.
    csv_text = (
        "codigo_barras,nombre,precio,iva_tasa,existencia,controla_stock,sku\n"
        "N/A,Agujero Negro,99,0.16,5,true,BH-M-00\n"
        "N/A,Cubo Infinito,69,0.16,7,true,IC-00\n"
        "n/a,Oloide,119,0.16,7,true,Geo-O-01\n"
    )
    res = cat.importar_csv(db, csv_text)
    db.commit()
    assert res.creados == 3 and not res.errores
    assert db.query(Producto).count() == 3
    # Ninguno quedó con el código basura "N/A".
    assert db.query(Producto).filter(Producto.codigo_barras.isnot(None)).count() == 0
    nombres = {p.nombre for p in db.query(Producto).all()}
    assert nombres == {"Agujero Negro", "Cubo Infinito", "Oloide"}


def test_http_alta_con_sku_sin_codigo_barras(op_client, db):
    r = op_client.post(
        "/catalogo/alta", data={"nombre": "SoloSKU", "precio": "5.00", "sku": "MAN-1"}
    )
    assert r.status_code == 200 and "creado" in r.text
    db.expire_all()
    p = db.query(Producto).filter_by(sku="MAN-1").one()
    assert p.codigo_barras is None and p.existencia == D("1")


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


def test_realta_reactiva_producto_eliminado_conserva_id(db, make_producto):
    # Bug: tras eliminar (lógico), re-dar de alta el mismo código/SKU decía
    # "ya existe". Ahora REACTIVA el mismo registro (conserva su historial).
    p = make_producto(codigo="RE1", sku="SKU-RE1", nombre="Original", existencia="3")
    pid = p.id
    cat.desactivar(db, p)
    db.commit()
    re = cat.crear_producto(
        db,
        nombre="Reinsertado",
        precio=D("99.00"),
        codigo_barras="RE1",
        existencia_inicial=D("5"),
    )
    db.commit()
    assert re.id == pid  # mismo registro: historial intacto
    assert re.activo is True
    assert re.nombre == "Reinsertado"
    assert re.existencia == D("5")  # existencia ajustada a la re-alta


def test_alta_duplicado_activo_sigue_rechazando(db, make_producto):
    make_producto(codigo="DUP-ACT", nombre="Activo")
    with pytest.raises(cat.CodigoDuplicado):
        cat.crear_producto(db, nombre="Otro", precio=D("1.00"), codigo_barras="DUP-ACT")
    db.rollback()


def test_http_eliminar_y_reinsertar(op_client, db, make_producto):
    p = make_producto(codigo="HRE", nombre="Vela", existencia="2")
    op_client.post(f"/catalogo/{p.id}/eliminar")
    # Re-alta por la UI con el mismo código → ya NO debe fallar.
    r = op_client.post(
        "/catalogo/alta",
        data={"nombre": "Vela nueva", "precio": "30.00", "codigo_barras": "HRE",
              "existencia": "4"},
    )
    assert r.status_code == 200
    assert "ya existe" not in r.text.lower()
    db.expire_all()
    prod = db.get(Producto, p.id)
    assert prod.activo is True and prod.nombre == "Vela nueva"


def test_http_eliminar_admin(op_client, db, make_producto):
    p = make_producto(codigo="HDEL", existencia="1")
    r = op_client.post(f"/catalogo/{p.id}/eliminar")
    assert r.status_code == 200
    db.expire_all()
    prod = db.get(Producto, p.id)
    assert prod.activo is False  # eliminación lógica
    # Ya no aparece en el listado del catálogo.
    assert "HDEL" not in r.text


def test_http_eliminar_no_admin_bloqueado(basic_client, db, make_producto):
    p = make_producto(codigo="NDEL", existencia="2")
    r = basic_client.post(f"/catalogo/{p.id}/eliminar")
    assert r.status_code == 403
