# Feature Specification: Fix Caddy Rate Limit Parsing Error

## Objective
To resolve the root cause of the Caddyfile parsing error in the deployment pipeline, which prevents Caddy from starting due to a malformed `rate_limit` directive.

## Clarifications
### Session 2026-09-02
- Q: Sintaxis del Plugin Rate Limit → A: Implementar zona `login_limit` con `key {client_ip}` (ver Q12; decisión final sobre la clave), `window 15m`, `events 5` y un bloque `match` para las rutas de login.
- Q: Comportamiento fallback si el plugin rate-limit falla → A: Fail-open. Caddy arranca sin rate limiting si el plugin falla; la disponibilidad prima sobre la seguridad del rate limit.
- Q: Identificación de cliente detrás de proxy → A: Usar `{client_ip}` como clave (ver Q12 y Q15; decisión final sobre clave y trusted_proxies). Railway inyecta la cabecera con la IP del cliente pero, al no configurar `trusted_proxies`, Caddy resuelve `{client_ip}` a la IP de conexión remota.
- Q: Logging/alertas al alcanzar umbral de rate limit → A: Confiar en el logging nativo de Caddy (respuestas 429 en stdout). Sin configuración adicional; Railway captura los logs.
- Q: Usuarios legítimos en redes compartidas (NAT/Corporativas) → A: Aceptar y documentar la limitación. El umbral de 5/15m es suficiente para uso corporativo normal.
- Q: Rollback si la nueva sintaxis rompe otras reglas del proxy → A: Rollback vía `git revert` del commit; Railway re-despliega automáticamente la versión anterior.
- Q: Formato de respuesta al exceder límite de rate limit (429) → A: Respuesta JSON estructurada con código HTTP 429 y payload `{"detail": "Demasiados intentos de inicio de sesión"}`.
- Q: Manejo si X-Forwarded-For no está presente → A: Fallback automático a la IP de conexión remota vía `{client_ip}` cuando no hay proxy de confianza (ver Q12; decisión final).
- Q: Alcance de rutas/eventos en bloque match → A: Proteger exhaustivamente `/api/login*`, `/api/auth*`, `/_event/auth_state.login*` y `/_event/estado_autenticacion.iniciar_sesion*`.
- Q: Tratamiento de X-Forwarded-For con múltiples IPs → A: Usar `{client_ip}` como clave. *Nota Q15*: al NO configurar `trusted_proxies`, Caddy resuelve la clave a la IP de conexión remota (no extrae la IP originaria del cliente). Ver Q15 para la decisión final.
- Q: Posicionamiento y orden del middleware en Caddy → A: Mantener `{ order rate_limit before basicauth }` en las opciones globales para asegurar prioridad antes de la autenticación.
- Q: Mecanismo de extracción de la "primera IP" del cliente → A: Usar el placeholder nativo de Caddy `{client_ip}` como clave. Sustituye la cabecera cruda `{http.request.header.X-Forwarded-For}` (que devolvería la lista completa con comas). *Nota Q15*: NO se configura `trusted_proxies` (Railway sin rango estable), por lo que `{client_ip}` se resuelve a la IP de conexión remota (nivel contenedor, no por usuario final).
- Q: ¿Debe el Definition of Done verificar el comportamiento 429? → A: Sí. El DoD debe incluir la verificación explícita de que al superar el umbral (5 intentos/15m) Caddy devuelve HTTP 429 con el payload JSON `{"detail": "Demasiados intentos de inicio de sesión"}` y `Content-Type: application/json`, no solo el arranque exitoso.
- Q: Persistencia del estado del rate limit entre reinicios → A: Aceptar contadores en memoria del proceso (plugin `mholt/caddy-ratelimit`). Se resetean en cada reinicio/redeploy de Caddy; se documenta como limitación conocida. Railway opera con 1 réplica, por lo que no aplica el problema de contadores compartidos entre nodos. Sin almacén externo.
- Q: Valor de `trusted_proxies` para Railway → A: NO declarar `trusted_proxies` (Railway usa un edge AWS dinámico sin rango público estable; `private_ranges` no lo cubre). En consecuencia, `{client_ip}` se resuelve a la IP de la conexión remota (la IP interna del contenedor/ingress de Railway con 1 réplica). **Implicación**: el rate limit NO aplica por usuario final detrás del proxy, sino a nivel del contenedor/ingress (todas las peticiones comparten el contador). Se documenta como limitación conocida de seguridad: la protección es efectiva contra fuerza bruta a nivel de instancia, no por IP de cliente individual.
- Q: Versión del plugin `mholt/caddy-ratelimit` para garantizar la sintaxis de bloque → A: **Fijar la versión** del plugin en el Dockerfile (`xcaddy build --with github.com/mholt/caddy-ratelimit@<versión estable>`) para eliminar el riesgo de regresión por versión flotante (la sintaxis de bloque `zone` requiere plugin ≥ v1.1.0). Build determinista y alineado con SHIFT LEFT. El alcance del fix incluye esta tarea en `Dockerfile`.

