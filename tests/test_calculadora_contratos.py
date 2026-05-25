import pytest
from datetime import date
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

class TestCalculadoraContratos:

    # Mandato - Grupo 1 (1-10 -> 10)
    def test_mandato_g1_dia_1(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 1)) == 10

    def test_mandato_g1_dia_5(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 5)) == 10

    def test_mandato_g1_dia_10(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 10)) == 10

    # Mandato - Grupo 2 (11-20 -> 20)
    def test_mandato_g2_dia_11(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 11)) == 20

    def test_mandato_g2_dia_15(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 15)) == 20

    def test_mandato_g2_dia_20(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 20)) == 20

    # Mandato - Grupo 3 (21-31 -> -1 = último día del mes)
    def test_mandato_g3_dia_21(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 21)) == -1

    def test_mandato_g3_dia_25(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 25)) == -1

    def test_mandato_g3_dia_31(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 31)) == -1

    # resolver_dia_pago_real
    def test_resolver_g1(self):
        assert CalculadoraContratos.resolver_dia_pago_real(10, 1, 1, 2026) == 10

    def test_resolver_g2(self):
        assert CalculadoraContratos.resolver_dia_pago_real(20, 2, 1, 2026) == 20

    def test_resolver_g3_enero(self):
        assert CalculadoraContratos.resolver_dia_pago_real(-1, 3, 1, 2026) == 31

    def test_resolver_g3_febrero_no_bisiesto(self):
        assert CalculadoraContratos.resolver_dia_pago_real(-1, 3, 2, 2023) == 28

    def test_resolver_g3_febrero_bisiesto(self):
        assert CalculadoraContratos.resolver_dia_pago_real(-1, 3, 2, 2024) == 29

    def test_resolver_g3_abril(self):
        assert CalculadoraContratos.resolver_dia_pago_real(-1, 3, 4, 2026) == 30

    # Arrendamiento
    def test_arrendamiento_dia_1(self):
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento(date(2026, 6, 1)) == 1

    def test_arrendamiento_dia_15(self):
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento(date(2026, 6, 15)) == 15

    def test_arrendamiento_dia_31(self):
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento(date(2026, 5, 31)) == 31

    # sumar_meses (DRY)
    def test_sumar_meses_normal(self):
        assert CalculadoraContratos.sumar_meses(date(2026, 1, 15), 2) == date(2026, 3, 15)

    def test_sumar_meses_31_a_febrero(self):
        assert CalculadoraContratos.sumar_meses(date(2026, 1, 31), 1) == date(2026, 2, 28)
