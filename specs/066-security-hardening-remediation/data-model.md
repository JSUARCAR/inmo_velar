# Data Model: Remediación de Seguridad Integral — Hardening v2.0

**Feature**: specs/066-security-hardening-remediation
**Fecha**: 2026-07-28

---

## Entidades Afectadas

### 1. SesionUsuario (modificación)

**Archivo**: `src/dominio/entidades/sesion_usuario.py`

| Campo | Tipo | Regla de Validación |
|-------|------|---------------------|
| `id_sesion` | `Optional[int]` | Auto-generado por BD |
| `id_usuario` | `int` | FK a `usuarios.id` — requerido |
| `token_sesion` | `str` | `secrets.token_urlsafe(32)` — único, no predecible |
| `fecha_inicio` | `str` | ISO 8601 — timestamp de creación |
| `fecha_fin` | `str` | **NUEVO** — `fecha_inicio + 8 horas` en ISO 8601; NUNCA `None`; NUNCA modificado post-creación |
| `activa` | `bool` | `True` al crear; `False` al cerrar sesión explícitamente |

**Transiciones de estado**:
```
CREADA (activa=True, fecha_fin=+8h)
    → EXPIRADA: cuando datetime.now() >= fecha_fin  [automático en validación]
    → CERRADA: cuando usuario hace logout  [activa=False]
```

**Regla de validación** (`esta_activa()`):
```python
def esta_activa(self) -> bool:
    if not self.activa:
        return False
    if self.fecha_fin:
        return datetime.fromisoformat(self.fecha_fin) > datetime.now()
    return False  # Sin fecha_fin → inválida (fail-safe)
```

---

### 2. Settings (modificación)

**Archivo**: `src/infraestructura/configuracion/settings.py`

| Campo | Regla Anterior | Regla Nueva |
|-------|---------------|-------------|
| `secret_key` | `default="CHANGE_ME_IN_PRODUCTION"` | Validator fail-fast: rechaza si vacía, <32 chars, o en lista `CLAVES_INSEGURAS` |
| `db_user` | `default="postgres"` | Sin cambio (la validación es en Railway, no en código) |
| `db_password` | `default=""` | Sin cambio (eliminado fallback de rxconfig.py) |

**Nuevas constantes**:
```python
CLAVES_INSEGURAS: frozenset[str] = frozenset({
    "CHANGE_ME_IN_PRODUCTION",
    "change_me",
    "secret",
    "development",
    "12345678901234567890123456789012",
})
```

---

### 3. Endpoints de API REST (contratos modificados)

**Archivos**: `src/presentacion_reflex/api/documentos_api.py`, `document_download_api.py`

#### Dependencia de autenticación compartida

```
ServicioAutenticacion.validar_sesion(token) → Usuario
    ├── token ausente → HTTP 401 "Sesión requerida"
    ├── token inválido/no encontrado → HTTP 401 "Sesión inválida"
    ├── sesion.fecha_fin < now() → HTTP 401 "Sesión expirada"
    └── sesion válida → Usuario (con id_usuario, rol, nombre)
```

#### IDOR Check (FR-005)

```
Verificar relación usuario ↔ entidad_id:
    ├── entidad relacionada al usuario → procesar petición
    └── sin relación → HTTP 403 "Sin acceso al recurso"
        (sin revelar si el recurso existe)
```

**Nota de implementación**: La verificación de IDOR se delega al `ServicioDocumentalElite` que ya tiene acceso al repositorio. El servicio debe aceptar `id_usuario` como parámetro adicional y lanzar `PermisoDenegado` si no hay relación.

---

### 4. Dockerfile — Entidades de Build

| Componente | Estado Actual | Estado Objetivo |
|-----------|--------------|----------------|
| Imagen base | `python:3.11-slim` (única etapa) | Multi-stage: `caddy:2-builder` + `python:3.11-slim` |
| Binario Caddy | Descarga dinámica sin hash | Compilado con `xcaddy` + plugin `caddy-ratelimit` |
| Usuario runtime | `root` (implícito) | `appuser` (UID 1001, sin shell, sin home) |

---

### 5. Variables de Entorno Requeridas (contrato de Railway)

| Variable | Uso | ¿Falla sin ella? |
|----------|-----|-----------------|
| `SECRET_KEY` | Firma criptográfica | **Sí** — fail-fast en arranque |
| `DATABASE_URL` | Conexión a PostgreSQL | **Sí** — fail-fast en arranque |
| `RAILWAY_ENVIRONMENT` | Detección de entorno prod | No (defaults a dev) |
| `RAILWAY_STATIC_URL` | URL pública de la app | No (fallback hardcoded) |

---

### 6. Archivos Purgados del Repositorio

Los siguientes archivos dejan de existir en el árbol de trabajo Y en el historial de Git:

| Archivo/Directorio | Motivo | Acción |
|--------------------|--------|--------|
| `check_db.py` | Credenciales producción | `git filter-repo --invert-paths` |
| `check_db_id.py` | Credenciales producción | `git filter-repo --invert-paths` |
| `migraciones/run_migration_ipc.py` | Credenciales producción | `git filter-repo --invert-paths` |
| `migraciones/migrate_to_railway.py` | Credenciales producción | `git filter-repo --invert-paths` |
| `migraciones/AGREGAR_A_ENV.txt` | Contraseña `7323` | `git filter-repo --invert-paths` |
| `migraciones/GUIA_RAPIDA.txt` | Contraseña `7323` | `git filter-repo --invert-paths` |
| `.playwright-mcp/` | 183 capturas con datos personales | `git rm -r --cached` + filter-repo |
| `migraciones/esquemas/` | Volcado BD 178KB | `git rm -r --cached` + filter-repo |
| `outputs/` | PDFs de prueba, debug logs | `git rm -r --cached` + filter-repo |

---

### 7. CORS — Configuración Objetivo

| Archivo | `allow_origins` actual | `allow_origins` objetivo | `allow_credentials` objetivo |
|---------|----------------------|------------------------|----------------------------|
| `pdf_download_api.py` | `["*"]` | `["https://inmovelar-production.up.railway.app"]` | `False` (eliminado) |
| `document_download_api.py` | `["*"]` | `["https://inmovelar-production.up.railway.app"]` | `False` (eliminado) |
| `rxconfig.py` | `["*", "http://localhost:3000", ...]` | `["http://localhost:3000", "https://inmovelar-production.up.railway.app", "https://extraordinary-joy-production-2fd2.up.railway.app"]` | N/A (Reflex config) |
