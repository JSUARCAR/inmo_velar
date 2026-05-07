import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from unittest.mock import patch

import pytest

from src.aplicacion.decorators.estrategia_idempotencia import (
    DatabaseIdempotencyStrategy,
    _build_full_key,
    _resolve_usuario_id,
    _serialize,
    _MAX_POLL_ATTEMPTS,
)
from src.aplicacion.decorators.idempotent import idempotent
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia


class MockRepositorioIdempotencia(IRepositorioIdempotencia):
    def __init__(self):
        self._store: Dict[str, dict] = {}
        self._lock = threading.Lock()

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
        with self._lock:
            if key in self._store:
                return False
            self._store[key] = {
                "key": key,
                "operacion": operacion,
                "parametros": parametros,
                "usuario_id": usuario_id,
                "estado": "processing",
                "fecha_creacion": datetime.now(timezone.utc),
            }
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
        if key in self._store:
            self._store[key]["resultado"] = resultado
            self._store[key]["estado"] = "completed"

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


@pytest.fixture
def mock_repo():
    return MockRepositorioIdempotencia()


@pytest.fixture
def strategy(mock_repo):
    return DatabaseIdempotencyStrategy(mock_repo)


class TestDatabaseIdempotencyStrategy:
    def test_first_call_executes_and_caches(self, strategy, mock_repo):
        def dummy_op(valor: str, idempotency_key: str | None = None, **kwargs) -> dict:
            return {"resultado": f"procesado:{valor}"}

        result = strategy.execute(
            func=dummy_op,
            args=(),
            kwargs={"valor": "data", "idempotency_key": "key-1"},
            key_prefix="test",
        )

        assert result["resultado"] == "procesado:data"
        cached = mock_repo.obtener_resultado("test:key-1")
        assert cached is not None
        assert cached["resultado"] == "procesado:data"

    def test_second_call_returns_cached(self, strategy, mock_repo):
        call_count = 0

        def dummy_op(valor: str, idempotency_key: str | None = None, **kwargs) -> dict:
            nonlocal call_count
            call_count += 1
            return {"resultado": f"procesado:{valor}"}

        r1 = strategy.execute(
            func=dummy_op,
            args=(),
            kwargs={"valor": "data", "idempotency_key": "key-2"},
            key_prefix="test",
        )
        r2 = strategy.execute(
            func=dummy_op,
            args=(),
            kwargs={"valor": "data", "idempotency_key": "key-2"},
            key_prefix="test",
        )

        assert call_count == 1
        assert r1["resultado"] == r2["resultado"]

    def test_different_keys_execute_independently(self, strategy, mock_repo):
        call_count = 0

        def dummy_op(valor: str, idempotency_key: str | None = None, **kwargs) -> dict:
            nonlocal call_count
            call_count += 1
            return {"resultado": f"procesado:{valor}"}

        strategy.execute(
            func=dummy_op,
            args=(),
            kwargs={"valor": "a", "idempotency_key": "key-a"},
            key_prefix="test",
        )
        strategy.execute(
            func=dummy_op,
            args=(),
            kwargs={"valor": "b", "idempotency_key": "key-b"},
            key_prefix="test",
        )

        assert call_count == 2

    def test_serialize_object_with_dict(self):
        class Dummy:
            def __init__(self):
                self.id = 42
                self.name = "test"

        result = _serialize(Dummy())
        assert result == {"id": 42, "name": "test"}

    def test_serialize_list(self):
        class Dummy:
            def __init__(self):
                self.id = 1

        result = _serialize([Dummy(), {"a": 1}])
        assert result == [{"id": 1}, {"a": 1}]

    def test_serialize_primitive(self):
        assert _serialize("string") == "string"
        assert _serialize(42) == 42
        assert _serialize([1, 2, 3]) == [1, 2, 3]

    def test_build_full_key_with_explicit_key(self):
        import inspect

        sig = inspect.signature(lambda a, b: None)
        bound = sig.bind(a=1, b=2)
        bound.apply_defaults()
        key = _build_full_key("test:prefix", bound, use_args=True)
        assert key.startswith("test:prefix:")
        assert len(key) > len("test:prefix:")

    def test_build_full_key_with_idempotency_key(self):
        import inspect

        sig = inspect.signature(lambda idempotency_key: None)
        bound = sig.bind(idempotency_key="my-key")
        bound.apply_defaults()
        key = _build_full_key("prefix", bound, use_args=True)
        assert key == "prefix:my-key"

    def test_build_full_key_double_prefix_guard(self):
        import inspect

        sig = inspect.signature(lambda idempotency_key: None)
        bound = sig.bind(idempotency_key="prefix:my-key")
        bound.apply_defaults()
        key = _build_full_key("prefix", bound, use_args=True)
        assert key == "prefix:my-key"
        assert key.count("prefix") == 1


