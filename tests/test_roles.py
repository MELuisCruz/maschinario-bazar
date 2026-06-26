"""Control de acceso por rol — RBAC (PRD §2).

Reglas acordadas:
  1. Solo admin eleva/degrada roles.
  2. Solo admin actualiza el catálogo (alta/edición).
  3. Solo admin importa CSV (inserción masiva).
"""

import pytest

from app.models import RolCajero
from app.services import cajeros as cajeros_svc

# --- Servicio: gestión de roles ---


def test_es_admin(db, cajero, cajero_basico):
    assert cajeros_svc.es_admin(cajero) is True
    assert cajeros_svc.es_admin(cajero_basico) is False
    assert cajeros_svc.es_admin(None) is False


def test_crear_cajero_y_duplicado(db):
    c = cajeros_svc.crear_cajero(
        db, usuario="nuevo", nombre="N", pin="1111", rol="cajero"
    )
    db.commit()
    assert c.id is not None and c.rol == RolCajero.cajero
    with pytest.raises(cajeros_svc.UsuarioDuplicado):
        cajeros_svc.crear_cajero(db, usuario="nuevo", nombre="X", pin="2222")
    db.rollback()


def test_elevar_y_degradar_rol(db, cajero, cajero_basico):
    cajeros_svc.cambiar_rol(db, cajero_basico, "administrador")
    db.commit()
    assert cajeros_svc.es_admin(cajero_basico)
    cajeros_svc.cambiar_rol(db, cajero_basico, "cajero")
    db.commit()
    assert not cajeros_svc.es_admin(cajero_basico)


def test_no_degradar_ultimo_admin(db, cajero):
    # `cajero` (caja1) es el único admin → no se puede degradar.
    with pytest.raises(cajeros_svc.UltimoAdmin):
        cajeros_svc.cambiar_rol(db, cajero, "cajero")
    db.rollback()


def test_no_desactivar_ultimo_admin(db, cajero):
    with pytest.raises(cajeros_svc.UltimoAdmin):
        cajeros_svc.set_activo(db, cajero, False)
    db.rollback()


# --- HTTP: guardas de rol ---


def test_admin_puede_gestionar_usuarios(op_client):
    r = op_client.get("/usuarios")
    assert r.status_code == 200 and "Alta de cajero" in r.text
    r2 = op_client.post(
        "/usuarios/alta",
        data={"usuario": "caja9", "nombre": "Nueve", "pin": "9999", "rol": "cajero"},
    )
    assert r2.status_code == 200 and "creado" in r2.text


def test_no_admin_bloqueado_en_usuarios(basic_client):
    r = basic_client.get("/usuarios", follow_redirects=False)
    assert r.status_code == 403
    r2 = basic_client.post(
        "/usuarios/alta", data={"usuario": "x", "nombre": "x", "pin": "1"}
    )
    assert r2.status_code == 403


def test_no_admin_catalogo_es_admin_only_pero_ve_inventario(basic_client, make_producto):
    # Catálogo es 100% admin: el cajero NO entra (ni ver ni actualizar).
    assert basic_client.get("/catalogo").status_code == 403
    r = basic_client.post(
        "/catalogo/alta",
        data={"nombre": "Cosa", "precio": "10.00", "codigo_barras": "Z"},
    )
    assert r.status_code == 403
    # Inventario sí lo CONSULTA (solo lectura), pero no puede ajustar existencias.
    assert basic_client.get("/inventario").status_code == 200
    p = make_producto(codigo="INVROL", existencia="3")
    r2 = basic_client.post(f"/inventario/{p.id}/reabastecer", data={"cantidad": "5"})
    assert r2.status_code == 403


def test_no_admin_bloqueado_en_import_csv(basic_client):
    csv_bytes = b"codigo_barras,nombre,precio\nA,Algo,5.00\n"
    r = basic_client.post(
        "/catalogo/importar",
        files={"archivo": ("p.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 403


def test_admin_si_puede_catalogo_y_csv(op_client):
    r = op_client.post(
        "/catalogo/alta",
        data={"nombre": "Cosa", "precio": "10.00", "codigo_barras": "ADM1"},
    )
    assert r.status_code == 200 and "creado" in r.text
    r2 = op_client.post(
        "/catalogo/importar",
        files={
            "archivo": (
                "p.csv",
                b"codigo_barras,nombre,precio\nADM2,Otro,5.00\n",
                "text/csv",
            )
        },
    )
    assert r2.status_code == 200 and "1 creados" in r2.text
