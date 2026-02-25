"""
Test Unitario: Crear Arrendamiento debe marcar la Propiedad como Ocupada
=========================================================================
Verifica que al crear un contrato de arrendamiento activo,
el servicio actualice disponibilidad_propiedad = 0 (Ocupada) en la BD.

Relación con la lógica inversa:
  terminar_arrendamiento → disponibilidad_propiedad = 1 (Disponible) ✅
  crear_arrendamiento    → disponibilidad_propiedad = 0 (Ocupada)    ✅ (fix)
"""

from unittest.mock import MagicMock, patch
import pytest

from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.propiedad import Propiedad


@pytest.fixture
def mocks():
    """Mocks de todos los repositorios necesarios."""
    repo_arriendo = MagicMock()
    repo_propiedad = MagicMock()
    repo_renovacion = MagicMock()
    repo_ipc = MagicMock()
    return repo_arriendo, repo_propiedad, repo_renovacion, repo_ipc


@pytest.fixture
def servicio(mocks):
    repo_arriendo, repo_propiedad, repo_renovacion, repo_ipc = mocks
    return ServicioContratoArrendamiento(
        repo_arriendo=repo_arriendo,
        repo_propiedad=repo_propiedad,
        repo_renovacion=repo_renovacion,
        repo_ipc=repo_ipc,
    )


def test_crear_arrendamiento_marca_propiedad_como_ocupada(servicio, mocks):
    """
    GIVEN una propiedad disponible y datos válidos para el contrato
    WHEN se llama a crear_arrendamiento()
    THEN la propiedad debe quedar con disponibilidad_propiedad = 0 (Ocupada)
    """
    repo_arriendo, repo_propiedad, repo_renovacion, repo_ipc = mocks

    # Arrange
    id_propiedad = 42
    propiedad_mock = Propiedad(
        id_propiedad=id_propiedad,
        matricula_inmobiliaria="MAT-001",
        direccion_propiedad="Calle 123",
        tipo_propiedad="Apartamento",
        disponibilidad_propiedad=1,  # Disponible inicialmente
    )

    contrato_creado_mock = MagicMock(spec=ContratoArrendamiento)
    contrato_creado_mock.id_contrato_a = 99

    # El repo no tiene arriendo activo previo
    repo_arriendo.obtener_activo_por_propiedad.return_value = None
    # El repo crea el contrato exitosamente
    repo_arriendo.crear.return_value = contrato_creado_mock
    # El repo devuelve la propiedad
    repo_propiedad.obtener_por_id.return_value = propiedad_mock

    datos = {
        "id_propiedad": id_propiedad,
        "id_arrendatario": 10,
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2027-03-01",
        "duracion_meses": 12,
        "canon": 1_500_000,
        "deposito": 0,
        "fecha_pago": 5,
    }

    # Act
    resultado = servicio.crear_arrendamiento(datos, usuario_sistema="admin")

    # Assert: la propiedad se consultó
    repo_propiedad.obtener_por_id.assert_called_once_with(id_propiedad)

    # Assert: la propiedad fue actualizada con disponibilidad = 0
    repo_propiedad.actualizar.assert_called_once()
    propiedad_actualizada: Propiedad = repo_propiedad.actualizar.call_args[0][0]
    assert propiedad_actualizada.disponibilidad_propiedad == 0, (
        f"Se esperaba disponibilidad_propiedad=0 (Ocupada), "
        f"pero fue: {propiedad_actualizada.disponibilidad_propiedad}"
    )

    # Assert: el contrato fue retornado correctamente
    assert resultado == contrato_creado_mock


def test_crear_arrendamiento_propiedad_no_encontrada_no_falla(servicio, mocks):
    """
    GIVEN que la propiedad no existe en BD (caso extremo)
    WHEN se llama a crear_arrendamiento()
    THEN no debe lanzar excepción y retorna el contrato igualmente
    """
    repo_arriendo, repo_propiedad, repo_renovacion, repo_ipc = mocks

    # Arrange
    repo_arriendo.obtener_activo_por_propiedad.return_value = None
    repo_arriendo.crear.return_value = MagicMock(spec=ContratoArrendamiento)
    repo_propiedad.obtener_por_id.return_value = None  # Propiedad no existe

    datos = {
        "id_propiedad": 999,
        "id_arrendatario": 10,
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2027-03-01",
        "duracion_meses": 12,
        "canon": 1_000_000,
        "deposito": 0,
        "fecha_pago": 5,
    }

    # Act - no debe lanzar
    resultado = servicio.crear_arrendamiento(datos, usuario_sistema="admin")

    # Assert: no se intentó actualizar porque la propiedad no existe
    repo_propiedad.actualizar.assert_not_called()
    assert resultado is not None