class MockService:
    def __init__(self, repo_idempotencia, usuario_id=1):
        self.repo_idempotencia = repo_idempotencia
        self.call_count = 0
        self.usuario_id = usuario_id

    @idempotent(key_prefix="test:service", ttl_hours=1)
    def operacion(self, valor: str, idempotency_key: str | None = None, **kwargs):
        self.call_count += 1
        return {"resultado": f"ok:{valor}", "timestamp": time.time()}


class TestIdempotentDecorator:
    def test_decorator_caches_result(self):
        repo = MockRepositorioIdempotencia()
        service = MockService(repo)
        key = f"dec-test-{uuid.uuid4().hex[:8]}"

        r1 = service.operacion("data", idempotency_key=key)
        r2 = service.operacion("data", idempotency_key=key)

        assert service.call_count == 1
        assert r1["resultado"] == r2["resultado"]
        assert r1["timestamp"] == r2["timestamp"]

    def test_decorator_different_keys(self):
        repo = MockRepositorioIdempotencia()
        service = MockService(repo)

        r1 = service.operacion("a", idempotency_key="k1")
        r2 = service.operacion("b", idempotency_key="k2")

        assert service.call_count == 2
        assert r1["resultado"] == "ok:a"
        assert r2["resultado"] == "ok:b"

    def test_decorator_no_repo_falls_through(self):
        service = MockService(repo_idempotencia=None, usuario_id=1)
        service.repo_idempotencia = None

        r = service.operacion("data", idempotency_key="key")
        assert r["resultado"] == "ok:data"


class TestErrorRecovery:
    def test_function_error_sets_failed_status(self, strategy, mock_repo):
        def failing_op(valor: str, idempotency_key: str | None = None, **kwargs):
            raise ValueError("Simulated DB error")

        with patch(
            "src.infraestructura.persistencia.database.db_manager.execute_write"
        ) as mock_write:
            with pytest.raises(ValueError, match="Simulated DB error"):
                strategy.execute(
                    func=failing_op,
                    args=(),
                    kwargs={"valor": "x", "idempotency_key": "key-error"},
                    key_prefix="test",
                )

            mock_write.assert_called_once()
            sql = mock_write.call_args[0][0]
            params = mock_write.call_args[0][1]
            assert "ESTADO" in sql.upper() and "failed" in sql.lower()
            assert "test:key-error" in params

    def test_concurrent_timeout_raises_runtime_error(self, strategy, mock_repo):
        mock_repo._store["test:key-timeout"] = {"estado": "processing"}

        def dummy_op(valor: str, idempotency_key: str | None = None, **kwargs):
            return {"ok": True}

        timeout_seconds = _MAX_POLL_ATTEMPTS * 0.5 + 1

        with pytest.raises(RuntimeError, match="Timeout esperando resultado"):
            strategy.execute(
                func=dummy_op,
                args=(),
                kwargs={"valor": "x", "idempotency_key": "key-timeout"},
                key_prefix="test",
                ttl_hours=1,
            )

    def test_failed_key_not_returned_as_completed(self, strategy, mock_repo):
        mock_repo._store["test:key-failed"] = {
            "estado": "failed",
            "resultado": {"error": "previous error", "status": "failed"},
        }

        cached = mock_repo.obtener_resultado("test:key-failed")
        assert cached is None, "Failed key no debe retornarse como resultado completado"

        with pytest.raises(RuntimeError, match="Timeout esperando resultado"):
            strategy.execute(
                func=lambda valor, idempotency_key=None, **kwargs: {"ok": True},
                args=(),
                kwargs={"valor": "x", "idempotency_key": "key-failed"},
                key_prefix="test",
            )

    @pytest.mark.skip(
        reason="Requiere PostgreSQL real. Ejecutar manual: python scripts/stress_test_idempotencia.py stress 50"
    )
    def test_integracion_postgres_real(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "scripts/stress_test_idempotencia.py", "stress", "10"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Stress test falló:\n{result.stderr}"
