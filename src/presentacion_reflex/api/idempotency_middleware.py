"""
Middleware de Idempotencia para API REST.
Intercepta requests con header Idempotency-Key, valida contra PostgreSQL,
y retorna respuesta cacheada si la operación ya fue completada.
"""

import json
import logging
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.infraestructura.factory.factory_idempotencia import crear_repo_idempotencia

logger = logging.getLogger(__name__)

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware FastAPI que maneja el header Idempotency-Key.
    - Si la key existe y está completada → retorna 200 con resultado cacheado.
    - Si la key está en processing → retorna 409 Conflict.
    - Si la key no existe → pasa al handler (el decorador @idempotent la registrará).
    """

    def __init__(self, app, repo_idem: Optional[IRepositorioIdempotencia] = None):
        super().__init__(app)
        self.repo_idem = repo_idem or crear_repo_idempotencia()

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in SAFE_METHODS:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        cached = self.repo_idem.obtener_resultado(idempotency_key)
        if cached:
            if isinstance(cached, dict) and cached.get("status") == "processing":
                return Response(
                    content=json.dumps(
                        {"error": "Operación en progreso", "status": "processing"}
                    ),
                    media_type="application/json",
                    status_code=409,
                    headers={"Retry-After": "2"},
                )
            return Response(
                content=json.dumps(cached),
                media_type="application/json",
                status_code=200,
                headers={
                    "X-Idempotency-Cached": "true",
                    "X-Idempotency-Key": idempotency_key,
                },
            )

        response = await call_next(request)
        response.headers["X-Idempotency-Key"] = idempotency_key
        return response
