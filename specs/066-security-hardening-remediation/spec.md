# Feature Specification: Remediación de Seguridad Integral — Hardening v2.0

**Feature Branch**: `security/066-security-hardening-remediation`

**Created**: 2026-07-28

**Status**: Draft

**Input**: Auditoría de seguridad consolidada v2.0 — JSUARCAR/inmo_velar (2 auditorías independientes, 20 hallazgos verificados en código fuente local y repositorio público)

---

## Contexto y Motivación

La auditoría de seguridad integral identificó **4 hallazgos críticos activos** que comprometen la confidencialidad total de los datos del negocio y el cumplimiento de la Ley 1581/2012 de Protección de Datos Personales de Colombia. Dos de estos hallazgos son explotables hoy sin credenciales por cualquier persona con acceso a internet.

Este feature abarca la remediación completa de los 20 hallazgos identificados, organizados en 4 fases de urgencia decreciente.

---

## Clarifications

### Session 2026-07-28

- Q: ¿El modelo de expiración de sesión es absoluto o deslizante (sliding)? → A: Absoluta — la sesión expira exactamente 8 horas desde su creación, sin importar la actividad del usuario. No se actualiza `fecha_fin` en cada petición.
- Q: ¿Qué roles tienen acceso a los endpoints de documentos? → A: Cualquier rol autenticado (sesión válida); el control granular es la verificación de relación entre el usuario y la entidad solicitada (IDOR check), no el rol en sí.
- Q: ¿Es necesario mantener `allow_credentials=True` en las sub-apps FastAPI de documentos y PDF una vez implementada la autenticación por cookie server-side? → A: No. Eliminar `allow_credentials=True` de ambas sub-apps (`pdf_download_api.py` y `document_download_api.py`); la validación de la cookie `_s` ocurre del lado del servidor, no requiere envío cross-origin de credenciales por el navegador.
- Q: ¿Qué mecanismo se usará para el rate limiting de login en producción? → A: Plugin `caddy-ratelimit` configurado con la directiva `rate_limit` en el `Caddyfile.runtime`, limitando por IP en la ruta del endpoint de autenticación; elimina la dependencia del diccionario en memoria de `auth_state.py` y funciona correctamente en entornos multi-réplica.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Protección Inmediata de Credenciales de Producción (Priority: P1)

Un administrador del sistema necesita garantizar que ninguna credencial de la base de datos de producción sea accesible públicamente, y que el historial de Git quede completamente depurado de cualquier secreto expuesto.

**Por qué esta prioridad**: Las credenciales de Railway/PostgreSQL están públicamente expuestas en el repositorio con acceso de superusuario (`postgres`). Cualquier persona puede conectarse a la BD de producción ahora mismo.

**Independent Test**: Ejecutar `git log --all --full-history -- check_db.py` y confirmar que el archivo no aparece en ningún commit. Intentar conectar con las credenciales anteriores debe resultar en rechazo.

**Acceptance Scenarios**:

1. **Given** credenciales antiguas de Railway, **When** se intenta conectar a la BD, **Then** la conexión es rechazada con error de autenticación
2. **Given** el repositorio público en GitHub, **When** se busca la contraseña anterior en cualquier archivo o commit, **Then** no se encuentra ninguna coincidencia
3. **Given** el código fuente del proyecto, **When** se busca cualquier contraseña hardcodeada, **Then** no se encuentra ninguna — solo referencias a variables de entorno

---

### User Story 2 — Control de Acceso en APIs de Documentos (Priority: P1)

Un usuario no autenticado intenta acceder a documentos del sistema (cédulas, contratos, pólizas). El sistema debe rechazar la petición con HTTP 401 sin exponer ningún dato.

**Por qué esta prioridad**: Los 4 endpoints `/api/documentos/*` y `/api/storage/*` no tienen ninguna protección. Es el hallazgo de mayor impacto en datos personales protegidos (Ley 1581/2012).

**Independent Test**: `curl` sin cookies a `/api/documentos/list/contrato/1` debe retornar HTTP 401. Con cookie de sesión válida debe retornar datos.

**Acceptance Scenarios**:

1. **Given** una petición sin cookie de sesión, **When** se accede a `/api/documentos/list/{tipo}/{id}`, **Then** el sistema responde HTTP 401
2. **Given** una petición sin cookie de sesión, **When** se accede a `/api/documentos/download/{id}`, **Then** el sistema responde HTTP 401
3. **Given** una petición sin cookie de sesión, **When** se accede a `/api/storage/{id}/download`, **Then** el sistema responde HTTP 401
4. **Given** una petición sin cookie, **When** se hace POST a `/api/documentos/upload/{tipo}/{id}`, **Then** el sistema responde HTTP 401
5. **Given** un usuario autenticado con sesión válida, **When** accede a `/api/documentos/download/{id}` de una entidad relacionada con su contexto, **Then** descarga el documento correctamente
6. **Given** un usuario autenticado, **When** intenta descargar un documento cuya `entidad_id` no tiene relación con ninguna entidad a la que el usuario tiene acceso, **Then** el sistema responde HTTP 403

