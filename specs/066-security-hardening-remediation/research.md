# Research: Remediación de Seguridad Integral — Hardening v2.0

**Fecha**: 2026-07-28
**Feature**: specs/066-security-hardening-remediation

---

## 1. xcaddy + caddy-ratelimit en Dockerfile

**Decisión**: Multi-stage build con `caddy:2-builder` + `xcaddy` para compilar el binario de Caddy con el plugin `github.com/mholt/caddy-ratelimit`. La imagen final usa `caddy:2-alpine`.

**Justificación**: Build reproducible sin arrastrar el entorno Go a producción. El rate limiting a nivel de Caddy descarta peticiones antes de llegar al event-loop de Python, ahorrando recursos del backend.

**Dockerfile (etapas relevantes)**:
```dockerfile
# Etapa 1: Builder
FROM caddy:2-builder AS caddy_builder
RUN xcaddy build --with github.com/mholt/caddy-ratelimit

# Etapa 2 (en Dockerfile principal): copiar binario compilado
COPY --from=caddy_builder /usr/bin/caddy /usr/local/bin/caddy
```

**Configuración Caddyfile.runtime (directiva rate_limit)**:
```caddyfile
{
    order rate_limit before static_response
}

:${PORT:-8080} {
    @login_attempt {
        path /_event/*
        method POST
    }
    rate_limit @login_attempt {
        zone login_limit {
            key {remote_host}
            events 5
            window 15m
        }
    }
    # ... resto de bloques (header, reverse_proxy, file_server)
}
```

**Alternativas descartadas**:
- `slowapi` en FastAPI: consume recursos Python antes de rechazar; Caddy es más eficiente
- Binario precompilado sin plugin: no incluye rate_limit, requiere descarga dinámica insegura

---

## 2. FastAPI Depends() para cookie en sub-app montada

**Decisión**: Función de dependencia `validar_sesion_api()` que extrae la cookie `_s` vía `Cookie(alias="_s")` de FastAPI y llama a `ServicioAutenticacion.validar_sesion()`. Se inyecta como dependencia global en el constructor de la sub-app `FastAPI(dependencies=[Depends(validar_sesion_api)])`.

**Justificación**: La sub-app montada vía `.mount()` recibe el scope ASGI completo incluyendo el header `Cookie`. La cookie `_s` con `Path=/` es enviada por el navegador en todas las peticiones al dominio, incluyendo `/api/storage/*` y `/api/documentos/*`. El patrón `dependencies=[...]` en el constructor aplica la dependencia a todos los endpoints sin modificar cada firma individualmente.

**Patrón de código**:
```python
from fastapi import FastAPI, Depends, Cookie, HTTPException, status
from typing import Annotated

async def validar_sesion_api(
    _s: Annotated[str | None, Cookie(alias="_s")] = None
) -> dict:
    if not _s:
        raise HTTPException(status_code=401, detail="Sesión requerida")
    from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
    # ... instanciar servicio y validar token
    return usuario

# Sub-app con dependencia global
doc_api = FastAPI(dependencies=[Depends(validar_sesion_api)])
```

**IDOR check adicional** (FR-005): después de autenticar, verificar que `entidad_id` o `documento_id` pertenece al ámbito de datos accesible por el usuario. Si no hay relación: HTTP 403 sin revelar existencia del recurso.

**Alternativas descartadas**:
- Middleware en `main_app`: dificulta inyección tipada del objeto Usuario
- Header `Authorization: Bearer`: rompe compatibilidad con cookies HttpOnly existentes

---

## 3. git filter-repo — Flujo de purga de secretos

**Decisión**: Usar `git filter-repo --invert-paths` sobre un clon fresco del repositorio. Purgar 6 archivos con credenciales + directorios de archivos sensibles.

**Precondiciones obligatorias**:
1. Rotar credenciales en Railway ANTES de purgar (la purga no invalida secretos ya expuestos)
2. Crear backup mirror: `git clone --mirror https://github.com/JSUARCAR/inmo_velar.git inmo_velar_backup`
3. Desactivar Branch Protection en GitHub temporalmente

**Comandos exactos**:
```bash
# Clon fresco
git clone https://github.com/JSUARCAR/inmo_velar.git inmo_velar_clean
cd inmo_velar_clean

# Purgar archivos con credenciales
git filter-repo --invert-paths \
    --path check_db.py \
    --path check_db_id.py \
    --path migraciones/run_migration_ipc.py \
    --path migraciones/migrate_to_railway.py \
    --path migraciones/AGREGAR_A_ENV.txt \
    --path migraciones/GUIA_RAPIDA.txt

# Purgar directorios sensibles
git filter-repo --invert-paths \
    --path .playwright-mcp \
    --path migraciones/esquemas \
    --path outputs

# Re-añadir remote (git filter-repo lo elimina por seguridad)
git remote add origin https://github.com/JSUARCAR/inmo_velar.git

# Verificar purga
git log --all --full-history -- check_db.py  # debe devolver vacío

# Force-push
git push origin --force --all
git push origin --force --tags
```

