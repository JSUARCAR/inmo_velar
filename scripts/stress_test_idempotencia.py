"""
STRESS TEST: Validación de Idempotencia en Concurrencia Extrema.

Uso:
    python scripts/stress_test_idempotencia.py [modo] [workers]

Modos:
    seq         Prueba secuencial (1 llamada, 1 replay)
    conc        Prueba concurrente con misma key (default workers=20)
    stress      Prueba masiva (default workers=50)

Ejemplos:
    python scripts/stress_test_idempotencia.py seq
    python scripts/stress_test_idempotencia.py conc 10
    python scripts/stress_test_idempotencia.py stress 100
"""

import sys
import os
import threading
import concurrent.futures
import logging
import uuid
import argparse
from datetime import date, datetime
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(threadName)s: %(message)s"
)
logger = logging.getLogger(__name__)

sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_recaudo import RepositorioRecaudo
from src.infraestructura.persistencia.repositorio_idempotencia_postgres import (
    RepositorioIdempotenciaPostgres,
)
from src.aplicacion.servicios.servicio_recaudo import ServicioRecaudo
from src.aplicacion.esquemas.recaudo import ComandoRegistrarPago
from src.dominio.constantes.recaudo import MetodoPago


def _obtener_contrato(servicio):
    contratos = servicio.obtener_contratos_activos()
    if not contratos:
        print("ERROR: No hay contratos activos.")
        sys.exit(1)
    return int(contratos[0]["id"])


def _limpiar_key(full_key):
    db_manager.execute_write(
        "DELETE FROM EVENTOS_IDEMPOTENCIA WHERE IDEMPOTENCY_KEY = %s", (full_key,)
    )
    db_manager.execute_write("DELETE FROM IDEMPOTENCY_KEYS WHERE KEY = %s", (full_key,))


def _cleanup_recaudo(rid):
    if rid:
        db_manager.execute_write(
            "DELETE FROM RECAUDO_CONCEPTOS WHERE ID_RECAUDO = %s", (rid,)
        )
        db_manager.execute_write("DELETE FROM RECAUDOS WHERE ID_RECAUDO = %s", (rid,))


def test_secuencial():
    print("=" * 60)
    print("MODO: Secuencial — 1 creación + 1 replay")
    print("=" * 60)

    repo_rec = RepositorioRecaudo(db_manager)
    repo_idem = RepositorioIdempotenciaPostgres()
    servicio = ServicioRecaudo(repo_rec, db_manager, repo_idem)

    cid = _obtener_contrato(servicio)
    key = f"stress-seq-{uuid.uuid4().hex[:8]}"
    comando = ComandoRegistrarPago(
        id_contrato_a=cid,
        fecha_pago=date.today(),
        valor_total=100000,
        metodo_pago=MetodoPago.EFECTIVO,
        tipo_concepto="Canon",
        periodo=datetime.now().strftime("%Y-%m"),
        referencia_bancaria=f"REF-SEQ-{uuid.uuid4().hex[:6]}",
        observaciones="STRESS TEST SEQ",
    )

    full_key = f"recaudo:registrar:{key}"

    print("\n--- Ejecución 1 (Creación) ---")
    r1 = servicio.registrar_pago(comando, "admin", idempotency_key=key)
    id1 = r1.id_recaudo
    print(f"Recaudo creado: ID={id1}")

    print("\n--- Ejecución 2 (Replay) ---")
    r2 = servicio.registrar_pago(comando, "admin", idempotency_key=key)
    id2 = r2.get("ID_RECAUDO") if isinstance(r2, dict) else r2.id_recaudo
    print(f"Recaudo replay: ID={id2}")

    assert id1 == id2, f"IDs distintos: {id1} vs {id2}"
    print("\n✅ PRUEBA SECUENCIAL OK")

    _limpiar_key(full_key)
    _cleanup_recaudo(id1)
    print("Limpieza completada.")


