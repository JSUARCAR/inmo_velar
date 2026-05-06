from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import Response

from src.infraestructura.repositorios.repositorio_documento import RepositorioDocumento

# Router para descargas de documentos genéricos (DB BLOBs)
document_download_router = APIRouter(tags=["Document Downloads"])


@document_download_router.get("/{id_documento}/download")
async def download_document(id_documento: int, force_download: bool = False):
    """
    Endpoint para descargar documentos almacenados como BLOB en la BD.
    Sirve para visualizar imágenes y descargar archivos.
    """
    try:
        repo = RepositorioDocumento()
        # Usamos el método explícito que trae el contenido (BLOB)
        documento = repo.obtener_por_id_con_contenido(id_documento)

        if not documento or not documento.contenido:
            raise HTTPException(status_code=404, detail="Documento no encontrado o sin contenido")

        # Determinar disposición (inline para preview, attachment para descarga forzada)
        disposition_type = "attachment" if force_download else "inline"
        content_disposition = f'{disposition_type}; filename="{documento.nombre_archivo}"'

        return Response(
            content=documento.contenido,
            media_type=documento.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": content_disposition,
                "Cache-Control": "public, max-age=3600",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def register_document_routes(app):
    """
    Registra las rutas de documentos en la aplicación FastAPI/Starlette de Reflex.
    """
    fastapi_app = getattr(app, "api", getattr(app, "_api", None))

    if fastapi_app:
        # Sub-app para aislamiento similar a pdf_download_api
        doc_api = FastAPI()

        from fastapi.middleware.cors import CORSMiddleware

        doc_api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        doc_api.include_router(document_download_router)

        try:
            if hasattr(fastapi_app, "mount"):
                fastapi_app.mount("/api/storage", doc_api)
                print("[STORAGE-REGISTER] Rutas de Documentos montadas exitosamente en /api/storage")
            else:
                print("[STORAGE-REGISTER] Error: La app backend no soporta 'mount'")
        except Exception as e:
            print(f"[STORAGE-REGISTER] Error registrando rutas de documentos: {e}")
