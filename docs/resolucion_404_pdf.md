# Resolución del Error 404 en Descarga de PDF

**Fecha**: 2026-09-03
**Característica**: Investigacion de Error 404 en Descarga de PDF

## Resumen del Problema
Los usuarios reportaron un error "404 Not Found" sistemático al intentar descargar los documentos de "Contrato de Mandato" y "Contrato de Arrendamiento" desde el módulo de Contratos.

## Causa Raíz Identificada
Mediante ingeniería inversa se determinó que el error 404 no se debía a que los archivos faltaran en el disco temporal, sino a que **el sub-enrutador de FastAPI (`pdf_api`) no se estaba montando exitosamente** en la aplicación Reflex.

1. **Imports Rotos**: El archivo `src/presentacion_reflex/api/deps.py` estaba importando `RepositorioSesion` y `RepositorioUsuario` desde la ruta obsoleta `src.infraestructura.repositorios` en lugar de `src.infraestructura.persistencia`. Esto generaba un `ModuleNotFoundError`.
2. **Fallos Silenciosos**: El módulo `pdf_download_api.py` capturaba cualquier error de montaje mediante un bloque `try...except` que únicamente imprimía el error mediante `print()`, haciendo imposible su detección temprana durante el inicio del servidor sin monitorear directamente los logs estándar de la terminal.

Al fallar el montaje, la ruta `/api/pdf/download/{filename}` literalmente no existía, provocando que Reflex/FastAPI devolviera un 404.

## Solución Arquitectónica Implementada

Se realizó una intervención end-to-end (desde infraestructura de enrutamiento hasta políticas de seguridad):

1. **Corrección de Dependencias**: 
   - Se actualizaron las sentencias de importación en `deps.py` al namespace correcto de persistencia para posibilitar el montaje del enrutador.

2. **Fortalecimiento de Seguridad y CORS**:
   - Se actualizó el `CORSMiddleware` para aceptar `allow_credentials=True`.
   - Se limitaron los orígenes permitidos estrictamente a Producción (`FRONTEND_URL`) y `localhost:3000`.
   - Se implementó un algoritmo estricto de prevención de inyección de directorios (**Path Traversal**) utilizando `pathlib.Path.resolve().is_relative_to()`.
   - Se implementó URL-decode en los endpoints para soportar nombres de archivos con caracteres especiales (ej. espacios).

3. **Prevención de Abusos (DoS)**:
   - Se desarrolló un middleware en-memoria de **Rate Limiting** que restringe a cada usuario a un máximo de 10 descargas por minuto (Retorna `HTTP 429`).

4. **Tolerancia a Fallos y Registro (Logging)**:
   - Los fallos de montaje ahora emiten un log de nivel `CRITICAL` que será visible en las herramientas modernas de APM.
   - Si un archivo físico fue purgado (True 404), el sistema retorna 404 explícitamente y de manera controlada.
   - Ante errores internos no controlados, el sistema responderá con `HTTP 500` mediante un payload JSON estructurado para fácil interpretación por parte de la UI frontend.

## Validación y Pruebas
Se construyó una nueva suite de pruebas de integración (`tests/integracion/api/test_pdf_download_api.py`) comprobando exitosamente:
- Descarga correcta (HTTP 200).
- Excepción de sesión ausente (HTTP 401).
- Error por archivo inexistente (HTTP 404 controlada).
- Rate Limiting superado (HTTP 429).
- Prevención de Path Traversal (Rechazo HTTP 403).
