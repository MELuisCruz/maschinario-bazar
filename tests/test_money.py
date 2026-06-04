"""Tests de la base de cálculo monetario (ACCEPTANCE_TESTS AT-2.4, AT-2.5, AT-3.1).

Lógica pura, sin DB ni hardware. Modelo de IVA = incluido.
"""

from decimal import Decimal

import pytest

from app.services.money import (
    LineaCalc,
    cambio_efectivo,
    compute_totales,
    line_importe,
    q2,
)

D = Decimal


def test_q2_half_up():
    # Redondeo HALF_UP a 2 decimales (no banker's rounding).
    assert q2("1.005") == D("1.01")
    assert q2("2.675") == D("2.68")
    assert q2("0.124") == D("0.12")


def test_line_importe_basico():
    assert line_importe(D("2"), D("40.00")) == D("80.00")
    assert line_importe(D("1.5"), D("10.00")) == D("15.00")


def test_line_importe_con_descuento_y_piso_en_cero():
    assert line_importe(D("2"), D("40.00"), D("5.00")) == D("75.00")
    # El descuento no deja el importe negativo.
    assert line_importe(D("1"), D("10.00"), D("50.00")) == D("0.00")


def test_at_2_4_iva_incluido_identidad():
    # Precio al público con IVA incluido: total 116 → base 100, IVA 16.
    t = compute_totales([LineaCalc(D("1"), D("116.00"))])
    assert t.total == D("116.00")
    assert t.subtotal == D("100.00")
    assert t.iva_total == D("16.00")
    # Identidad del desglose AT-2.4: subtotal + IVA = total.
    assert t.subtotal + t.iva_total == t.total


def test_at_2_5_descuento_recalcula_totales():
    # Dos líneas: 116 + 58 = 174; descuento global de 24 → total 150.
    lineas = [LineaCalc(D("1"), D("116.00")), LineaCalc(D("1"), D("58.00"))]
    t = compute_totales(lineas, descuento_global=D("24.00"))
    assert t.total == D("150.00")
    assert t.descuento_total == D("24.00")
    assert t.subtotal + t.iva_total == t.total


def test_descuento_global_topado_no_deja_total_negativo():
    t = compute_totales([LineaCalc(D("1"), D("50.00"))], descuento_global=D("999.00"))
    assert t.total == D("0.00")
    assert t.iva_total == D("0.00")


def test_descuento_por_linea_se_suma_al_total():
    t = compute_totales([LineaCalc(D("2"), D("40.00"), D("5.00"))])
    # importe línea = 80 - 5 = 75
    assert t.total == D("75.00")
    assert t.descuento_total == D("5.00")


def test_at_3_1_cambio_efectivo():
    assert cambio_efectivo(D("179.80"), D("200.00")) == D("20.20")
    assert cambio_efectivo(D("100.00"), D("100.00")) == D("0.00")


@pytest.mark.parametrize(
    "precio,base,iva",
    [
        (D("11.60"), D("10.00"), D("1.60")),
        (D("99.99"), D("86.20"), D("13.79")),
        (D("1.00"), D("0.86"), D("0.14")),
    ],
)
def test_iva_incluido_varios(precio, base, iva):
    t = compute_totales([LineaCalc(D("1"), precio)])
    assert t.subtotal == base
    assert t.iva_total == iva
    assert t.subtotal + t.iva_total == t.total
