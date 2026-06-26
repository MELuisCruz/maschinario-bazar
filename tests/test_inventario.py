"""Inventario: existencias separadas del catálogo (cajero ve, admin edita)."""

from decimal import Decimal

from app.models import Producto

D = Decimal


def test_admin_reabastece_suma_existencia(op_client, db, make_producto):
    p = make_producto(codigo="INV-RB", existencia="2")
    r = op_client.post(f"/inventario/{p.id}/reabastecer", data={"cantidad": "8"})
    assert r.status_code == 200
    db.expire_all()
    assert db.get(Producto, p.id).existencia == D("10")


def test_admin_ajusta_a_valor_exacto(op_client, db, make_producto):
    p = make_producto(codigo="INV-AJ", existencia="7")
    r = op_client.post(f"/inventario/{p.id}/ajustar", data={"existencia": "3"})
    assert r.status_code == 200
    db.expire_all()
    assert db.get(Producto, p.id).existencia == D("3")


def test_admin_ajustar_negativo_rechazado(op_client, db, make_producto):
    p = make_producto(codigo="INV-NEG", existencia="5")
    r = op_client.post(f"/inventario/{p.id}/ajustar", data={"existencia": "-2"})
    assert r.status_code == 400
    db.expire_all()
    assert db.get(Producto, p.id).existencia == D("5")  # sin cambios


def test_cajero_consulta_inventario_solo_lectura(basic_client, make_producto):
    make_producto(codigo="INV-RO", nombre="Tardigrado", existencia="4")
    r = basic_client.get("/inventario")
    assert r.status_code == 200
    assert "Tardigrado" in r.text
    # Sin controles de edición (no aparecen los formularios de ajuste).
    assert 'action="/inventario/' not in r.text


def test_admin_ve_controles_de_inventario(op_client, make_producto):
    make_producto(codigo="INV-ADM", existencia="4")
    r = op_client.get("/inventario")
    assert r.status_code == 200
    assert 'action="/inventario/' in r.text  # formularios de reabasto/ajuste


def test_cajero_no_puede_ajustar(basic_client, make_producto):
    p = make_producto(codigo="INV-CJ", existencia="4")
    assert (
        basic_client.post(
            f"/inventario/{p.id}/reabastecer", data={"cantidad": "5"}
        ).status_code
        == 403
    )
    assert (
        basic_client.post(
            f"/inventario/{p.id}/ajustar", data={"existencia": "9"}
        ).status_code
        == 403
    )
