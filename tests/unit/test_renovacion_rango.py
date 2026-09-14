"""
Tests unitarios: validación previa de rangos en renovación (T006, T012).

Gate en dos niveles (spec 073, FR-003):
  1. Máximos operativos (canon ≤ $10.000.000, comisión ≤ 1500).
  2. Límite int4 (2.147.483.647) como red de seguridad para derivados.

El mensaje operativo indica campo + valor, sin tecnicismos.
"""

import pytest

from src.aplicacion.utils.validadores import (
    validar_canon,
    validar_comision,
    validar_derivado,
)
from src.dominio.excepciones.excepciones_base import ValorFueraDeRangoError


def test_canon_dentro_de_rango_no_lanza():
    validar_canon(2_300_000)
    validar_canon(10_000_000)


def test_canon_sobre_maximo_operativo_lanza_con_campo_y_valor():
    with pytest.raises(ValorFueraDeRangoError) as exc_info:
        validar_canon(10_000_001)
    mensaje = str(exc_info.value)
    assert "canon" in mensaje.lower()
    assert "10000001" in mensaje


def test_comision_limite_y_sobre_limite():
    validar_comision(1500)
    with pytest.raises(ValorFueraDeRangoError) as exc_info:
        validar_comision(1501)
    assert "1501" in str(exc_info.value)


def test_derivado_en_rango_int4_no_lanza():
    validar_derivado("comision_monto", 230_000)
    validar_derivado("comision_monto", 2_147_483_647)


def test_derivado_sobre_int4_lanza():
    with pytest.raises(ValorFueraDeRangoError) as exc_info:
        validar_derivado("comision_monto", 2_147_483_648)
    mensaje = str(exc_info.value)
    assert "comision_monto" in mensaje
    assert "2147483648" in mensaje


def test_mensaje_operativo_sin_tecnicismos():
    with pytest.raises(ValorFueraDeRangoError) as exc_info:
        validar_canon(99_000_000)
    mensaje = str(exc_info.value).lower()
    assert "integer" not in mensaje
    assert "out of range" not in mensaje
    assert "psycopg2" not in mensaje
    assert "traceback" not in mensaje
