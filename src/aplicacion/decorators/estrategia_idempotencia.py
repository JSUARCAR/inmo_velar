import hashlib
import json
import inspect
import logging
import time
from typing import Callable, Optional, Any, Dict
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.infraestructura.factory.factory_idempotencia import crear_repo_idempotencia

logger = logging.getLogger(__name__)

_MAX_POLL_ATTEMPTS = 15
_INITIAL_DELAY = 0.01


def _resolve_usuario_id(call_args: Dict, instance) -> int:
    usuario_id = call_args.get("usuario_id")
    if not usuario_id:
        usuario_str = call_args.get("usuario")
        if usuario_str and isinstance(usuario_str, str):
            from src.infraestructura.persistencia.database import db_manager

            user_data = db_manager.execute_query_one(
                "SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s",
                (usuario_str,),
            )
            if user_data:
                usuario_id = user_data.get("ID_USUARIO")
    if not usuario_id:
        usuario_id = getattr(instance, "usuario_id", 1)
    return usuario_id


def _serialize(result):
    if hasattr(result, "__dict__"):
        return result.__dict__
    if isinstance(result, list):
        return [r.__dict__ if hasattr(r, "__dict__") else r for r in result]
    return result


def _build_full_key(
    key_prefix: str, bound: inspect.BoundArguments, use_args: bool
) -> str:
    raw_key = bound.arguments.get("idempotency_key")
    if raw_key:
        return (
            f"{key_prefix}:{raw_key}" if not raw_key.startswith(key_prefix) else raw_key
        )
    if use_args:
        call_args = {k: v for k, v in bound.arguments.items() if k != "self"}
        arg_str = json.dumps(call_args, sort_keys=True, default=str)
        key_hash = hashlib.sha256(arg_str.encode()).hexdigest()
        return f"{key_prefix}:{key_hash}"
    return key_prefix


class DatabaseIdempotencyStrategy:
    """
    Estrategia de idempotencia basada en PostgreSQL.
    Encapsula: lock atómico, resolución de usuario, backoff, serialización.
    """

    def __init__(self, repo_idem: Optional[IRepositorioIdempotencia] = None):
        self.repo_idem = repo_idem or crear_repo_idempotencia()

    def execute(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        key_prefix: str,
        ttl_hours: int = 24,
        use_args: bool = True,
    ) -> Any:
        instance = args[0] if args else None
        repo_idem = self.repo_idem

        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        call_args = {k: v for k, v in bound.arguments.items() if k != "self"}

        full_key = _build_full_key(key_prefix, bound, use_args)

        cached = repo_idem.obtener_resultado(full_key)
        if cached:
            if isinstance(cached, dict) and cached.get("status") in (
                "processing",
                "failed",
            ):
                cached = None
            else:
                return cached

        usuario_id = _resolve_usuario_id(call_args, instance)

        won = repo_idem.bloquear(
            key=full_key,
            operacion=f"{func.__module__}.{func.__name__}",
            parametros=call_args,
            usuario_id=usuario_id,
            ttl_hours=1,
        )

        if won:
            try:
                kwargs["_idempotency_full_key"] = full_key
                result = func(*args, **kwargs)
                serializable = _serialize(result)
                repo_idem.registrar(
                    key=full_key,
                    operacion=f"{func.__module__}.{func.__name__}",
                    resultado=serializable,
                    parametros=call_args,
                    usuario_id=usuario_id,
                    ttl_hours=ttl_hours,
                )
                return result
            except Exception as e:
                from src.infraestructura.persistencia.database import db_manager

                error_payload = json.dumps({"error": str(e), "status": "failed"})
                db_manager.execute_write(
                    "UPDATE IDEMPOTENCY_KEYS SET ESTADO = 'failed', RESULTADO = %s::jsonb WHERE KEY = %s",
                    (error_payload, full_key),
                )
                raise e

        for attempt in range(_MAX_POLL_ATTEMPTS):
            delay = min(_INITIAL_DELAY * (2**attempt), 0.5)
            time.sleep(delay)
            cached = repo_idem.obtener_resultado(full_key)
            if cached:
                if isinstance(cached, dict) and cached.get("status") in (
                    "processing",
                    "failed",
                ):
                    continue
                return cached

        raise RuntimeError(
            f"Timeout esperando resultado de operación concurrente para key: {full_key}"
        )
