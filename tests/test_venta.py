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


def test_at_2_6_agotado_se_bloquea(db, turno, make_producto):
    # Decisión del titular (18-jun-2026): vender sin existencia se BLOQUEA.
    make_producto(codigo="SIN", existencia="0", controla_stock=True)
    v = _venta(db, turno)
    res = ventas.agregar_por_codigo(db, v, "SIN")
    db.commit()
    assert res.bloqueado is True
    assert res.aviso is not None
    assert len(v.lineas) == 0  # NO se agrega (agotado)


def test_no_excede_existencia_al_incrementar(db, turno, make_producto):
    make_producto(codigo="LIM", existencia="2", controla_stock=True)
    v = _venta(db, turno)
    ventas.agregar_por_codigo(db, v, "LIM")  # 1
    ventas.agregar_por_codigo(db, v, "LIM")  # 2 (== existencia)
    res = ventas.agregar_por_codigo(db, v, "LIM")  # 3 > 2 → bloquea
    db.commit()
    assert res.bloqueado is True
    assert v.lineas[0].cantidad == D("2")  # no pasó del stock


def test_sin_control_de_stock_no_se_bloquea(db, turno, make_producto):
    make_producto(codigo="LIBRE", existencia="0", controla_stock=False)
    v = _venta(db, turno)
    res = ventas.agregar_por_codigo(db, v, "LIBRE")
    db.commit()
    assert res.bloqueado is False
    assert len(v.lineas) == 1  # sin control de stock: se vende sin tope


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


# --- Búsqueda por nombre en la barra de venta (desplegable de coincidencias) ---


def test_buscar_productos_por_nombre_sku_minimo_y_solo_activos(db, make_producto):
    make_producto(codigo="C1", nombre="Botella de Klein", sku="KB-00")
    make_producto(codigo="C2", nombre="Banda de Moebius", sku="MT-00")
    inactivo = make_producto(codigo="C3", nombre="Klein inactivo", sku="ZZ-00")
    inactivo.activo = False
    db.commit()

    # Parcial por nombre, insensible a mayúsculas; el inactivo no aparece.
    res = ventas.buscar_productos(db, "klein")
    assert [p.nombre for p in res] == ["Botella de Klein"]
    # Por SKU.
    assert ventas.buscar_productos(db, "MT-00")[0].nombre == "Banda de Moebius"
    # Varias coincidencias ordenadas por nombre.
    nombres = [p.nombre for p in ventas.buscar_productos(db, "de")]
    assert nombres == ["Banda de Moebius", "Botella de Klein"]
    # Menos de 2 caracteres → sin resultados (evita ruido al teclear/escanear).
    assert ventas.buscar_productos(db, "k") == []


def test_agregar_por_id_agrega_linea(db, turno, make_producto):
    p = make_producto(codigo="ID1", nombre="Oloide", precio="119.00")
    v = _venta(db, turno)
    res = ventas.agregar_por_id(db, v, p.id)
    db.commit()
    assert res.linea.descripcion == "Oloide" and len(v.lineas) == 1
    with pytest.raises(ventas.ProductoNoEncontrado):
        ventas.agregar_por_id(db, v, 999999)
    db.rollback()


def test_http_buscar_y_agregar(op_client, make_producto):
    make_producto(codigo="BN1", nombre="Tardigrado", precio="45.00", sku="TARD-0")
    # GET búsqueda → desplegable con la coincidencia (no agrega aún).
    r = op_client.get("/venta/buscar", params={"codigo": "tardi"})
    assert r.status_code == 200
    assert "Tardigrado" in r.text and "/venta/agregar" in r.text
    # Sin coincidencias.
    r0 = op_client.get("/venta/buscar", params={"codigo": "noexiste"})
    assert "Sin coincidencias" in r0.text
    # POST agregar por id → agrega la línea elegida del desplegable.
    prod = make_producto(codigo="BN2", nombre="Cubo Infinito", precio="69.00")
    r2 = op_client.post("/venta/agregar", data={"producto_id": prod.id})
    assert r2.status_code == 200 and "Cubo Infinito" in r2.text
