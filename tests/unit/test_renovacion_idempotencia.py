"""
T018 [US2]: Idempotencia de renovación de mandato (FR-011).

Verifica que el decorador @idempotent(key_prefix="mandato:renovar")
impide filas duplicadas de RENOVACIONES_CONTRATOS para el mismo intento
de renovación, y que IDEMPOTENCY_KEYS transita processing -> completed.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock


from src.aplicacion.decorators.idempotent import idempotent
from src.aplicacion.servicios.servicio_contrato_mandato import ServicioContratoMandato
from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia


class RepoIdempotenciaConHistorial(IRepositorioIdempotencia):
    """Fake de repositorio de idempotencia que registra la secuencia de
    estados de cada clave (transiciones de IDEMPOTENCY_KEYS)."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}
        self.estados: Dict[str, list] = {}

    def _set(self, key: str, campo: str, valor: Any) -> None:
        if key not in self._store:
            self._store[key] = {}
        self._store[key][campo] = valor
        self.estados.setdefault(key, []).append((campo, valor))

    def existe(self, key: str) -> bool:
        return key in self._store

    def bloquear(
        self,
        key: str,
        operacion: str,
        parametros: Dict[str, Any],
        usuario_id: int,
        ttl_hours: int = 1,
    ) -> bool:
        if key in self._store:
            return False
        self._set(key, "operacion", operacion)
        self._set(key, "estado", "processing")
        return True

    def obtener_resultado(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.get("estado") == "completed":
            return entry.get("resultado")
        if entry.get("estado") == "processing":
            return {"status": "processing"}
        return None

    def registrar(
        self,
        key: str,
        operacion: str,
        resultado: Any,
        parametros: Dict[str, Any],
        usuario_id: int,
        ttl_hours: int = 24,
    ) -> None:
        self._set(key, "resultado", resultado)
        self._set(key, "estado", "completed")

    def registrar_evento(
        self,
        entidad_tipo: str,
        entidad_id: int,
        tipo_evento: str,
        idempotency_key: str,
        payload: Dict[str, Any],
        usuario_id: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    def limpiar_expirados(self) -> int:
        return 0


class ServicioRenovacionFake:
    """Equivalente a ServicioContratoMandato.renovar_mandato decorado."""

    def __init__(self, repo_idempotencia: Optional[IRepositorioIdempotencia]):
        self.repo_idempotencia = repo_idempotencia
        self.crear_renovacion = Mock()
        self.actualizar_mandato = Mock()
        self.call_count = 0

    @idempotent(key_prefix="mandato:renovar")
    def renovar_mandato(
        self, id_contrato: int, usuario_sistema: str, nueva_fecha_fin: str = None, **kwargs
    ) -> Dict[str, Any]:
        self.call_count += 1
        self.crear_renovacion(id_contrato=id_contrato, usuario_sistema=usuario_sistema)
        return {
            "id_contrato_m": id_contrato,
            "fecha_fin": nueva_fecha_fin or "2026-01-01",
            "estado": "renovado",
        }


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


class TestIdempotenciaRenovacionMandato:
    def test_la_misma_clave_no_duplica_filas(self) -> None:
        repo = RepoIdempotenciaConHistorial()
        servicio = ServicioRenovacionFake(repo)

        r1 = servicio.renovar_mandato(1, "sistema", "2026-01-01")
        r2 = servicio.renovar_mandato(1, "sistema", "2026-01-01")

        assert servicio.call_count == 1
        assert servicio.crear_renovacion.call_count == 1
        assert r1 == r2

    def test_transicion_estados_processing_completed(self) -> None:
        repo = RepoIdempotenciaConHistorial()
        servicio = ServicioRenovacionFake(repo)

        servicio.renovar_mandato(1, "sistema", "2026-01-01")

        claves = list(repo.estados.keys())
        assert len(claves) == 1
        clave = claves[0]

        transiciones = [
            estado for campo, estado in repo.estados[clave] if campo == "estado"
        ]
        assert "processing" in transiciones
        assert transiciones[-1] == "completed"
        assert repo._store[clave]["estado"] == "completed"

    def test_claves_distintas_ejecutan_por_separado(self) -> None:
        repo = RepoIdempotenciaConHistorial()
        servicio = ServicioRenovacionFake(repo)

        servicio.renovar_mandato(1, "sistema", "2026-01-01")
        servicio.renovar_mandato(2, "sistema", "2026-02-01")

        assert servicio.call_count == 2
        assert len(repo.estados) == 2

    def test_sin_repo_idempotencia_el_flujo_no_se_bloquea(self) -> None:
        servicio = ServicioRenovacionFake(None)

        r = servicio.renovar_mandato(1, "sistema", "2026-01-01")

        assert servicio.call_count == 1
        assert r["estado"] == "renovado"


class TestServicioRealMandato:
    def test_renovar_mandato_decorado_previene_repetidos(self) -> None:
        repo_idem = RepoIdempotenciaConHistorial()
        repo_mandato = Mock()
        repo_propiedad = Mock()
        repo_renovacion = Mock()

        # FR-006/FR-008: renovar_mandato abre db.transaccion(); el mock debe
        # soportar el protocolo de context manager (Spec 075).
        repo_mandato.db = MagicMock()
        repo_mandato.db.transaccion.return_value.__enter__ = MagicMock()
        repo_mandato.db.transaccion.return_value.__exit__ = MagicMock()

        mandato = _mandato_activo()
        repo_mandato.obtener_por_id.return_value = mandato
        repo_propiedad.obtener_por_id.return_value = None

        servicio = ServicioContratoMandato(
            repo_mandato, repo_propiedad, repo_renovacion, repo_idem
        )

        primera = servicio.renovar_mandato(1, "sistema", "2026-01-01")
        segunda = servicio.renovar_mandato(1, "sistema", "2026-01-01")

        assert repo_renovacion.crear.call_count == 1
        assert repo_mandato.actualizar.call_count == 1
        assert primera.id_contrato_m == 1
        assert segunda["id_contrato_m"] == 1