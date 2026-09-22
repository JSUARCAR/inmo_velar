"""
Tests unitarios del helper `_calcular_incremento_ipc` (T007, US1).

Cubre los 7 casos del set SC-001 referentes al IPC:
1. duración >= 12 meses con IPC vigente -> incremento
2. duración < 12 meses -> 0%
3. sin valor IPC registrado -> 0%
4. renovación consecutiva (canon ya incrementado en el contrato)
5. borde 31-Dic (fecha_inicio_renovacion = 01-Ene)
6. borde 28-Feb en año bisiesto
7. sin mandato activo: la renovación continúa sin error
"""

import unittest
from unittest.mock import MagicMock

from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.ipc import IPC
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos


def _crear_servicio(**kwargs):
    """Construye el servicio con repositorios mock configurados."""
    repos = {
        "repo_arriendo": MagicMock(),
        "repo_propiedad": MagicMock(),
        "repo_renovacion": MagicMock(),
        "repo_ipc": MagicMock(),
        "repo_mandato": MagicMock(),
    }
    for nombre, valor in kwargs.items():
        if nombre in repos:
            repos[nombre] = valor
    return ServicioContratoArrendamiento(**repos)


class TestCalcularIncrementoIPC(unittest.TestCase):
    def test_duracion_doce_meses_con_ipc_vigente(self):
        """Caso 1: >= 12 meses e IPC vigente -> retorna el valor del IPC."""
        servicio = _crear_servicio()
        contrato = ContratoArrendamiento(id_contrato_a=1, duracion_contrato_a=12)
        ipc_actual = IPC(anio=2025, valor_ipc=10.0)

        resultado = servicio._calcular_incremento_ipc(contrato, ipc_actual)

        self.assertEqual(resultado, 10.0)

    def test_duracion_menor_a_doce_meses(self):
        """Caso 2: duración < 12 meses -> 0.0 aunque exista IPC."""
        servicio = _crear_servicio()
        contrato = ContratoArrendamiento(id_contrato_a=1, duracion_contrato_a=6)
        ipc_actual = IPC(anio=2025, valor_ipc=10.0)

        resultado = servicio._calcular_incremento_ipc(contrato, ipc_actual)

        self.assertEqual(resultado, 0.0)

    def test_sin_valor_ipc_registrado(self):
        """Caso 3: sin IPC vigente -> 0.0 aunque la duración lo permita."""
        servicio = _crear_servicio()
        contrato = ContratoArrendamiento(id_contrato_a=1, duracion_contrato_a=12)

        resultado = servicio._calcular_incremento_ipc(contrato, None)

        self.assertEqual(resultado, 0.0)

    def test_renovacion_consecutiva_recalcula_sobre_canon_nuevo(self):
        """Caso 4: la cadena de canon se mantiene; la segunda renovación parte del canon ya incrementado."""
        servicio = _crear_servicio()
        ipc_actual = IPC(anio=2025, valor_ipc=10.0)

        contrato_primera = ContratoArrendamiento(
            id_contrato_a=1, canon_arrendamiento=1_000_000, duracion_contrato_a=12
        )
        incremento = servicio._calcular_incremento_ipc(contrato_primera, ipc_actual)
        canon_tras_primera = int(
            contrato_primera.canon_arrendamiento * (1 + incremento / 100)
        )

        contrato_segunda = ContratoArrendamiento(
            id_contrato_a=1,
            canon_arrendamiento=canon_tras_primera,
            duracion_contrato_a=12,
        )
        incremento_segunda = servicio._calcular_incremento_ipc(contrato_segunda, ipc_actual)
        canon_tras_segunda = int(canon_tras_primera * (1 + incremento_segunda / 100))

        self.assertEqual(canon_tras_primera, 1_100_000)
        self.assertEqual(canon_tras_segunda, 1_210_000)

    def test_borde_31_diciembre(self):
        """Caso 5: fecha_fin_original 2026-12-31 -> fecha_inicio_renovacion 2027-01-01."""
        resultado = CalculadoraContratos.calcular_fecha_inicio_renovacion(
            "2026-12-31"
        )
        self.assertEqual(resultado, "2027-01-01")

    def test_borde_28_febrero_bisiesto(self):
        """Caso 6: 2028-02-28 (bisiesto) -> fecha_inicio_renovacion 2028-02-29."""
        resultado = CalculadoraContratos.calcular_fecha_inicio_renovacion(
            "2028-02-28"
        )
        self.assertEqual(resultado, "2028-02-29")

    def test_sin_mandato_activo_la_renovacion_continua(self):
        """Caso 7: sin mandato activo la renovación continúa sin error (FR-009)."""
        repo_mandato = MagicMock()
        repo_mandato.obtener_activo_por_propiedad.return_value = None
        repo_arriendo = MagicMock(db=None)
        contrato_actual = ContratoArrendamiento(
            id_contrato_a=1,
            id_propiedad=5,
            fecha_inicio_contrato_a="2025-01-01",
            fecha_fin_contrato_a="2025-12-31",
            duracion_contrato_a=12,
            canon_arrendamiento=1_000_000,
            estado_contrato_a="ACTIVO",
        )
        repo_arriendo.obtener_por_id.return_value = contrato_actual

        servicio = _crear_servicio(
            repo_arriendo=repo_arriendo,
            repo_mandato=repo_mandato,
        )
        servicio.repo_ipc = MagicMock()
        servicio.repo_ipc.obtener_ultimo.return_value = None

        try:
            renovado = servicio._ejecutar_renovacion_arrendamiento(1, "test_user")
        except Exception as exc:  # noqa: BLE001
            self.fail(f"No debería lanzarse excepción: {exc}")

        self.assertEqual(renovado.canon_arrendamiento, 1_000_000)
        repo_mandato.obtener_activo_por_propiedad.assert_called_once_with(5)


if __name__ == "__main__":
    unittest.main()