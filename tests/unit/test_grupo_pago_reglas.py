"""
Tests unitarios para las reglas de grupo y día de pago V2 (CalculadoraContratos).
Verifica la regla unificada de dominio según Spec §FR-001..FR-003 y contracts/contratos-dominio.md.
"""

from datetime import date
import pytest
from src.dominio.servicios.calculadora_contratos import (
    CalculadoraContratos,
    DIA_CORTE_GRUPO_1_INICIO,
    DIA_CORTE_GRUPO_1_FIN,
    DIA_CORTE_GRUPO_2_INICIO,
    DIA_CORTE_GRUPO_2_FIN,
    DIA_CORTE_GRUPO_3_INICIO,
    DIA_CORTE_GRUPO_3_FIN,
    DIA_PAGO_MANDATO_GRUPO_1,
    DIA_PAGO_MANDATO_GRUPO_2,
    DIA_PAGO_MANDATO_GRUPO_3,
)


class TestGrupoPagoReglasV2:
    """Pruebas de la regla unificada V2 de grupos y días de pago."""

    def test_constantes_definidas(self) -> None:
        """Verifica que las constantes de tramos y días de pago existan sin magic numbers."""
        assert DIA_CORTE_GRUPO_1_INICIO == 28
        assert DIA_CORTE_GRUPO_1_FIN == 7
        assert DIA_CORTE_GRUPO_2_INICIO == 8
        assert DIA_CORTE_GRUPO_2_FIN == 17
        assert DIA_CORTE_GRUPO_3_INICIO == 18
        assert DIA_CORTE_GRUPO_3_FIN == 27

        assert DIA_PAGO_MANDATO_GRUPO_1 == 10
        assert DIA_PAGO_MANDATO_GRUPO_2 == 20
        assert DIA_PAGO_MANDATO_GRUPO_3 == 30

    @pytest.mark.parametrize(
        "dia,grupo_esperado,dia_mandato_esperado",
        [
            # Grupo 1 (Tramo 28 al 7)
            (1, 1, 10),
            (2, 1, 10),
            (6, 1, 10),
            (7, 1, 10),
            (28, 1, 10),
            (29, 1, 10),
            (30, 1, 10),
            (31, 1, 10),
            # Grupo 2 (Tramo 8 al 17)
            (8, 2, 20),
            (9, 2, 20),
            (12, 2, 20),
            (16, 2, 20),
            (17, 2, 20),
            # Grupo 3 (Tramo 18 al 27)
            (18, 3, 30),
            (19, 3, 30),
            (22, 3, 30),
            (26, 3, 30),
            (27, 3, 30),
        ],
    )
    def test_tabla_de_verdad_tramos_v2(
        self, dia: int, grupo_esperado: int, dia_mandato_esperado: int
    ) -> None:
        """Verifica la tabla de verdad completa para cada día del mes (1..31)."""
        # Usamos un mes de 31 días como enero
        fecha_obj = date(2026, 1, dia)
        fecha_str = f"2026-01-{dia:02d}"

        # Test calcular_grupo_operativo
        assert (
            CalculadoraContratos.calcular_grupo_operativo(fecha_obj) == grupo_esperado
        )
        assert (
            CalculadoraContratos.calcular_grupo_operativo(fecha_str) == grupo_esperado
        )

        # Test calcular_dia_pago_mandato
        assert (
            CalculadoraContratos.calcular_dia_pago_mandato(fecha_obj)
            == dia_mandato_esperado
        )
        assert (
            CalculadoraContratos.calcular_dia_pago_mandato(fecha_str)
            == dia_mandato_esperado
        )

        # Test calcular_dia_pago_arrendamiento (día exacto)
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento(fecha_obj) == dia
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento(fecha_str) == dia

        # Test delegación calcular_ciclo_pago_mandato
        ciclo = CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_obj)
        assert ciclo == (grupo_esperado, dia_mandato_esperado)

    def test_bordes_transicion_criticos(self) -> None:
        """Verifica exactamente los bordes de transición: 7/8, 17/18, 27/28, 1 y 31."""
        # Borde 7 -> G1, 8 -> G2
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-07") == 1
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-08") == 2
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-07") == 10
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-08") == 20

        # Borde 17 -> G2, 18 -> G3
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-17") == 2
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-18") == 3
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-17") == 20
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-18") == 30

        # Borde 27 -> G3, 28 -> G1
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-27") == 3
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-28") == 1
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-27") == 30
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-28") == 10

        # Borde 1 y 31 -> G1
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-01") == 1
        assert CalculadoraContratos.calcular_grupo_operativo("2026-05-31") == 1
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-01") == 10
        assert CalculadoraContratos.calcular_dia_pago_mandato("2026-05-31") == 10

    def test_febrero_bisiesto_y_cambio_anio(self) -> None:
        """Verifica comportamiento en fin de febrero (bisiesto y no bisiesto) y cambio de año."""
        # 28 feb no bisiesto (2025) y bisiesto (2024-02-29)
        assert CalculadoraContratos.calcular_grupo_operativo("2025-02-28") == 1
        assert CalculadoraContratos.calcular_dia_pago_mandato("2025-02-28") == 10
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento("2025-02-28") == 28

        assert CalculadoraContratos.calcular_grupo_operativo("2024-02-29") == 1
        assert CalculadoraContratos.calcular_dia_pago_mandato("2024-02-29") == 10
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento("2024-02-29") == 29

        # Cambio de año 31-dic a 01-ene
        assert CalculadoraContratos.calcular_grupo_operativo("2026-12-31") == 1
        assert CalculadoraContratos.calcular_grupo_operativo("2027-01-01") == 1
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento("2026-12-31") == 31
        assert CalculadoraContratos.calcular_dia_pago_arrendamiento("2027-01-01") == 1

    def test_formato_invalido_lanza_value_error(self) -> None:
        """Verifica que fechas inválidas propagan ValueError."""
        with pytest.raises(ValueError):
            CalculadoraContratos.calcular_grupo_operativo("fecha-invalida")
        with pytest.raises(ValueError):
            CalculadoraContratos.calcular_dia_pago_mandato("2026-13-45")
        with pytest.raises(ValueError):
            CalculadoraContratos.calcular_dia_pago_arrendamiento("abc")
