"""
Tests unitarios para servicios de Propiedad Horizontal.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestServicioAsistenciasAsambleas:
    """Tests para el servicio de Asistencias a Asambleas."""

    def test_crear_asistencia_validacion_campos_requeridos(self):
        """Test: Validar campos requeridos en crear_asistencia."""
        from src.aplicacion.servicios.servicio_asistencias_asambleas import (
            ServicioAsistenciasAsambleas,
        )

        mock_repo_asistencia = MagicMock()
        mock_repo_propiedad = MagicMock()

        servicio = ServicioAsistenciasAsambleas(
            mock_repo_asistencia, mock_repo_propiedad
        )

        # Test con diccionario vacío - debe lanzar ValueError
        with pytest.raises(ValueError, match="Campo requerido"):
            servicio.crear_asistencia({}, "admin")

    def test_crear_asistencia_falta_fecha(self):
        """Test: Validar que fecha es requerida."""
        from src.aplicacion.servicios.servicio_asistencias_asambleas import (
            ServicioAsistenciasAsambleas,
        )

        mock_repo_asistencia = MagicMock()
        mock_repo_propiedad = MagicMock()

        servicio = ServicioAsistenciasAsambleas(
            mock_repo_asistencia, mock_repo_propiedad
        )

        datos_incompletos = {
            "id_propiedad": 1,
            "fecha_asistencia": "",
            "hora_asistencia": "14:00",
            "tipo_reunion": "Ordinaria",
            "tipo_asistente": "Propietario",
            "direccion_asistencia": "Calle 123",
        }

        with pytest.raises(ValueError, match="fecha_asistencia"):
            servicio.crear_asistencia(datos_incompletos, "admin")

    def test_crear_asistencia_exitoso(self):
        """Test: Crear asistencia con datos válidos."""
        from src.aplicacion.servicios.servicio_asistencias_asambleas import (
            ServicioAsistenciasAsambleas,
        )
        from src.dominio.entidades.asistencia_asambleas import AsistenciaAsambleas

        mock_repo_asistencia = MagicMock()
        mock_repo_propiedad = MagicMock()
        mock_repo_propiedad.obtener_info_completa_contrato.return_value = {
            "id_propietario": 1,
            "id_asesor": 2,
        }
        mock_repo_asistencia.crear.return_value = AsistenciaAsambleas(
            id_asistencia=1,
            id_propiedad=1,
        )

        servicio = ServicioAsistenciasAsambleas(
            mock_repo_asistencia, mock_repo_propiedad
        )

        datos_validos = {
            "id_propiedad": 1,
            "fecha_asistencia": "2026-04-15",
            "hora_asistencia": "14:00",
            "tipo_reunion": "Ordinaria",
            "tipo_asistente": "Propietario",
            "direccion_asistencia": "Calle 123",
        }

        resultado = servicio.crear_asistencia(datos_validos, "admin")

        assert resultado.id_propiedad == 1
        mock_repo_propiedad.obtener_info_completa_contrato.assert_called_once_with(1)


class TestServicioPagosAdministracion:
    """Tests para el servicio de Pagos de Administración."""

    def test_generar_pagos_sin_propiedades(self):
        """Test: Generar pagos cuando no hay propiedades."""
        from src.aplicacion.servicios.servicio_pagos_administracion import (
            ServicioPagosAdministracion,
        )

        mock_repo = MagicMock()
        mock_repo.obtener_elegibles.return_value = []

        servicio = ServicioPagosAdministracion(mock_repo)

        resultado = servicio.generar_pagos_mes("2026-04", "admin")

        assert resultado["exitosos"] == 0
        assert resultado["fallidos"] == 0

    def test_listar_pagos_con_filtros(self):
        """Test: Listar pagos con filtros."""
        from src.aplicacion.servicios.servicio_pagos_administracion import (
            ServicioPagosAdministracion,
        )

        mock_repo = MagicMock()
        mock_repo.listar.return_value = []

        servicio = ServicioPagosAdministracion(mock_repo)

        servicio.listar_pagos(filtro_periodo="2026-04", filtro_estado="Pendiente")

        mock_repo.listar.assert_called_once_with(
            filtro_periodo="2026-04",
            filtro_estado="Pendiente",
            filtro_propiedad=None,
            filtro_nombre=None,
        )