**Post-push**: Notificar a todos los colaboradores que deben re-clonar. Verificar con gitleaks.

**Alternativas descartadas**:
- `git filter-branch`: deprecated, lento, propenso a corrupción
- `BFG Repo-Cleaner`: menos mantenido que git filter-repo

---

## 4. Pydantic v2 field_validator Fail-Fast

**Decisión**: `@field_validator("secret_key", mode="after")` en `Settings(BaseSettings)` que lanza `ValueError` si el valor es el default inseguro, está vacío, o tiene menos de 32 caracteres. El `Settings()` se instancia al importar el módulo envuelto en `try/except` que llama `sys.exit(1)`.

**Patrón de código**:
```python
import sys
from pydantic import field_validator
from pydantic_settings import BaseSettings

CLAVES_INSEGURAS = {"CHANGE_ME_IN_PRODUCTION", "change_me", "secret", "development"}

class Settings(BaseSettings):
    secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION", ...)

    @field_validator("secret_key", mode="after")
    @classmethod
    def validar_secret_key(cls, v: str) -> str:
        if not v or v.strip() in CLAVES_INSEGURAS or len(v) < 32:
            raise ValueError(
                "CRÍTICO: SECRET_KEY no configurada o usa valor inseguro. "
                "Configure una cadena aleatoria de al menos 32 caracteres en Railway Variables."
            )
        return v

# Fail-fast al importar
try:
    _settings_instance = Settings()
except Exception as err:
    print(f"\n[ERROR FATAL DE CONFIGURACIÓN]\n{err}\n", file=sys.stderr)
    sys.exit(1)
```

**Consideración**: El `sys.exit(1)` a nivel de módulo interrumpe el arranque del proceso antes de que Reflex abra cualquier puerto.

**Alternativas descartadas**:
- Validación diferida en endpoints: permite arranque con clave insegura
- `@validator` Pydantic v1: obsoleto en el stack actual (Pydantic v2)

---

## 5. Mínimos Privilegios PostgreSQL — Usuario app_velar

**Decisión**: Crear `app_velar` con solo permisos DML (`SELECT, INSERT, UPDATE, DELETE`) sobre todas las tablas del schema `public`. Sin `DROP`, `CREATE`, `ALTER`, `TRUNCATE`. Usar `ALTER DEFAULT PRIVILEGES` para tablas futuras.

**SQL exacto**:
```sql
-- Crear usuario dedicado
CREATE USER app_velar WITH PASSWORD 'nueva_clave_segura_aqui';

-- Revocar accesos PUBLIC innecesarios
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Otorgar conexión y uso del schema
GRANT CONNECT ON DATABASE railway TO app_velar;
GRANT USAGE ON SCHEMA public TO app_velar;

-- Permisos DML sobre tablas existentes
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_velar;

-- Permisos sobre secuencias (SERIAL/IDENTITY columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_velar;

-- Permisos automáticos para tablas y secuencias FUTURAS
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_velar;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO app_velar;
```

**Alternativas descartadas**:
- Mantener usuario `postgres` (superusuario): viola OWASP A07, impacto total ante compromiso
- `GRANT ALL ON ALL TABLES`: incluye TRUNCATE y REFERENCES innecesarios

---

## 6. Cabeceras HTTP de Seguridad en Caddyfile.runtime

**Decisión**: Modificar `entrypoint.sh` para que el heredoc del `Caddyfile.runtime` incluya el bloque `header` con las 5 directivas de seguridad.

**Bloque a insertar en entrypoint.sh**:
```caddyfile
header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains"
    X-Frame-Options "DENY"
    X-Content-Type-Options "nosniff"
    Referrer-Policy "strict-origin-when-cross-origin"
    -Server
}
```

**Ubicación**: Dentro del bloque `handle { ... }` del file_server, ANTES del bloque `@html`.

---

## 7. Usuario no-root en Dockerfile

**Decisión**: Añadir instrucciones `RUN addgroup/adduser` y `USER appuser` en el Dockerfile, después de instalar dependencias y ANTES del CMD.

**Patrón**:
```dockerfile
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --no-create-home appuser

# Cambiar propietario de archivos de la app
RUN chown -R appuser:appgroup /app

USER appuser
CMD ["/bin/bash", "/app/entrypoint.sh"]
```

**Consideración**: Caddy necesita enlazarse al puerto indicado por `$PORT` (≥1024 en Railway). Si Railway asigna puerto <1024, se requiere `CAP_NET_BIND_SERVICE`. En Railway, `$PORT` es típicamente 8080 (>1024), así que no hay problema.
