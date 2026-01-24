"""
Elite PDF Download API - Backend Route para descargas con nombre correcto.

Esta API route sirve PDFs con el header Content-Disposition, garantizando
que el navegador use el nombre de archivo correcto en lugar de UUIDs.
"""

from fastapi import APIRouter, HTTPException, FastAPI
from fastapi.responses import FileResponse, Response
from pathlib import Path
import os

# Router para PDF downloads - SIN prefijo porque se montará en /api/pdf
pdf_router = APIRouter(tags=["PDF Downloads"])

# Directorio base donde se guardan los PDFs generados
PDF_OUTPUT_DIR = Path("documentos_generados")


@pdf_router.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Endpoint para descargar PDFs con nombre correcto.
    
    El header Content-Disposition fuerza al navegador a usar el nombre
    especificado en lugar de generar un UUID.
    
    Args:
        filename: Nombre del archivo PDF a descargar
        
    Returns:
        FileResponse con headers correctos para descarga
    """
    # Sanitizar filename para prevenir path traversal
    safe_filename = Path(filename).name
    
    # Construir path completo
    pdf_path = PDF_OUTPUT_DIR / safe_filename
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF no encontrado: {safe_filename}")
    
    if not pdf_path.suffix.lower() == '.pdf':
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    # Retornar archivo permitiendo que FileResponse maneje el Content-Disposition
    # Starlette/FastAPI generará automáticamente: content-disposition: attachment; filename="..."
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=safe_filename,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }
    )


@pdf_router.get("/view/{filename}")
async def view_pdf(filename: str):
    """
    Endpoint para ver PDFs inline en el navegador.
    
    Args:
        filename: Nombre del archivo PDF a visualizar
        
    Returns:
        FileResponse para visualización inline
    """
    safe_filename = Path(filename).name
    pdf_path = PDF_OUTPUT_DIR / safe_filename
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF no encontrado: {safe_filename}")
    
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename}"',
        }
    )


def register_pdf_routes(app):
    """
    Registra las rutas de PDF en la aplicación FastAPI/Starlette de Reflex.
    
    Args:
        app: Instancia de la app Reflex
    """
    # Obtener la instancia subyacente de Reflex (puede ser Starlette o FastAPI)
    fastapi_app = getattr(app, "api", getattr(app, "_api", None))
    
    if fastapi_app:
        # Creamos una sub-app FastAPI para poder usar routers
        # Esto soluciona el error "Starlette object has no attribute include_router"
        # al montar la sub-app que SÍ es FastAPI sobre la app Starlette
        pdf_api = FastAPI()
        
        # Configurar CORS para permitir descargas directas desde el frontend
        from fastapi.middleware.cors import CORSMiddleware
        pdf_api.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        pdf_api.include_router(pdf_router)
        
        # Montamos la sub-app en /api/pdf
        try:
            if hasattr(fastapi_app, "mount"):
                fastapi_app.mount("/api/pdf", pdf_api)
                pass  # print("✅ Rutas PDF montadas exitosamente en /api/pdf") [OpSec Removed]
            else:
                pass  # print("❌ Error: La app backend no soporta 'mount'") [OpSec Removed]
        except Exception as e:
            pass  # print(f"❌ Error registrando rutas PDF: {e}") [OpSec Removed]
    else:
        pass  # print("WARNING: No se pudo obtener la instancia FastAPI de app. No se registraron rutas PDF.") [OpSec Removed]
