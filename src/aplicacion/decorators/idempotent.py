import functools
import logging
from typing import Callable, Optional
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.estrategia_idempotencia import (
    DatabaseIdempotencyStrategy,
)

logger = logging.getLogger(__name__)


def idempotent(key_prefix: str, ttl_hours: int = 24, use_args: bool = True):
    """
    Decorador para garantizar la idempotencia de una operación crítica.
    Delega a DatabaseIdempotencyStrategy para el lock atómico y backoff.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args else None
            repo_idem: Optional[IRepositorioIdempotencia] = getattr(
                instance, "repo_idempotencia", None
            )

            if not repo_idem:
                return func(*args, **kwargs)

            strategy = DatabaseIdempotencyStrategy(repo_idem)
            return strategy.execute(
                func=func,
                args=args,
                kwargs=kwargs,
                key_prefix=key_prefix,
                ttl_hours=ttl_hours,
                use_args=use_args,
            )

        return wrapper

    return decorator
