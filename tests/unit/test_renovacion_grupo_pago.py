"""
Tests unitarios del recálculo de grupo de pago y atomicidad en renovación de contratos.
Cubre Spec §FR-004, §FR-005, §FR-006, §FR-008, §FR-012 (T006, T019).
"""

import unittest
from unittest.mock import MagicMock, patch
from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.aplicacion.servicios.servicio_contrato_mandato import (
    ServicioContratoMandato,
)
from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.excepciones.excepciones_base import ContratoNoRenovableError


class TestRenovacionGrupoPago(unittest.TestCase):
    """Pruebas unitarias con mocks para renovación de arriendo y mandato."""

    def setUp(self) -> None:
        # Repositorios mock para arrendamiento
        self.repo_arriendo = MagicMock()
        self.repo_propiedad = MagicMock()
        self.repo_renovacion = MagicMock()
        self.repo_ipc = MagicMock()
        self.repo_mandato = MagicMock()

        # Mock db transaction para arriendo
        self.mock_db = MagicMock()
        self.mock_db.transaccion.return_value.__enter__ = MagicMock()
        # __exit__ debe retornar falsy para NO suprimir excepciones del bloque
        self.mock_db.transaccion.return_value.__exit__ = MagicMock(return_value=False)
        self.repo_arriendo.db = self.mock_db
        self.repo_mandato.db = self.mock_db

        self.servicio_arriendo = ServicioContratoArrendamiento(
            repo_arriendo=self.repo_arriendo,
            repo_propiedad=self.repo_propiedad,
            repo_renovacion=self.repo_renovacion,
            repo_ipc=self.repo_ipc,
            repo_mandato=self.repo_mandato,
        )

        self.servicio_mandato = ServicioContratoMandato(
            repo_mandato=self.repo_mandato,
            repo_propiedad=self.repo_propiedad,
            repo_renovacion=self.repo_renovacion,
        )

    def test_renovacion_arrendamiento_recalcula_grupo_y_fecha_pago(self) -> None:
        """
        FR-004: Al renovar arriendo, grupo_operativo y fecha_pago se recalculan
        a partir de fecha_inicio_renovacion (fecha_fin_original + 1 día).
        Si fecha_fin_original es 2026-05-17 -> fecha_inicio_renovacion es 2026-05-18.
        Día 18 corresponde a Grupo 3, y día exacto de pago es 18.
        """
        arriendo = ContratoArrendamiento(
            id_contrato_a=1,
            id_propiedad=100,
            estado_contrato_a=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_a="2025-05-18",
            fecha_fin_contrato_a="2026-05-17",
            duracion_contrato_a=12,
            canon_arrendamiento=1500000,
            grupo_operativo=1,  # Grupo previo
            fecha_pago="5",  # Día previo
        )
        self.repo_arriendo.obtener_por_id.return_value = arriendo
        self.repo_ipc.obtener_ultimo.return_value = None
        self.repo_propiedad.obtener_por_id.return_value = None
        self.repo_mandato.obtener_activo_por_propiedad.return_value = None

        with patch.object(
            self.servicio_arriendo, "actualizar_canon_liquidaciones_futuras"
        ), patch.object(
            self.servicio_arriendo, "actualizar_valor_recaudos_futuros"
        ), patch.object(
            self.servicio_arriendo, "_invalidar_cache_propiedad"
        ), patch.object(
            self.servicio_arriendo, "_invalidar_cache_estado_cartera"
        ):
            self.servicio_arriendo.renovar_arrendamiento(1, "test_admin")

        # Verifica que se haya guardado con grupo 3 y fecha_pago "18"
        self.assertEqual(arriendo.grupo_operativo, 3)
        self.assertEqual(str(arriendo.fecha_pago), "18")
        self.repo_arriendo.actualizar.assert_called_once_with(arriendo, "test_admin")

    def test_renovacion_arrendamiento_sincroniza_mandato_activo(self) -> None:
        """
        FR-005: La renovación de un arrendamiento sincroniza el mandato activo de la
        misma propiedad, adoptando la fecha efectiva del período renovado.
        Si fecha_inicio_renovacion es 2026-05-18:
        Mandato adopta Grupo 3, día de pago mandato 30.
        """
        arriendo = ContratoArrendamiento(
            id_contrato_a=1,
            id_propiedad=100,
            estado_contrato_a=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_a="2025-05-18",
            fecha_fin_contrato_a="2026-05-17",
            duracion_contrato_a=12,
            canon_arrendamiento=1500000,
            grupo_operativo=2,
            fecha_pago="10",
        )
        mandato = ContratoMandato(
            id_contrato_m=2,
            id_propiedad=100,
            estado_contrato_m=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_m="2025-05-01",
            fecha_fin_contrato_m="2026-05-17",
            duracion_contrato_m=12,
            canon_mandato=1500000,
            grupo_operativo=1,  # previo
            fecha_pago="10",  # previo
        )
        self.repo_arriendo.obtener_por_id.return_value = arriendo
        self.repo_ipc.obtener_ultimo.return_value = None
        self.repo_propiedad.obtener_por_id.return_value = None
        self.repo_mandato.obtener_activo_por_propiedad.return_value = mandato

        with patch.object(
            self.servicio_arriendo, "actualizar_canon_liquidaciones_futuras"
        ), patch.object(
            self.servicio_arriendo, "actualizar_valor_recaudos_futuros"
        ), patch.object(
            self.servicio_arriendo, "_invalidar_cache_propiedad"
        ), patch.object(
            self.servicio_arriendo, "_invalidar_cache_estado_cartera"
        ):
            self.servicio_arriendo.renovar_arrendamiento(1, "test_admin")

        # Mandato debe tener grupo 3 y día 30
        self.assertEqual(mandato.grupo_operativo, 3)
        self.assertEqual(str(mandato.fecha_pago), "30")
        self.repo_mandato.actualizar.assert_called_once_with(mandato, "test_admin")

    def test_renovacion_arrendamiento_mismo_tramo_no_degrada_a_cero(self) -> None:
        """
        Spec §SC-001 / Acceptance Scenario 2:
        Cuando el nuevo período cae en el mismo tramo de grupo (ej: inicio día 28 -> Grupo 1),
        el grupo se mantiene correcto y NO se degrada ni queda en cero.
        """
        arriendo = ContratoArrendamiento(
            id_contrato_a=1,
            id_propiedad=100,
            estado_contrato_a=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_a="2025-05-28",
            fecha_fin_contrato_a="2026-05-27",  # fin 27 -> inicio ren 28 (G1)
            duracion_contrato_a=12,
            canon_arrendamiento=1500000,
            grupo_operativo=1,
            fecha_pago="28",
        )
        self.repo_arriendo.obtener_por_id.return_value = arriendo
        self.repo_ipc.obtener_ultimo.return_value = None
        self.repo_propiedad.obtener_por_id.return_value = None
        self.repo_mandato.obtener_activo_por_propiedad.return_value = None

        with patch.object(
            self.servicio_arriendo, "actualizar_canon_liquidaciones_futuras"
        ), patch.object(
            self.servicio_arriendo, "actualizar_valor_recaudos_futuros"
        ), patch.object(
            self.servicio_arriendo, "_invalidar_cache_propiedad"
        ), patch.object(
            self.servicio_arriendo, "_invalidar_cache_estado_cartera"
        ):
            self.servicio_arriendo.renovar_arrendamiento(1, "test_admin")

        self.assertEqual(arriendo.grupo_operativo, 1)
        self.assertEqual(str(arriendo.fecha_pago), "28")

    def test_renovacion_mandato_recalcula_grupo_y_fecha_pago(self) -> None:
        """
        FR-006: Al renovar un contrato de mandato directamente, se recalculan
        grupo_operativo y fecha_pago con la regla de mandato sobre fecha_inicio_renovacion.
        fecha_fin 2026-05-07 -> fecha_inicio_renovacion 2026-05-08 -> Grupo 2, día 20.
        """
        mandato = ContratoMandato(
            id_contrato_m=5,
            id_propiedad=101,
            estado_contrato_m=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_m="2025-05-08",
            fecha_fin_contrato_m="2026-05-07",
            duracion_contrato_m=12,
            canon_mandato=1200000,
            grupo_operativo=1,  # previo incorrecto
            fecha_pago="10",  # previo incorrecto
        )
        self.repo_mandato.obtener_por_id.return_value = mandato
        self.repo_propiedad.obtener_por_id.return_value = None

        with patch.object(self.servicio_mandato, "_invalidar_cache_estado_cartera"):
            self.servicio_mandato.renovar_mandato(5, "test_admin")

        self.assertEqual(mandato.grupo_operativo, 2)
        self.assertEqual(str(mandato.fecha_pago), "20")
        self.repo_mandato.actualizar.assert_called_once_with(mandato, "test_admin")

    def test_renovacion_mandato_usa_transaccion_gestionada(self) -> None:
        """
        FR-008, R3 (T019): renovar_mandato debe envolver las operaciones en db.transaccion().
        """
        mandato = ContratoMandato(
            id_contrato_m=5,
            id_propiedad=101,
            estado_contrato_m=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_m="2025-05-08",
            fecha_fin_contrato_m="2026-05-07",
            duracion_contrato_m=12,
            canon_mandato=1200000,
        )
        self.repo_mandato.obtener_por_id.return_value = mandato
        self.repo_propiedad.obtener_por_id.return_value = None

        with patch.object(self.servicio_mandato, "_invalidar_cache_estado_cartera"):
            self.servicio_mandato.renovar_mandato(5, "test_admin")

        # Verifica que se haya abierto la transacción
        self.mock_db.transaccion.assert_called()

    def test_actualizacion_fecha_inicio_recalcula_grupo_v2_y_dia_exacto(
        self,
    ) -> None:
        """
        FR-003 (T008): al editar fecha_inicio del arriendo, el grupo se unifica
        a tramos V2 y el día de pago es el día exacto de la fecha.
        Nueva fecha_inicio 2025-11-20 -> Grupo 3 y fecha_pago "20".
        El mandato en cascada queda con Grupo 3 y fecha_pago "30" (regla mandato).
        """
        arriendo = ContratoArrendamiento(
            id_contrato_a=7,
            id_propiedad=300,
            estado_contrato_a=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_a="2025-11-05",
            fecha_fin_contrato_a="2026-11-19",
            duracion_contrato_a=12,
            canon_arrendamiento=1200000,
            grupo_operativo=1,
            fecha_pago="5",
        )
        self.repo_arriendo.obtener_por_id.return_value = arriendo
        mandato = MagicMock()
        self.repo_mandato.obtener_activo_por_propiedad.return_value = mandato

        self.servicio_arriendo.actualizar_arrendamiento(
            7, {"fecha_inicio": "2025-11-20"}, "test_admin"
        )

        self.assertEqual(arriendo.grupo_operativo, 3)
        self.assertEqual(arriendo.fecha_pago, "20")
        self.repo_arriendo.actualizar.assert_called_once_with(arriendo, "test_admin")
        self.assertEqual(mandato.grupo_operativo, 3)
        self.assertEqual(mandato.fecha_pago, "30")
        self.repo_mandato.actualizar.assert_called_once_with(mandato, "test_admin")

    def test_renovar_mandato_sin_db_ejecuta_directo(self) -> None:
        """
        Cobertura de la rama sin db_manager: con repo sin conexión gestionada,
        renovar_mandato ejecuta el flujo directo y persiste el grupo recalculado.
        """
        mandato = ContratoMandato(
            id_contrato_m=5,
            id_propiedad=101,
            estado_contrato_m=EstadoContrato.ACTIVO,
            fecha_inicio_contrato_m="2025-05-08",
            fecha_fin_contrato_m="2026-05-07",
            duracion_contrato_m=12,
            canon_mandato=1200000,
        )
        self.repo_mandato.obtener_por_id.return_value = mandato
        self.repo_mandato.db = None
        self.repo_propiedad.obtener_por_id.return_value = None

        with patch.object(self.servicio_mandato, "_invalidar_cache_estado_cartera"):
            resultado = self.servicio_mandato.renovar_mandato(5, "test_admin")

        self.assertEqual(resultado.grupo_operativo, 2)
        self.assertEqual(str(resultado.fecha_pago), "20")
        self.repo_mandato.actualizar.assert_called_once_with(mandato, "test_admin")

    def test_renovar_mandato_no_activo_lanza_contrato_no_renovable(self) -> None:
        """
        FR-006: un mandato no ACTIVO no es renovable; no se toca grupo ni persistencia.
        """
        mandato = ContratoMandato(
            id_contrato_m=5,
            id_propiedad=101,
            estado_contrato_m=EstadoContrato.FINALIZADO,
        )
        self.repo_mandato.obtener_por_id.return_value = mandato

        with self.assertRaises(ContratoNoRenovableError):
            with patch.object(self.servicio_mandato, "_invalidar_cache_estado_cartera"):
                self.servicio_mandato.renovar_mandato(5, "test_admin")

        self.repo_renovacion.crear.assert_not_called()
        self.repo_mandato.actualizar.assert_not_called()