---

### User Story 3 — Higiene del Repositorio Git (Priority: P2)

Un desarrollador que clona el repositorio no debe encontrar archivos de diagnóstico internos, volcados de esquema de BD, capturas de prueba con datos personales, ni scripts temporales.

**Por qué esta prioridad**: El volcado de esquema (`schema_extracted.json`, 178 KB) y las 183 capturas de `.playwright-mcp/` amplifican el impacto de los hallazgos críticos al proveer un mapa detallado del sistema.

**Independent Test**: Clonar el repositorio y verificar que los directorios de exclusión no existen. `git log --all --oneline -- migraciones/esquemas/` debe devolver cero resultados.

**Acceptance Scenarios**:

1. **Given** el repositorio clonado, **When** se busca `.playwright-mcp/`, **Then** el directorio no existe
2. **Given** el repositorio clonado, **When** se busca `migraciones/esquemas/`, **Then** el directorio no existe
3. **Given** el historial completo de Git, **When** se busca `schema_extracted.json`, **Then** no aparece en ningún commit
4. **Given** el repositorio, **When** se ejecuta `gitleaks detect --source .`, **Then** cero secretos encontrados

---

### User Story 4 — Configuración Segura de Infraestructura HTTP (Priority: P2)

Un usuario que accede a la aplicación recibe las cabeceras de seguridad HTTP estándar en todas las respuestas de producción.

**Por qué esta prioridad**: El `Caddyfile.runtime` generado en `entrypoint.sh` omite el bloque de cabeceras de seguridad que sí existe en el `Caddyfile` estático.

**Independent Test**: `curl -I https://inmovelar-production.up.railway.app` debe mostrar `Strict-Transport-Security`, `X-Frame-Options` y `X-Content-Type-Options`.

**Acceptance Scenarios**:

1. **Given** la aplicación en producción, **When** se hace cualquier petición HTTP, **Then** la respuesta incluye `Strict-Transport-Security: max-age=31536000; includeSubDomains`
2. **Given** la aplicación en producción, **When** se inspecciona una respuesta, **Then** incluye `X-Frame-Options: DENY`
3. **Given** la aplicación en producción, **When** se inspecciona una respuesta, **Then** incluye `X-Content-Type-Options: nosniff`
4. **Given** securityheaders.com, **When** se analiza la URL de producción, **Then** la calificación es A o superior

---

### User Story 5 — Configuración Fail-Fast de Variables de Entorno Críticas (Priority: P2)

El sistema no arranca si alguna variable de entorno crítica de seguridad no está configurada correctamente, en lugar de usar valores por defecto peligrosos.

**Por qué esta prioridad**: `settings.py` define `SECRET_KEY` con default `"CHANGE_ME_IN_PRODUCTION"`. El sistema arranca silenciosamente con clave predecible si no se configura.

**Independent Test**: Iniciar la aplicación sin `SECRET_KEY` en el entorno debe resultar en error de arranque con mensaje claro antes de aceptar conexiones.

**Acceptance Scenarios**:

1. **Given** un entorno sin `SECRET_KEY`, **When** se inicia la aplicación, **Then** el proceso termina con error descriptivo antes de aceptar conexiones
2. **Given** `SECRET_KEY=CHANGE_ME_IN_PRODUCTION`, **When** se inicia, **Then** el proceso termina con error indicando que se debe cambiar
3. **Given** un `SECRET_KEY` válido (≥32 bytes), **When** se inicia, **Then** arranca correctamente

---

### User Story 6 — Seguridad de Contenedor y Cadena de Suministro (Priority: P3)

El contenedor Docker de producción no ejecuta procesos como root, y los binarios de terceros descargados son verificados criptográficamente.

**Independent Test**: `docker run --rm <imagen> whoami` debe retornar un usuario no-root.

**Acceptance Scenarios**:

1. **Given** el contenedor de producción, **When** se ejecuta `whoami` dentro, **Then** el resultado es un usuario no-root
2. **Given** el Dockerfile, **When** se descarga Caddy, **Then** se verifica el hash SHA256 antes de instalarlo
3. **Given** un hash SHA256 incorrecto, **When** se construye la imagen, **Then** el build falla

---

### User Story 7 — Fortalecimiento de Sesiones y Autenticación (Priority: P3)

Las sesiones tienen duración máxima de 8 horas, el rate limiting funciona en entornos multi-réplica, y los logs no exponen tokens de sesión.