## User Needs & Value
**As a** system administrator or DevOps engineer,
**I need** the Caddy web server to successfully parse its configuration and start up without syntax errors,
**so that** the application is successfully deployed and accessible to users with the intended rate limiting protections in place.

## Assumptions
- The application uses Caddy as a reverse proxy/web server.
- A custom Caddyfile is being generated or used during the deployment phase.
- The `rate_limit` plugin is installed or intended to be used, but the syntax provided in the `Caddyfile` is incorrect or incompatible with the installed version.
- The fix should maintain the intended rate limiting behavior (if possible) while using valid Caddyfile syntax.

## Functional Requirements
1. The global options block in `Caddyfile` must declare `order rate_limit before basicauth` to prioritize rate limiting in the HTTP handler chain. NO se configura la directiva `trusted_proxies` (Railway usa un edge AWS dinámico sin rango público estable; ver Q15); en consecuencia `{client_ip}` se resuelve a la IP de la conexión remota, no a la IP del cliente final.
2. The `Caddyfile` must contain valid syntax for the `rate_limit` directive implementing a zone named `login_limit` with `key {client_ip}` (sin `trusted_proxies`, lo que resuelve la clave a la IP de la conexión remota; ver Q15), `window 15m`, `events 5`, and a `match` block targeting login routes (`/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*`).
3. When the rate limit threshold is exceeded for matching login requests, the response must return HTTP status 429 with JSON payload `{"detail": "Demasiados intentos de inicio de sesión"}` and `Content-Type: application/json`.
4. The deployment pipeline must complete the Caddy startup step without raising wrong argument count or unexpected line ending after '5' errors.
5. The server must successfully bind to port 8080 (as indicated in the logs) and route traffic to the backend.
6. The deployment build must pin a fixed version of the rate-limiting plugin (at least the version that supports the block/`zone` syntax) so that future builds remain deterministic and do not break the `rate_limit` syntax due to an unpinned floating version. [Q16]

## User Scenarios & Testing

**Scenario 1: Deployment succeeds without Caddy errors**
- **Given** a new deployment is triggered
- **When** the pipeline reaches Step 5 (Starting Caddy)
- **Then** Caddy parses the configuration successfully and the application becomes accessible.

## Edge Cases & Limitations
- **Versión del plugin `rate_limit`**: Se fija la versión de `github.com/mholt/caddy-ratelimit` en el Dockerfile (Q16) para garantizar que la sintaxis de bloque `zone` siga siendo compatible en builds futuros (requiere plugin ≥ v1.1.0). Esto elimina el riesgo de que una versión flotante rompa la sintaxis en el futuro.
- **Identificación del cliente (proxy)**: NO se configura `trusted_proxies` (Q15). Como Railway opera con 1 réplica detrás de un edge AWS dinámico sin rango público estable, `{client_ip}` se resuelve a la IP de la conexión remota (IP interna del contenedor/ingress). **Limitación de seguridad**: el rate limit NO distingue por usuario final detrás del proxy; todas las peticiones a la instancia comparten el mismo contador. La protección es efectiva a nivel de instancia (fuerza bruta contra la autorización), no por IP de cliente individual. Aceptado como limitación conocida.
- Si el plugin `rate_limit` falla al cargar o no se compila correctamente, el sistema debe adoptar una postura **fail-open**: Caddy arranca normalmente sin rate limiting, priorizando la disponibilidad del servicio.
- **Limitación conocida**: Usuarios legítimos detrás de una misma IP pública (NAT/redes corporativas) comparten el umbral de 5 intentos/15m. Se considera aceptable dado el caso de uso del sistema.
- **Limitación conocida (persistencia)**: Los contadores del rate limit viven en memoria del proceso y se resetean en cada reinicio/redeploy de Caddy. Una IP bloqueada puede reintentar tras un redeploy. Aceptado como parte del alcance; sin almacén externo compartido.
- **Rollback**: Si la nueva sintaxis del Caddyfile causa regresiones en otras reglas del proxy, el mecanismo de reversión es `git revert` del commit correspondiente; Railway re-despliega automáticamente la versión anterior.

## Success Criteria
- Deployment logs show successful Caddy startup.
- The Reflex backend is accessible via the Caddy reverse proxy.
- No parsing errors regarding `rate_limit` are thrown.
- When the rate limit threshold is exceeded (5 events within 15m for matching login routes), the server returns HTTP 429 with JSON payload `{"detail": "Demasiados intentos de inicio de sesión"}` and `Content-Type: application/json`.
