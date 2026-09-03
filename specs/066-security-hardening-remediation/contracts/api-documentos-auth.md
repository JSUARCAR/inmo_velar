# Contrato: API de Documentos — Endpoints Protegidos

**Feature**: 066-security-hardening-remediation
**Archivo fuente**: `src/presentacion_reflex/api/documentos_api.py`, `document_download_api.py`

---

## Dependencia de Autenticación Global

Todos los endpoints listados abajo requieren la cookie `_s` (HttpOnly, SameSite=Lax/Strict).

**Función de dependencia** (compartida entre ambas sub-apps):
```
Cookie: _s=<token_urlsafe_32_bytes>
```

| Condición | Respuesta |
|-----------|-----------|
| Cookie `_s` ausente | `HTTP 401` `{"detail": "Sesión requerida"}` |
| Token inválido o no encontrado en BD | `HTTP 401` `{"detail": "Sesión inválida"}` |
| `sesion.fecha_fin < datetime.now()` | `HTTP 401` `{"detail": "Sesión expirada"}` |
| Sesión válida | Continúa al IDOR check |

---

## Endpoints

### POST /api/documentos/upload/{entidad_tipo}/{entidad_id}

**Autenticación**: ✅ Requerida (cookie `_s`)
**Autorización**: IDOR check — el usuario debe tener relación con `entidad_id`

**Path params**:
- `entidad_tipo`: `str` — tipo de entidad (`contrato`, `persona`, `propiedad`, etc.)
- `entidad_id`: `str` — ID de la entidad

**Form data**:
- `file`: `UploadFile` — archivo a subir (requerido)
- `usuario`: `str` — se ignora; el usuario se extrae de la sesión autenticada

**Respuestas**:
| Status | Body | Condición |
|--------|------|-----------|
| `200` | `{"status": "success", "id": int, "filename": str}` | Éxito |
| `400` | `{"detail": str}` | Validación de archivo fallida |
| `401` | `{"detail": "Sesión requerida/inválida/expirada"}` | Sin sesión |
| `403` | `{"detail": "Sin acceso al recurso"}` | IDOR check falla |
| `500` | `{"detail": "Error interno"}` | Error inesperado |

---

### GET /api/documentos/list/{entidad_tipo}/{entidad_id}

**Autenticación**: ✅ Requerida
**Autorización**: IDOR check

**Respuestas**:
| Status | Body | Condición |
|--------|------|-----------|
| `200` | `[{"id": int, "filename": str, "version": int, "created_at": str, "size_kb": float}]` | Éxito |
| `401` | `{"detail": "..."}` | Sin sesión válida |
| `403` | `{"detail": "Sin acceso al recurso"}` | Sin relación |

---

### GET /api/documentos/download/{documento_id}

**Autenticación**: ✅ Requerida
**Autorización**: IDOR check — `documento_id` debe pertenecer a entidad accesible por el usuario

**Respuestas**:
| Status | Body | Condición |
|--------|------|-----------|
| `200` | `binary` (Content-Type según MIME) | Éxito |
| `401` | `{"detail": "..."}` | Sin sesión |
| `403` | `{"detail": "Sin acceso al recurso"}` | Sin relación |
| `404` | `{"detail": "Documento no encontrado"}` | No existe (solo si autenticado y autorizado) |

---

### GET /api/storage/{id_documento}/download

**Sub-app**: `document_download_api.py` montada en `/api/storage`
**Autenticación**: ✅ Requerida (dependencia global en constructor `FastAPI(dependencies=[...])`)

**Respuestas**:
| Status | Body | Condición |
|--------|------|-----------|
| `200` | `binary` + `Content-Disposition` header | Éxito |
| `401` | `{"detail": "Sesión requerida"}` | Sin cookie `_s` |
| `404` | `{"detail": "Documento no encontrado o sin contenido"}` | No existe (solo si autenticado) |

---

## CORS — Configuración Post-Remediación

Aplica a ambas sub-apps (`pdf_download_api.py`, `document_download_api.py`):

```python
CORSMiddleware(
    allow_origins=["https://inmovelar-production.up.railway.app"],
    allow_credentials=False,  # Eliminado — validación server-side
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```