def test_concurrente(workers: int = 20):
    print("=" * 60)
    print(f"MODO: Concurrente — {workers} hilos, misma key")
    print("=" * 60)

    repo_rec = RepositorioRecaudo(db_manager)
    repo_idem = RepositorioIdempotenciaPostgres()
    servicio = ServicioRecaudo(repo_rec, db_manager, repo_idem)

    cid = _obtener_contrato(servicio)
    key = f"stress-conc-{uuid.uuid4().hex[:8]}"
    comando = ComandoRegistrarPago(
        id_contrato_a=cid,
        fecha_pago=date.today(),
        valor_total=100000,
        metodo_pago=MetodoPago.EFECTIVO,
        tipo_concepto="Canon",
        periodo=datetime.now().strftime("%Y-%m"),
        referencia_bancaria=f"REF-CONC-{uuid.uuid4().hex[:6]}",
        observaciones=f"STRESS TEST CONCURRENTE - KEY: {key}",
    )

    full_key = f"recaudo:registrar:{key}"
    results: List[Tuple[int, bool, str]] = []
    lock = threading.Lock()

    def worker(idx):
        try:
            res = servicio.registrar_pago(comando, "admin", idempotency_key=key)
            if isinstance(res, dict):
                rid = res.get("id_recaudo") or res.get("ID_RECAUDO")
            else:
                rid = getattr(res, "id_recaudo", None) or getattr(res, "ID_RECAUDO", None)
            
            with lock:
                results.append((rid, True, "OK"))
        except Exception as e:
            with lock:
                results.append((0, False, str(e)))

    print(f"Lanzando {workers} workers...")
    start = datetime.now()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers, thread_name_prefix="ConcurWorker"
    ) as executor:
        futures = [executor.submit(worker, i) for i in range(workers)]
        concurrent.futures.wait(futures)

    duration = (datetime.now() - start).total_seconds()
    exitosos = [r for r in results if r[1]]
    fallidos = [r for r in results if not r[1]]
    unique_ids = set(r[0] for r in exitosos if r[0] > 0)

    print(f"\nDuración: {duration:.2f}s")
    print(f"Totales: {len(results)} | OK: {len(exitosos)} | FAIL: {len(fallidos)}")
    print(f"IDs únicos: {len(unique_ids)}")

    if len(unique_ids) == 1:
        print(f"\n✅ PRUEBA CONCURRENTE OK — 1 registro (ID={list(unique_ids)[0]})")
    elif len(unique_ids) > 1:
        print(f"\n❌ PRUEBA FALLIDA — {len(unique_ids)} registros: {unique_ids}")
    else:
        print("\n⚠️  Sin registros exitosos")

    _limpiar_key(full_key)
    for rid in unique_ids:
        _cleanup_recaudo(rid)
    print("Limpieza completada.")


def test_stress(workers: int = 50):
    print("=" * 60)
    print(f"MODO: Stress — {workers} hilos, misma key, medición completa")
    print("=" * 60)

    repo_rec = RepositorioRecaudo(db_manager)
    repo_idem = RepositorioIdempotenciaPostgres()
    servicio = ServicioRecaudo(repo_rec, db_manager, repo_idem)

    cid = _obtener_contrato(servicio)
    key = f"stress-max-{uuid.uuid4().hex[:8]}"
    comando = ComandoRegistrarPago(
        id_contrato_a=cid,
        fecha_pago=date.today(),
        valor_total=100000,
        metodo_pago=MetodoPago.EFECTIVO,
        tipo_concepto="Canon",
        periodo=datetime.now().strftime("%Y-%m"),
        referencia_bancaria=f"REF-STRESS-{uuid.uuid4().hex[:6]}",
        observaciones=f"STRESS TEST MASIVO - KEY: {key}",
    )

    full_key = f"recaudo:registrar:{key}"
    results: List[Tuple[int, bool, str]] = []
    lock = threading.Lock()

    def worker(idx):
        try:
            res = servicio.registrar_pago(comando, "admin", idempotency_key=key)
            if isinstance(res, dict):
                rid = res.get("id_recaudo") or res.get("ID_RECAUDO")
            else:
                rid = getattr(res, "id_recaudo", None) or getattr(res, "ID_RECAUDO", None)
            
            with lock:
                results.append((rid, True, "OK"))
        except Exception as e:
            with lock:
                results.append((0, False, str(e)))

    print(f"Lanzando {workers} workers...")
    start = datetime.now()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers, thread_name_prefix="StressWorker"
    ) as executor:
        futures = [executor.submit(worker, i) for i in range(workers)]
        concurrent.futures.wait(futures)

    duration = (datetime.now() - start).total_seconds()
    exitosos = [r for r in results if r[1]]
    fallidos = [r for r in results if not r[1]]
    unique_ids = set(r[0] for r in exitosos if r[0] > 0)

    print(f"\n--- RESULTADOS ---")
    print(f"Duración: {duration:.2f}s")
    print(f"Totales: {len(results)} | OK: {len(exitosos)} | FAIL: {len(fallidos)}")
    print(f"IDs únicos: {len(unique_ids)}")

    if fallidos:
        print("\nTop 5 errores:")
        for f in fallidos[:5]:
            print(f"  {f[2][:100]}")

    if len(unique_ids) == 1:
        print(f"\n✅ STRESS TEST OK — 1 registro (ID={list(unique_ids)[0]})")
    elif len(unique_ids) > 1:
        print(f"\n❌ STRESS TEST FALLIDO — {len(unique_ids)} registros: {unique_ids}")
    else:
        print("\n⚠️  Sin registros exitosos")

    _limpiar_key(full_key)
    for rid in unique_ids:
        _cleanup_recaudo(rid)
    print("Limpieza completada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stress test de idempotencia")
    parser.add_argument(
        "modo",
        nargs="?",
        default="stress",
        choices=["seq", "conc", "stress"],
        help="Modo de prueba (default: stress)",
    )
    parser.add_argument(
        "workers",
        nargs="?",
        type=int,
        default=None,
        help="Número de workers (default: seq=1, conc=20, stress=50)",
    )

    args = parser.parse_args()
    workers_defaults = {"seq": 1, "conc": 20, "stress": 50}
    workers = args.workers or workers_defaults[args.modo]

    if args.modo == "seq":
        test_secuencial()
    elif args.modo == "conc":
        test_concurrente(workers)
    else:
        test_stress(workers)

    db_manager.shutdown()