**Independent Test**: Token de sesión creado hace más de 8 horas debe ser rechazado con redirección al login.

**Acceptance Scenarios**:

1. **Given** una sesión de más de 8 horas, **When** el usuario realiza cualquier acción, **Then** es redirigido al login
2. **Given** 5 intentos fallidos de login, **When** se realiza un 6° intento en 15 minutos, **Then** el sistema bloquea (incluso post-reinicio del contenedor)
3. **Given** los logs de Railway en producción, **When** se busca cualquier token de sesión, **Then** no se encuentra ninguno en texto plano

---

### Edge Cases

- Sesiones sin `fecha_fin` existentes al deploy: se tratan como expiradas en el primer acceso, forzando re-login.
- Colaboradores con el repositorio clonado localmente: deben re-clonar después de la purga de historial Git.
- El usuario `app_velar` de mínimos privilegios debe validarse contra todas las operaciones existentes antes de revocar el acceso del usuario anterior.
- La rotación de credenciales debe ser zero-downtime: nuevas credenciales activas antes de revocar las anteriores.
- La imagen Docker usada en Railway DEBE incluir el plugin `caddy-ratelimit` compilado en el binario de Caddy; si se usa la descarga dinámica del binario oficial, se debe construir una imagen personalizada de Caddy con el plugin, o usar `xcaddy` en el build step.

---

## Requirements *(mandatory)*

### Functional Requirements

**Fase 1 — Emergencia (0–4 horas)**

- **FR-001**: El sistema DEBE rotar todas las credenciales de producción y crear usuario `app_velar` con privilegios mínimos (`SELECT, INSERT, UPDATE, DELETE` sobre tablas de la aplicación; sin `DROP`, `CREATE`, `ALTER`, `TRUNCATE`)
- **FR-002**: El sistema DEBE eliminar toda contraseña o cadena de conexión hardcodeada del código fuente, reemplazando con referencias a variables de entorno
- **FR-003**: El administrador DEBE revisar logs de acceso de Railway en `/api/documentos/*` y `/api/storage/*` buscando explotación previa

**Fase 2 — Urgente (24–72 horas)**

- **FR-004**: Los 4 endpoints de API REST de documentos DEBEN validar cookie de sesión activa retornando HTTP 401 si es inválida, vencida o inexistente; cualquier rol con sesión válida puede intentar el acceso
- **FR-005**: Los endpoints de documentos DEBEN verificar que la `entidad_id` o `documento_id` solicitado tenga relación con el usuario autenticado (IDOR check); si no existe relación, el sistema DEBE responder HTTP 403 sin revelar si el recurso existe
- **FR-006**: El historial completo de Git DEBE ser purgado de los 6 archivos con credenciales usando `git filter-repo` + force-push
- **FR-007**: Los archivos sensibles (`.playwright-mcp/`, `migraciones/esquemas/`, `outputs/`, `tasks/`, `skills/`, temporales) DEBEN ser eliminados del árbol y del historial
- **FR-008**: `settings.py` DEBE implementar validación fail-fast que impida el arranque si `SECRET_KEY` tiene el valor por defecto o está ausente
- **FR-009**: `rxconfig.py` DEBE eliminar el fallback `'7323'`; si `DATABASE_URL` está ausente, la aplicación DEBE fallar explícitamente

**Fase 3 — Importante (1–2 semanas)**

- **FR-010**: `entrypoint.sh` DEBE incluir en el `Caddyfile.runtime`: (a) el bloque completo de cabeceras HTTP (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, `-Server`), y (b) la directiva `rate_limit` del plugin `caddy-ratelimit` aplicada a la ruta del endpoint de autenticación, limitando a 5 intentos por IP en una ventana de 15 minutos
- **FR-010b**: El `Dockerfile` DEBE construir el binario de Caddy usando `xcaddy` incluyendo el plugin `github.com/mholt/caddy-ratelimit`, en lugar de descargar el binario oficial sin plugins
- **FR-011**: CORS en `pdf_download_api.py` y `document_download_api.py` DEBE restringir `allow_origins` a la lista explícita de dominios de producción, eliminando `"*"`; `allow_credentials` DEBE eliminarse (`False` o campo omitido) ya que la validación de la cookie `_s` es server-side y no requiere envío cross-origin de credenciales
- **FR-012**: `rxconfig.py` DEBE eliminar `"*"` de `cors_allowed_origins`
- **FR-013**: El `Dockerfile` DEBE crear y usar usuario no-root `appuser` para todos los procesos
- **FR-014**: El `Dockerfile` DEBE descargar Caddy a versión fija y verificar hash SHA256 antes de instalar
- **FR-015**: Las sesiones DEBEN tener `fecha_fin` establecida en el momento de creación como `fecha_inicio + 8 horas` (expiración absoluta); `fecha_fin` NO se actualiza en peticiones posteriores; toda validación de sesión DEBE rechazar tokens cuya `fecha_fin` sea anterior al momento actual
- **FR-016**: La función `_debug()` en `auth_state.py` DEBE estar completamente gateada por `IS_PROD`, sin exponer tokens en logs

