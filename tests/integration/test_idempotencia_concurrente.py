import threading
import time
import uuid
from typing import Dict

import pytest

from src.aplicacion.decorators.idempotent import idempotent
from tests.integration.test_idempotencia import MockRepositorioIdempotencia


class MockServiceConcurrente:
    def __init__(self, repo_idempotencia, usuario_id=1):
        self.repo_idempotencia = repo_idempotencia
        self.call_count = 0
        self.call_count_lock = threading.Lock()
        self.usuario_id = usuario_id

    @idempotent(key_prefix="test:concurrente", ttl_hours=1)
    def operacion_lenta(self, valor: str, idempotency_key: str | None = None, **kwargs):
        time.sleep(0.05)
        with self.call_count_lock:
            self.call_count += 1
        return {"resultado": f"procesado:{valor}", "timestamp": time.time()}


@pytest.fixture
def repo():
    return MockRepositorioIdempotencia()


@pytest.fixture
def key():
    return f"conc-{uuid.uuid4().hex[:12]}"


class TestConcurrenciaIdempotencia:
    def test_10_hilos_misma_key_un_solo_call(self, repo, key):
        service = MockServiceConcurrente(repo, usuario_id=1)
        resultados: Dict[int, dict] = {}
        errores: list[str] = []
        lock = threading.Lock()

        def worker():
            try:
                res = service.operacion_lenta("data", idempotency_key=key)
                with lock:
                    resultados[threading.get_ident()] = res
            except Exception as e:
                with lock:
                    errores.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errores, f"Errores: {errores}"
        assert service.call_count == 1, f"call_count={service.call_count}, esperado=1"
        assert len(resultados) == 10
        timestamps = {r["timestamp"] for r in resultados.values()}
        assert len(timestamps) == 1, "Timestamps distintos = no vino del cache"
        resultados_lista = list(resultados.values())
        for i in range(1, len(resultados_lista)):
            assert resultados_lista[i]["resultado"] == resultados_lista[0]["resultado"]

    def test_5_hilos_5_keys_5_calls(self, repo):
        service = MockServiceConcurrente(repo, usuario_id=1)
        resultados: Dict[int, dict] = {}
        lock = threading.Lock()

        def worker(worker_key: str):
            try:
                res = service.operacion_lenta("data", idempotency_key=worker_key)
                with lock:
                    resultados[threading.get_ident()] = res
            except Exception:
                pass

        keys = [f"k-{uuid.uuid4().hex[:8]}" for _ in range(5)]
        threads = [threading.Thread(target=worker, args=(k,)) for k in keys]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert service.call_count == 5

    def test_20_hilos_estres_rapido(self, repo, key):
        service = MockServiceConcurrente(repo, usuario_id=1)
        resultados: Dict[int, dict] = {}
        errores: list[str] = []
        lock = threading.Lock()

        def worker():
            try:
                res = service.operacion_lenta("data", idempotency_key=key)
                with lock:
                    resultados[threading.get_ident()] = res
            except Exception as e:
                with lock:
                    errores.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if errores:
            pytest.fail(f"Errores en hilos: {errores}")
        assert service.call_count == 1, (
            f"20 hilos deben producir 1 call, count={service.call_count}"
        )
        assert len(resultados) == 20
