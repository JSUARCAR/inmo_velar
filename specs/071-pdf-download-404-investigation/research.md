# PDF Download 404 Error - Research Findings

## Technical Context Unknowns Resolved

### 1. File System Persistence on Railway
**Decision**: Rely on ephemeral container storage for immediate downloads.
**Rationale**: The PDF generation and download happen sequentially in the same user session. While Railway containers have ephemeral filesystems (wiped on redeploy), the immediate download pattern does not require persistent volumes. 
**Alternatives considered**: Setting up an S3 bucket or a Railway persistent volume. Rejected because it adds unnecessary infrastructure complexity for files that are meant to be downloaded immediately and not stored permanently on the application server.

### 2. Reflex/FastAPI Routing in Production
**Decision**: Fix broken imports in src/presentacion_reflex/api/deps.py to allow successful route mounting.
**Rationale**: Reverse engineering revealed that app._api.mount() is supported, but the PDF routes are **never mounted** because register_pdf_routes(app) catches a ModuleNotFoundError during the import of validar_sesion_api. Specifically, deps.py attempts to import RepositorioSesion and RepositorioUsuario from src.infraestructura.repositorios, but these modules reside in src.infraestructura.persistencia. The try...except block silently catches this and aborts mounting, causing the server to return 404 Not Found for any /api/pdf/download/* request.
**Alternatives considered**: Moving route registration outside of the app lifecycle. Rejected because the root cause is a simple broken import that needs fixing.

### 3. CORS and Authentication for PDF Downloads
**Decision**: Update CORSMiddleware configuration in pdf_download_api.py to allow_credentials=True.
**Rationale**: The frontend fetch request uses credentials: 'include' to pass the session cookie _s. However, the sub-app's CORSMiddleware explicitly sets allow_credentials=False. While same-origin requests might bypass strict CORS preflight checks, local development testing will fail or block the cookie. 
**Alternatives considered**: Changing the frontend fetch to omit credentials. Rejected because validar_sesion_api strictly requires the _s cookie to authorize the download, ensuring PDFs cannot be downloaded by unauthorized users.

### 4. CORS Origins and Validation
**Decision**: Enforce explicit origin matching using environment variables (`FRONTEND_URL`) and `http://localhost:3000`.
**Rationale**: Because `allow_credentials=True` is required (to receive the `_s` cookie), the HTTP standard forbids using `allow_origins=["*"]`. We must explicitly declare the origins to prevent CSRF and cross-origin leakage.
**Alternatives considered**: Using wildcard domains (`*.velar.com`). Rejected as less secure than exact matching.

### 5. Path Traversal Prevention
**Decision**: Use `pathlib.Path.resolve().is_relative_to(BASE_DIR)` to validate the requested filename.
**Rationale**: Exposing a file download endpoint by concatenating `BASE_DIR + filename` is vulnerable to Path Traversal (`../../etc/passwd`). Validating the resolved path ensures the file resides exactly inside the `documentos_generados` directory.
**Alternatives considered**: Using regex to validate filename characters. Rejected as `is_relative_to` is the standard and safest Pythonic approach for path containment.

### 6. Rate Limiting Strategy
**Decision**: Implement a fixed-window or token-bucket rate limiter per session/IP (e.g., max 10 requests per minute).
**Rationale**: Generating and serving PDFs can consume significant CPU/Mem resources. A rate limiter prevents DoS attacks from automated scraping or accidental infinite loops in the frontend.
**Alternatives considered**: No rate limiting. Rejected because it exposes the application to resource exhaustion on Railway.

## Conclusion
The 404 error is definitively caused by a silent failure during backend initialization (broken imports in `deps.py`), preventing the `/api/pdf/download/{filename}` route from being registered. Fixing the imports, adjusting the CORS credentials and origins, securing the path retrieval against Traversal, and adding Rate Limiting will fully resolve the issue and ensure the endpoint is production-ready.