**Fase 4 — Consolidación (1 mes)**

- **FR-017**: `requirements.txt` DEBE separarse en producción y desarrollo; `pyautogui` removido de producción
- **FR-018**: El pipeline CI DEBE incluir job `pip-audit` para detectar CVEs en dependencias de producción
- **FR-019**: `.pre-commit-config.yaml` DEBE incluir `gitleaks` o `detect-secrets` como hook bloqueante
- **FR-020**: Cuentas con hash SHA-256 legacy DEBEN ser identificadas y forzadas a resetear contraseña
- **FR-021**: El pipeline CI DEBE incluir job SAST con `bandit` o `semgrep` sobre código Python

### Restricciones y Reglas de Negocio

- **RN-001**: Credenciales rotadas en Railway DEBEN estar operativas antes de revocar las antiguas (zero-downtime rotation)
- **RN-002**: La purga del historial Git requiere notificación a todos los colaboradores; cualquier PR abierto contra el historial antiguo quedará inválido
- **RN-003**: El usuario `app_velar` DEBE tener acceso completo a todas las tablas en uso; validar con tests de integración antes de revocar acceso anterior
- **RN-004**: Los cambios a la capa de autenticación API DEBEN ser compatibles con el frontend Reflex existente; el mecanismo de cookie `_s` es el canal oficial

### Key Entities

- **Credencial**: Par usuario/contraseña o connection string. Nunca debe existir en código fuente.
- **Sesión de Usuario**: Token opaco de 32 bytes URL-safe, con `fecha_inicio` y `fecha_fin` fija (= `fecha_inicio + 8 horas`, expiración absoluta). `fecha_fin` no se modifica después de la creación.
- **Endpoint Protegido**: Ruta de API que requiere sesión válida y permisos de rol antes de procesar.
- **Cabecera de Seguridad HTTP**: Directiva que instruye al navegador sobre política de seguridad.
- **Historial de Git**: Registro inmutable de commits. Purga con `git filter-repo` requiere re-clonado de todos los colaboradores.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cero credenciales encontradas por `gitleaks detect --source .` en repositorio completo (incluyendo historial)
- **SC-002**: Los 4 endpoints de documentos retornan HTTP 401 en el 100% de peticiones sin sesión válida
- **SC-003**: Calificación A o superior en securityheaders.com para la URL de producción
- **SC-004**: El contenedor de producción ejecuta procesos con usuario no-root (verificable con `whoami`)
- **SC-005**: `pip-audit` contra dependencias de producción reporta cero CVEs conocidos
- **SC-006**: Sesiones cuya `fecha_fin` sea anterior al momento actual son rechazadas con HTTP 401; el plazo máximo absoluto desde creación es 8 horas sin excepción
- **SC-007**: La aplicación no arranca si `SECRET_KEY=CHANGE_ME_IN_PRODUCTION` o `DATABASE_URL` está ausente
- **SC-008**: El repositorio clonado no contiene archivos en `.playwright-mcp/`, `migraciones/esquemas/`, ni `outputs/`
- **SC-009**: Puntuación de madurez de seguridad global ≥ 7.5/10 en re-auditoría posterior
- **SC-010**: Cero incidentes de acceso no autorizado a documentos en logs de Railway en los 30 días post-deploy

---

## Assumptions

- Las credenciales de Railway se están rotando de forma inmediata, en paralelo con este spec (acción de emergencia).
- El repositorio tiene un único colaborador activo actualmente; la coordinación del force-push es manejable.
- El usuario `app_velar` se crea en Railway PostgreSQL antes de desplegar el cambio de `DATABASE_URL`.
- El mecanismo de cookie `_s` usado por `AuthState` puede reutilizarse como dependencia en los endpoints FastAPI sin cambios en el frontend.
- Redis no está disponible en el stack actual; el rate limiting se implementa con el plugin `caddy-ratelimit` directamente en el `Caddyfile.runtime`, configurado como directiva `rate_limit` que limita por IP en la ruta de autenticación (5 req/15 min). El binario de Caddy se construye con `xcaddy` para incluir el plugin.
- La expiración de sesiones de 8 horas es el valor acordado para el negocio; puede ajustarse post-implementación.
- El SAST con `bandit` se ejecuta sobre `src/` excluyendo `venv/` y `__pycache__/`.
