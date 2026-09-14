"""T030 / FR-012: invalidación de caché post-commit, no bloqueante (quickstart E12.3).

Verifica que `invalidate_cache('cache_estado_cartera')` se invoca DESPUÉS del
commit exitoso de la renovación (arrendamiento y mandato) y que un fallo de la
invalidación NO aborta ni revierte la transacción: se tolera data obsoleta
temporal (consistencia eventual).
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.aplicacion.servicios.servicio_contrato_mandato import ServicioContratoMandato
from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.entidades.contrato_mandato import ContratoMandato

KEY_CACHE = "cache_estado_cartera"


class _TransaccionFake:
    """Context manager que registra el orden de inicio/commit."""

    def __init__(self, orden: list):
        self.orden = orden

    def __enter__(self):
        self.orden.append("inicio")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.orden.append("commit")
        return False


def _servicio_arriendo_con_db(orden: list) -> ServicioContratoArrendamiento:
    servicio = ServicioContratoArrendamiento(
        repo_arriendo=MagicMock(),
        repo_propiedad=MagicMock(),
        repo_renovacion=MagicMock(),
        repo_ipc=MagicMock(),
        repo_mandato=MagicMock(),
    )
    db = MagicMock()
    db.transaccion.return_value = _TransaccionFake(orden)
    servicio.repo_arriendo.db = db
    return servicio


def _mandato_activo() -> ContratoMandato:
    mandato = ContratoMandato(
        id_contrato_m=1,
        id_propiedad=10,
        id_propietario=20,
        id_asesor=30,
        fecha_inicio_contrato_m="2024-01-01",
        fecha_fin_contrato_m="2024-12-31",
        duracion_contrato_m=12,
        canon_mandato=500000,
        estado_contrato_m=EstadoContrato.ACTIVO,
    )
    mandato.updated_by = "test"
    mandato.updated_at = datetime.now().isoformat()
    return mandato


def _servicio_mandato() -> ServicioContratoMandato:
    repo_mandato = MagicMock()
    repo_propiedad = MagicMock()
    repo_renovacion = MagicMock()
    repo_mandato.obtener_por_id.return_value = _mandato_activo()
    repo_propiedad.obtener_por_id.return_value = None
    return ServicioContratoMandato(repo_mandato, repo_propiedad, repo_renovacion)


class TestCacheArrendamiento:
    def test_se_invalida_despues_del_commit(self):
        """FR-012: la invalidación ocurre tras el commit, no antes."""
        orden: list = []
        servicio = _servicio_arriendo_con_db(orden)
        sentinel = object()
        servicio._ejecutar_renovacion_arrendamiento = MagicMock(return_value=sentinel)

        with patch(
            "src.aplicacion.servicios.servicio_contrato_arrendamiento.invalidate_cache"
        ) as mock_inv:
            mock_inv.side_effect = lambda key: orden.append(f"cache:{key}")
            resultado = servicio.renovar_arrendamiento(1, "test")

        assert resultado is sentinel
        assert orden == ["inicio", "commit", f"cache:{KEY_CACHE}"]

    def test_fallo_de_cache_no_bloquea_ni_revierte(self):
        """FR-012: si la invalidación falla, la renovación ya confirmada sobrevive."""
        orden: list = []
        servicio = _servicio_arriendo_con_db(orden)
        sentinel = object()
        servicio._ejecutar_renovacion_arrendamiento = MagicMock(return_value=sentinel)

        with patch(
            "src.aplicacion.servicios.servicio_contrato_arrendamiento.invalidate_cache",
            side_effect=RuntimeError("cache caída"),
        ):
            resultado = servicio.renovar_arrendamiento(1, "test")

        assert resultado is sentinel
        assert "commit" in orden


class TestCacheMandato:
    def test_se_invalida_tras_renovacion(self):
        servicio = _servicio_mandato()

        with patch(
            "src.aplicacion.servicios.servicio_contrato_mandato.invalidate_cache"
        ) as mock_inv:
            resultado = servicio.renovar_mandato(1, "test", "2026-01-01")

        mock_inv.assert_called_once_with(KEY_CACHE)
        assert resultado.id_contrato_m == 1
        assert resultado.fecha_fin_contrato_m == "2026-01-01"

    def test_fallo_de_cache_no_bloquea_ni_revierte(self):
        servicio = _servicio_mandato()

        with patch(
            "src.aplicacion.servicios.servicio_contrato_mandato.invalidate_cache",
            side_effect=RuntimeError("cache caída"),
        ):
            resultado = servicio.renovar_mandato(1, "test", "2026-01-01")

        assert resultado.id_contrato_m == 1
