"""Fixtures de pruebas: DB de test aislada y cliente HTTP (ACCEPTANCE_TESTS §11).

Usa una base `maschinario_test` en el mismo servidor PostgreSQL. Las tablas se
crean una vez por sesión (create_all es válido en pruebas; en producción se usa
Alembic, CLAUDE.md §7) y se truncan antes de cada test para aislarlo.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db import get_session
from app.main import app
from app.models import Base, Cajero, Producto, Turno
from app.services.security import hash_pin


def _test_database_url() -> str:
    url = get_settings().database_url
    # Apunta a la base de pruebas dedicada.
    return url.rsplit("/", 1)[0] + "/maschinario_test"


engine = create_engine(_test_database_url(), future=True)
TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine, checkfirst=True)


@pytest.fixture(autouse=True)
def _clean():
    """Trunca todas las tablas antes de cada test (aislamiento)."""
    tablas = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture(autouse=True)
def _sin_impresora(monkeypatch):
    """Los tests nunca tocan la impresora física: get_printer siempre 'falla'.

    El flujo de impresión es tolerante (imprimir_ticket devuelve ok=False), así
    que cobro/reimpresión se prueban sin enviar nada por USB.
    """

    def _no_printer(_settings=None):
        raise RuntimeError("sin impresora (test)")

    monkeypatch.setattr("app.services.printing.get_printer", _no_printer)
    monkeypatch.setattr(
        "app.services.printing.PRINT_ESPERA_S", 0
    )  # sin demora en tests


@pytest.fixture
def db() -> Session:
    s = TestSession()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def client():
    """TestClient con get_session apuntando a la DB de pruebas."""

    def _override():
        s = TestSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def cajero(db) -> Cajero:
    """Cajero activo con PIN '2468' (admin)."""
    c = Cajero(
        usuario="caja1",
        nombre="Ana Cajera",
        pin_hash=hash_pin("2468"),
        rol="administrador",
        activo=True,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def turno(db, cajero) -> Turno:
    """Turno abierto del cajero, con fondo inicial 500."""
    t = Turno(cajero_id=cajero.id, fondo_inicial=Decimal("500.00"))
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@pytest.fixture
def make_producto(db):
    """Factory de productos. Uso: make_producto(codigo='...', precio='116.00', ...)."""

    seq = {"n": 0}

    def _make(
        codigo="7500000000001",
        nombre="Producto demo",
        precio="116.00",
        existencia="10",
        controla_stock=True,
        iva_tasa="0.160",
        sku=None,
    ):
        seq["n"] += 1
        p = Producto(
            sku=sku or f"SKU{seq['n']:04d}",
            codigo_barras=codigo,
            nombre=nombre,
            precio=Decimal(precio),
            existencia=Decimal(existencia),
            controla_stock=controla_stock,
            iva_tasa=Decimal(iva_tasa),
            activo=True,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return p

    return _make


@pytest.fixture
def op_client(client, cajero, turno):
    """Cliente autenticado como admin (caja1) con turno abierto."""
    client.post("/login", data={"usuario": "caja1", "pin": "2468"})
    # Asocia el turno ya abierto a la sesión.
    client.post("/turno/reanudar")
    return client


@pytest.fixture
def cajero_basico(db) -> Cajero:
    """Cajero con rol 'cajero' (no admin), PIN '1357'."""
    c = Cajero(
        usuario="caja2",
        nombre="Beto Cajero",
        pin_hash=hash_pin("1357"),
        rol="cajero",
        activo=True,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def basic_client(client, cajero_basico):
    """Cliente autenticado como cajero NO admin, con turno abierto."""
    from app.models import Turno

    t = Turno(cajero_id=cajero_basico.id, fondo_inicial=Decimal("0"))
    db_s = TestSession()
    db_s.add(t)
    db_s.commit()
    db_s.close()
    client.post("/login", data={"usuario": "caja2", "pin": "1357"})
    client.post("/turno/reanudar")
    return client
