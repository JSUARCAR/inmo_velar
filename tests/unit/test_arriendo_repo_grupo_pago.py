"""
Tests unitarios para el repositorio de contrato de arrendamiento.
Verifica que _row_to_entity mapee fielmente la columna GRUPO_OPERATIVO (Spec §FR-007).
"""

from unittest.mock import MagicMock
import pytest
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
    RepositorioContratoArrendamientoPostgres,
)


class TestArriendoRepoGrupoPago:
    """Verifica el mapeo de persistencia de GRUPO_OPERATIVO en contratos de arrendamiento."""

    @pytest.fixture
    def repo(self) -> RepositorioContratoArrendamientoPostgres:
        mock_db = MagicMock()
        return RepositorioContratoArrendamientoPostgres(db_manager=mock_db)

    def test_row_to_entity_mapea_grupo_operativo_mayusculas(
        self, repo: RepositorioContratoArrendamientoPostgres
    ) -> None:
        """Verifica que _row_to_entity extraiga GRUPO_OPERATIVO en mayúsculas."""
        row = {
            "ID_CONTRATO_A": 10,
            "ID_PROPIEDAD": 20,
            "ID_ARRENDATARIO": 30,
            "FECHA_INICIO_CONTRATO_A": "2026-01-01",
            "FECHA_FIN_CONTRATO_A": "2026-12-31",
            "CANON_ARRENDAMIENTO": 1500000,
            "FECHA_PAGO": "1",
            "GRUPO_OPERATIVO": 1,
            "ESTADO_CONTRATO_A": "ACTIVO",
        }
        entidad = repo._row_to_entity(row)
        assert entidad is not None
        assert entidad.grupo_operativo == 1
        assert entidad.fecha_pago == "1"

    def test_row_to_entity_mapea_grupo_operativo_minusculas(
        self, repo: RepositorioContratoArrendamientoPostgres
    ) -> None:
        """Verifica que _row_to_entity extraiga grupo_operativo en minúsculas."""
        row = {
            "id_contrato_a": 11,
            "id_propiedad": 21,
            "id_arrendatario": 31,
            "fecha_inicio_contrato_a": "2026-02-15",
            "fecha_fin_contrato_a": "2027-02-14",
            "canon_arrendamiento": 2000000,
            "fecha_pago": "15",
            "grupo_operativo": 2,
            "estado_contrato_a": "ACTIVO",
        }
        entidad = repo._row_to_entity(row)
        assert entidad is not None
        assert entidad.grupo_operativo == 2
        assert entidad.fecha_pago == "15"

    def test_row_to_entity_grupo_operativo_nulo_o_ausente_default_cero(
        self, repo: RepositorioContratoArrendamientoPostgres
    ) -> None:
        """Verifica que si no viene GRUPO_OPERATIVO o es None, sea 0 por defecto."""
        row = {
            "ID_CONTRATO_A": 12,
            "ID_PROPIEDAD": 22,
            "ID_ARRENDATARIO": 32,
            "ESTADO_CONTRATO_A": "ACTIVO",
        }
        entidad = repo._row_to_entity(row)
        assert entidad is not None
        assert entidad.grupo_operativo == 0
