"""Autenticación y turno (ACCEPTANCE_TESTS §1, AT-1.1..AT-1.4)."""

from decimal import Decimal

from app.models import Cajero, Turno
from app.services import turnos
from app.services.security import hash_pin


def test_at_1_1_pin_correcto_abre_turno(db, cajero):
    auth = turnos.authenticate(db, "caja1", "2468")
    assert auth is not None and auth.id == cajero.id
    turno = turnos.abrir_turno(db, cajero.id, Decimal("500.00"))
    db.commit()
    assert turno.cerrado_en is None
    assert turno.fondo_inicial == Decimal("500.00")


def test_at_1_2_pin_incorrecto_rechaza_sin_turno(db, cajero):
    assert turnos.authenticate(db, "caja1", "0000") is None
    assert db.query(Turno).count() == 0


def test_at_1_3_turno_abierto_se_reanuda_no_duplica(db, cajero):
    t1 = turnos.abrir_turno(db, cajero.id, Decimal("100"))
    db.commit()
    t2 = turnos.abrir_turno(db, cajero.id, Decimal("999"))
    db.commit()
    assert t2.id == t1.id  # reanuda el mismo
    assert db.query(Turno).count() == 1


def test_at_1_4_cajero_inactivo_rechaza(db):
    inactivo = Cajero(
        usuario="off", nombre="Inactivo", pin_hash=hash_pin("1111"), activo=False
    )
    db.add(inactivo)
    db.commit()
    assert turnos.authenticate(db, "off", "1111") is None


def test_login_flow_http(client, cajero):
    # PIN incorrecto → 401, sin sesión.
    bad = client.post("/login", data={"usuario": "caja1", "pin": "0000"})
    assert bad.status_code == 401

    # PIN correcto → 303 a /turno.
    ok = client.post(
        "/login", data={"usuario": "caja1", "pin": "2468"}, follow_redirects=False
    )
    assert ok.status_code == 303 and ok.headers["location"] == "/turno"

    # Abrir turno → 303 a /venta.
    abrir = client.post(
        "/turno/abrir", data={"fondo_inicial": "300"}, follow_redirects=False
    )
    assert abrir.status_code == 303 and abrir.headers["location"] == "/venta"


def test_paginas_protegidas_redirigen_a_login(client):
    r = client.get("/turno", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"
