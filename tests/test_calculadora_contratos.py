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
        # En V2, el 10 pertenece a G2, y se paga el 20
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 10)) == 20

    def test_mandato_g2_dia_11(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 11)) == 20

    def test_mandato_g2_dia_15(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 15)) == 20

    def test_mandato_g2_dia_20(self):
        # En V2, el 20 pertenece a G3, y se paga el 30
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 20)) == 30

    def test_mandato_g3_dia_21(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 21)) == 30

    def test_mandato_g3_dia_25(self):
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 25)) == 30

    def test_mandato_g3_dia_31(self):
        # En V2, el 31 pertenece a G1, y se paga el 10
        assert CalculadoraContratos.calcular_dia_pago_mandato(date(2026, 1, 31)) == 10

    def test_resolver_g1(self):
        # 10 de Marzo de 2026 es Martes, día hábil
        assert CalculadoraContratos.resolver_dia_pago_real(10, 1, 3, 2026) == 10

    def test_resolver_g2(self):
        # 20 de Abril de 2026 es Lunes, día hábil
        assert CalculadoraContratos.resolver_dia_pago_real(20, 2, 4, 2026) == 20

    def test_resolver_g3_enero(self):
        # 30 de Enero de 2026 es Viernes, día hábil. En V2 ya no es -1, pasamos explícitamente 30
        assert CalculadoraContratos.resolver_dia_pago_real(30, 3, 1, 2026) == 30

    def test_resolver_g3_febrero_no_bisiesto(self):
        # 2026 no bisiesto, 30 -> 28
        # Febrero 28 de 2026 es Sabado -> se mueve a Lunes 2 de Marzo (Día 2)
        assert CalculadoraContratos.resolver_dia_pago_real(30, 3, 2, 2026) == 2

    def test_resolver_g3_febrero_bisiesto(self):
        # 2024 bisiesto, 30 -> 29
        # Febrero 29 de 2024 es Jueves, día hábil
        assert CalculadoraContratos.resolver_dia_pago_real(30, 3, 2, 2024) == 29

    def test_resolver_g3_abril(self):
        # 30 de Abril 2026 es Jueves
        assert CalculadoraContratos.resolver_dia_pago_real(30, 3, 4, 2026) == 30

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

    # calcular_duracion_meses
    def test_duracion_meses_exactos(self):
        # 1-Ene a 31-Dic = 12 meses
        assert CalculadoraContratos.calcular_duracion_meses(date(2026, 1, 1), date(2026, 12, 31)) == 12

    def test_duracion_meses_mitad_mes(self):
        # 15-Ene a 14-Feb = 1 mes
        assert CalculadoraContratos.calcular_duracion_meses(date(2026, 1, 15), date(2026, 2, 14)) == 1

    def test_duracion_meses_incompleto(self):
        # 15-Ene a 10-Feb = 0 meses
        assert CalculadoraContratos.calcular_duracion_meses(date(2026, 1, 15), date(2026, 2, 10)) == 0

    def test_duracion_meses_bisiesto(self):
        # 1-Feb a 29-Feb = 1 mes en año bisiesto
        assert CalculadoraContratos.calcular_duracion_meses(date(2024, 2, 1), date(2024, 2, 29)) == 1
        
    def test_duracion_meses_varios_anios(self):
        # 1-Ene-2024 a 31-Dic-2025 = 24 meses
        assert CalculadoraContratos.calcular_duracion_meses(date(2024, 1, 1), date(2025, 12, 31)) == 24

    # validar_coherencia
    def test_validar_coherencia_correcta(self):
        valido, msg = CalculadoraContratos.validar_coherencia(date(2026, 1, 1), date(2026, 12, 31), 12)
        assert valido is True
        
    def test_validar_coherencia_incorrecta(self):
        valido, msg = CalculadoraContratos.validar_coherencia(date(2026, 1, 1), date(2026, 12, 31), 6)
        assert valido is False
        assert "discrepancia detectada" in msg.lower()
