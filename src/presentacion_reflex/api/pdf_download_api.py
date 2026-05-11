"""
Elite PDF Download API - Backend Route para descargas con nombre correcto.

Versión compatible con Starlette y FastAPI (Uso de .mount()).
"""

import urllib.parse
from pathlib import Path
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Router para PDF downloads
pdf_router = APIRouter(tags=["PDF Downloads"])

# Directorio base donde se guardan los PDFs generados
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
PDF_OUTPUT_DIR = BASE_DIR / "documentos_generados"

@pdf_router.get("/download/{filename}")
async def download_pdf(filename: str):
    """Endpoint para descargar PDFs con nombre correcto."""
    decoded_filename = urllib.parse.unquote(filename)
    print(f"\n[PDF-DOWNLOAD] Original: {filename}")
    print(f"[PDF-DOWNLOAD] Decodificado: {decoded_filename}")
    
    safe_filename = Path(decoded_filename).name
    pdf_path = PDF_OUTPUT_DIR / safe_filename
    
    print(f"[PDF-DOWNLOAD] Ruta absoluta: {pdf_path.absolute()}")
    print(f"[PDF-DOWNLOAD] Existe?: {pdf_path.exists()}")

    if not pdf_path.exists():
        print(f"[PDF-DOWNLOAD] Error 404: Archivo no encontrado")
        raise HTTPException(
            status_code=404, detail=f"PDF no encontrado: {safe_filename}"
        )

    return FileResponse(
        path=str(pdf_path),
        media_type=None,  # FastAPI detectará automáticamente application/pdf o application/zip
        filename=safe_filename,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )

@pdf_router.get("/view/{filename}")
async def view_pdf(filename: str):
    """Endpoint para ver PDFs inline en el navegador."""
    decoded_filename = urllib.parse.unquote(filename)
    safe_filename = Path(decoded_filename).name
    pdf_path = PDF_OUTPUT_DIR / safe_filename

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404, detail=f"PDF no encontrado: {safe_filename}"
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename}"',
        },
    )

def register_pdf_routes(app):
    """
    Registra las rutas de PDF en la aplicación Reflex usando .mount() para compatibilidad total.
    """
    try:
        target_app = getattr(app, "api", getattr(app, "_api", None))

        if not target_app:
            print("[PDF-REGISTER] Error: No se pudo obtener la instancia de la app backend.")
            return

        # Crear una mini-app de FastAPI para el router
        pdf_api = FastAPI()
        
        # Habilitar CORS para esta sub-app
        pdf_api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        pdf_api.include_router(pdf_router)

        # Montar la app en /api/pdf
        if hasattr(target_app, "mount"):
            target_app.mount("/api/pdf", pdf_api)
            print("[PDF-REGISTER] Rutas montadas exitosamente en /api/pdf usando .mount()")
        else:
            print("[PDF-REGISTER] Error: La app backend no soporta '.mount()'")

    except Exception as e:
        print(f"[PDF-REGISTER] Error critico registrando rutas: {str(e)}")
