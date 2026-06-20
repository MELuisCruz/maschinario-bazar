"""Reportes y export fiscal (ACCEPTANCE_TESTS §8, AT-8.1, AT-8.2)."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.services import cobro, fiscal_export, reportes, ventas

D = Decimal


def _vender(db, turno, make_producto, codigo, precio):
    make_producto(codigo=codigo, precio=precio, existencia="20")
    v = ventas.get_or_create_venta(db, turno.id, turno.cajero_id)
    ventas.agregar_por_codigo(db, v, codigo)
    db.commit()
    cobro.cobrar_efectivo(db, v, v.total)
    db.commit()
    return v


def _rango_amplio():
    ahora = datetime.now(timezone.utc)
    return ahora - timedelta(days=1), ahora + timedelta(days=1)


def test_at_8_1_totaliza_por_periodo_y_medio(db, turno, make_producto):
    _vender(db, turno, make_producto, "R1", "100.00")
    _vender(db, turno, make_producto, "R2", "50.00")
    desde, hasta = _rango_amplio()
    rep = reportes.generar(db, desde, hasta)
    assert rep.num_tickets == 2
    assert rep.total == D("150.00")
    assert rep.por_medio.get("efectivo") == D("150.00")
    assert rep.ticket_promedio == D("75.00")
    assert "Ana Cajera" in rep.por_cajero


def test_reporte_lista_folios_del_periodo(db, turno, make_producto):
    v1 = _vender(db, turno, make_producto, "F1", "100.00")
    v2 = _vender(db, turno, make_producto, "F2", "50.00")
    desde, hasta = _rango_amplio()
    rep = reportes.generar(db, desde, hasta)
    folios = [x["folio"] for x in rep.ventas]
    assert v1.folio in folios and v2.folio in folios
    assert len(rep.ventas) == 2
    for fila in rep.ventas:
        assert {"folio", "fecha", "total", "estado"} <= set(fila)
        assert fila["estado"] == "pagada"


def test_at_8_2_export_fiscal_marca_y_rfc(db, turno, make_producto):
    v = _vender(db, turno, make_producto, "EX", "116.00")
    assert v.exportada_fiscal is False
    desde, hasta = _rango_amplio()
    exp = fiscal_export.generar_export(db, desde, hasta)
    db.commit()

    assert exp.rfc_destino == "XAXX010101000"  # RFC genérico
    assert exp.marcadas == 1
    fila = exp.filas[0]
    # Campos requeridos: folio, fecha, subtotal, IVA, total, medio.
    for campo in ("folio", "fecha", "subtotal", "iva", "total", "medio", "rfc"):
        assert campo in fila
    assert fila["folio"] == v.folio
    assert fila["iva"] == "16.00"
    assert fila["total"] == "116.00"
    # La venta queda marcada como exportada (AT-8.2).
    db.refresh(v)
    assert v.exportada_fiscal is True


def test_export_csv_tiene_encabezado(db, turno, make_producto):
    _vender(db, turno, make_producto, "CSV", "10.00")
    desde, hasta = _rango_amplio()
    exp = fiscal_export.generar_export(db, desde, hasta)
    db.commit()
    csv_text = fiscal_export.a_csv(exp)
    assert csv_text.splitlines()[0] == "folio,fecha,subtotal,iva,total,medio,rfc"


def test_http_reportes_y_export(op_client, make_producto, db, turno):
    _vender(db, turno, make_producto, "H1", "100.00")
    r = op_client.get("/reportes?periodo=hoy")
    assert r.status_code == 200 and "Ticket promedio" in r.text
    r2 = op_client.get("/reportes/export?periodo=mes")
    assert r2.status_code == 200
    assert r2.headers["content-type"].startswith("text/csv")
    assert "XAXX010101000" in r2.text


def test_export_fiscal_solo_admin(basic_client):
    # Restricción silenciosa: el cajero no-admin no puede exportar (403).
    assert basic_client.get("/reportes/export?periodo=mes").status_code == 403


def test_cajero_ve_solo_su_turno_sin_controles(basic_client):
    # El cajero entra a Reportes pero ve SOLO su turno actual, sin controles.
    r = basic_client.get("/reportes")
    assert r.status_code == 200
    assert "Generar Reporte" not in r.text and "Consultar" not in r.text
    assert "turno actual" in r.text


def test_admin_ve_boton_generar_reporte(op_client):
    r = op_client.get("/reportes?periodo=hoy")
    assert r.status_code == 200 and "Generar Reporte" in r.text


def test_reportes_rango_de_fechas(op_client, make_producto, db, turno):
    _vender(db, turno, make_producto, "RG1", "100.00")
    r = op_client.get("/reportes?desde=2026-06-01&hasta=2026-06-30")
    assert r.status_code == 200
    assert "Rango: 2026-06-01" in r.text  # el rango personalizado se refleja
    # Export con el mismo rango (admin).
    r2 = op_client.get("/reportes/export?desde=2026-06-01&hasta=2026-06-30")
    assert r2.status_code == 200 and r2.headers["content-type"].startswith("text/csv")
