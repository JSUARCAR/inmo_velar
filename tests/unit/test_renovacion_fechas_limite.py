"""
T020 [US3]: Fechas límite — E5 de quickstart.md.

Verifica `calcular_fecha_inicio_renovacion` (+1 día) y `sumar_meses`
en bordes: 31-Dic→01-Ene, 28-Feb bisiesto, 31-Ene→28/29-Feb, 30-Nov→31-Dic.
"""

import pytest

from src.dominio.servicios.calculadora_contratos import CalculadoraContratos


class TestCalcularFechaInicioRenovacion:
    def test_31_dic_a_01_ene(self):
        assert (
            CalculadoraContratos.calcular_fecha_inicio_renovacion("2026-12-31")
            == "2027-01-01"
        )

    def test_28_feb_bisiesto_a_29_feb(self):
        assert (
            CalculadoraContratos.calcular_fecha_inicio_renovacion("2028-02-28")
            == "2028-02-29"
        )

    def test_fin_de_mes_comun(self):
        assert (
            CalculadoraContratos.calcular_fecha_inicio_renovacion("2024-01-31")
            == "2024-02-01"
        )

    def test_cadena_consecutiva(self):
        primera = CalculadoraContratos.calcular_fecha_inicio_renovacion("2025-12-31")
        segunda = CalculadoraContratos.calcular_fecha_inicio_renovacion("2026-12-31")
        assert primera == "2026-01-01"
        assert segunda == "2027-01-01"


class TestSumarMesesFechasLimite:
    def test_31_ene_a_28_feb_no_bisiesto(self):
        assert CalculadoraContratos.sumar_meses("2027-01-31", 1).isoformat() == "2027-02-28"

    def test_31_ene_a_29_feb_bisiesto(self):
        assert CalculadoraContratos.sumar_meses("2028-01-31", 1).isoformat() == "2028-02-29"

    def test_30_nov_a_31_dic(self):
        """Último día del mes origen → última fecha del mes destino (E5)."""
        assert CalculadoraContratos.sumar_meses("2026-11-30", 1).isoformat() == "2026-12-31"

    def test_28_feb_no_bisiesto_fin_de_mes(self):
        assert CalculadoraContratos.sumar_meses("2027-02-28", 1).isoformat() == "2027-03-31"

    def test_31_dic_a_31_ene(self):
        assert CalculadoraContratos.sumar_meses("2026-12-31", 1).isoformat() == "2027-01-31"

    def test_transicion_bisiesto_con_duracion_12(self):
        """E5: fecha_fin 2028-02-29 + 12 meses -> última fecha del mes destino."""
        assert CalculadoraContratos.sumar_meses("2028-02-29", 12).isoformat() == "2029-02-28"

    def test_fecha_nunca_vacia(self):
        resultado = CalculadoraContratos.calcular_fecha_inicio_renovacion("2026-11-30")
        assert resultado != ""
        assert resultado == "2026-12-01"


class TestSumarMesesRamaTruncado:
    """T029: rama `except ValueError` de `sumar_meses` (Constitución §5, dominio 100%).

    Origen NO es fin-de-mes, pero el día no existe en el mes destino →
    se trunca al último día del mes destino.
    """

    def test_30_ene_a_28_feb_no_bisiesto(self):
        assert CalculadoraContratos.sumar_meses("2026-01-30", 1).isoformat() == "2026-02-28"

    def test_30_ene_a_29_feb_bisiesto(self):
        assert CalculadoraContratos.sumar_meses("2028-01-30", 1).isoformat() == "2028-02-29"

    def test_29_ene_a_28_feb_no_bisiesto(self):
        assert CalculadoraContratos.sumar_meses("2027-01-29", 1).isoformat() == "2027-02-28"

    def test_30_dic_mas_2_a_28_feb(self):
        """30-Dic (no último día) + 2 meses → 28-Feb (día 30 inválido en febrero)."""
        assert CalculadoraContratos.sumar_meses("2026-12-30", 2).isoformat() == "2027-02-28"