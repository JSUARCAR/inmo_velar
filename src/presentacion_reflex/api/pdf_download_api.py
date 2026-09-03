"""
Elite PDF Download API - Backend Route para descargas con nombre correcto.

Versión compatible con Starlette y FastAPI (Uso de .mount()).
"""

import os
import time
import logging
import urllib.parse
from pathlib import Path
from fastapi import APIRouter, FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Router para PDF downloads
pdf_router = APIRouter(tags=["PDF Downloads"])

# Directorio base donde se guardan los PDFs generados
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
PDF_OUTPUT_DIR = (BASE_DIR / "documentos_generados").resolve()

# === Rate Limiting Simple ===
RATE_LIMIT_DB = {}
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW = 60  # segundos


def get_current_user(request: Request):
    """Dependencia dummy - se reemplazará por validar_sesion_api"""
    pass


async def rate_limit_pdf(usuario: dict = Depends(get_current_user)) -> dict:
    user_id = (
        usuario.get("id") if isinstance(usuario, dict) else getattr(usuario, "id", None)
    )
    if not user_id:
        return usuario

    current_time = time.time()

    if user_id not in RATE_LIMIT_DB:
        RATE_LIMIT_DB[user_id] = []

    RATE_LIMIT_DB[user_id] = [
        req_time
        for req_time in RATE_LIMIT_DB[user_id]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    if len(RATE_LIMIT_DB[user_id]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas peticiones (Rate Limit excedido). Intente más tarde.",
        )

    RATE_LIMIT_DB[user_id].append(current_time)
    return usuario


@pdf_router.get("/download/{filename}")
async def download_pdf(filename: str):
    """Endpoint para descargar PDFs con nombre correcto y validación de seguridad."""
    try:
        decoded_filename = urllib.parse.unquote(filename)
        # Extraer solo el nombre del archivo para evitar inyecciones iniciales
        safe_filename = Path(decoded_filename).name
        pdf_path = (PDF_OUTPUT_DIR / safe_filename).resolve()

        # Validación estricta contra Path Traversal
        if not pdf_path.is_relative_to(PDF_OUTPUT_DIR):
            raise HTTPException(
                status_code=403, detail="Acceso denegado: Ruta inválida"
            )

        if not pdf_path.exists():
            raise HTTPException(
                status_code=404, detail=f"PDF no encontrado o expirado: {safe_filename}"
            )

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=safe_filename,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Content-Type": "application/pdf",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fallo interno en descarga de PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Error interno del servidor procesando el PDF"
        )


@pdf_router.get("/view/{filename}")
async def view_pdf(filename: str):
    """Endpoint para ver PDFs inline en el navegador con validación de seguridad."""
    try:
        decoded_filename = urllib.parse.unquote(filename)
        safe_filename = Path(decoded_filename).name
        pdf_path = (PDF_OUTPUT_DIR / safe_filename).resolve()

        if not pdf_path.is_relative_to(PDF_OUTPUT_DIR):
            raise HTTPException(
                status_code=403, detail="Acceso denegado: Ruta inválida"
            )

        if not pdf_path.exists():
            raise HTTPException(
                status_code=404, detail=f"PDF no encontrado o expirado: {safe_filename}"
            )

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{safe_filename}"',
                "Content-Type": "application/pdf",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fallo interno en visualización de PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Error interno del servidor procesando el PDF"
        )


def register_pdf_routes(app):
    """
    Registra las rutas de PDF en la aplicación Reflex usando .mount() para compatibilidad total.
    """
    try:
        target_app = getattr(app, "api", getattr(app, "_api", None))

        if not target_app:
            print(
                "[PDF-REGISTER] Error: No se pudo obtener la instancia de la app backend."
            )
            return

        from src.presentacion_reflex.api.deps import validar_sesion_api

        # Sobrescribir la dependencia dummy con la real
        global get_current_user
        get_current_user = validar_sesion_api

        # Crear una mini-app de FastAPI para el router con rate limiting + auth
        pdf_api = FastAPI(dependencies=[Depends(rate_limit_pdf)])

        # Configuración estricta CORS (allow_credentials=True requiere orígenes explícitos)
        frontend_url = os.environ.get(
            "FRONTEND_URL", "https://inmovelar-production.up.railway.app"
        )
        allowed_origins = [frontend_url, "http://localhost:3000"]

        pdf_api.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )

        pdf_api.include_router(pdf_router)

        # Montar la app en /api/pdf
        if hasattr(target_app, "mount"):
            target_app.mount("/api/pdf", pdf_api)
            print(
                "[PDF-REGISTER] Rutas montadas exitosamente en /api/pdf usando .mount()"
            )
        else:
            print("[PDF-REGISTER] Error: La app backend no soporta '.mount()'")

    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.critical(f"FALLO CRITICO MONTANDO RUTAS PDF: {str(e)}", exc_info=True)
        print(f"[PDF-REGISTER] Error critico registrando rutas: {str(e)}")
