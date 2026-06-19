"""Configuración editable del ticket (módulo admin).

Cubre: defaults, persistencia, render del ticket con los campos editables y
control de acceso (solo admin).
"""

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from app.services import configuracion as cfg_svc
from app.services.printing import construir_ticket_texto


def _venta_stub():
    f = datetime(2026, 6, 18, 12, 0, tzinfo=timezone.utc)
    return SimpleNamespace(
        folio="V-0001",
        cerrado_en=f,
        creado_en=f,
        lineas=[
            SimpleNamespace(
                descripcion="Cosa",
                cantidad=Decimal("1"),
                importe=Decimal("116.00"),
                descuento=Decimal("0"),
            )
        ],
        subtotal=Decimal("100.00"),
        descuento_total=Decimal("0"),
        iva_total=Decimal("16.00"),
        total=Decimal("116.00"),
        pagos=[],
    )


def test_defaults_cuando_vacio(db):
    cfg = cfg_svc.get_config(db)
    assert cfg["ticket_establecimiento"]  # toma APP_BUSINESS_NAME
    assert cfg["ticket_pie"] == "¡Gracias por su compra!"
    assert cfg["ticket_evento"] == ""
    assert cfg["ticket_domicilio"] == ""
    assert cfg["ticket_telefono"] == ""


def test_set_y_get_persisten_con_trim(db):
    cfg_svc.set_config(
        db,
        {
            "ticket_establecimiento": "  Mi Bazar  ",
            "ticket_evento": "Bazar Navideño 2026",
            "ticket_pie": "Vuelva pronto",
        },
    )
    db.commit()
    cfg = cfg_svc.get_config(db)
    assert cfg["ticket_establecimiento"] == "Mi Bazar"
    assert cfg["ticket_evento"] == "Bazar Navideño 2026"
    assert cfg["ticket_pie"] == "Vuelva pronto"


def test_ticket_incluye_campos_editables():
    texto = construir_ticket_texto(
        _venta_stub(),
        cajero_nombre="Ana",
        business_name="Mi Bazar",
        evento="Bazar Navideño 2026",
        domicilio="Calle 1, Centro",
        telefono="55 1234 5678",
        pie="Vuelva pronto",
    )
    assert "MI BAZAR" in texto  # establecimiento va en mayúsculas
    assert "Bazar Navideño 2026" in texto
    assert "Calle 1, Centro" in texto
    assert "Tel: 55 1234 5678" in texto
    assert "Vuelva pronto" in texto
    assert "NOTA DE COMPRA  (no es CFDI)" in texto  # leyenda fija sigue


def test_ticket_omite_campos_vacios():
    texto = construir_ticket_texto(
        _venta_stub(), cajero_nombre="Ana", business_name="Mi Bazar"
    )
    assert "Tel:" not in texto  # sin teléfono, no aparece la línea
    assert "¡Gracias por su compra!" in texto  # pie por defecto


def test_ticket_fecha_formato_y_tz_por_defecto():
    # _venta_stub usa cerrado_en = 2026-06-18 12:00 UTC → UTC-6 = 06:00.
    texto = construir_ticket_texto(
        _venta_stub(), cajero_nombre="Ana", business_name="Bazar"
    )
    assert "Fecha: 18-06-2026 06:00 UTC-6" in texto


def test_ticket_fecha_formato_configurable():
    texto = construir_ticket_texto(
        _venta_stub(),
        cajero_nombre="Ana",
        business_name="Bazar",
        fecha_formato="%Y/%m/%d %H:%M",
        tz_offset=0,
    )
    assert "Fecha: 2026/06/18 12:00 UTC+0" in texto


def test_defaults_incluyen_fecha_y_tz(db):
    cfg = cfg_svc.get_config(db)
    assert cfg["ticket_fecha_formato"] == "%d-%m-%Y %H:%M"
    assert cfg["ticket_tz_offset"] == "-6"
    kw = cfg_svc.ticket_kwargs(db)
    assert kw["tz_offset"] == -6 and kw["fecha_formato"] == "%d-%m-%Y %H:%M"


def test_admin_ve_y_guarda(op_client):
    r = op_client.get("/configuracion")
    assert r.status_code == 200
    r = op_client.post(
        "/configuracion",
        data={
            "ticket_establecimiento": "Mi Bazar",
            "ticket_evento": "Feria 2026",
            "ticket_domicilio": "",
            "ticket_telefono": "",
            "ticket_pie": "Gracias",
        },
    )
    assert r.status_code == 200
    assert "Feria 2026" in r.text


def test_no_admin_bloqueado(basic_client):
    r = basic_client.get("/configuracion")
    assert r.status_code == 403
