# Data Model: Fix Caddy Rate Limit Parsing Error

This feature does not introduce or modify any database entities, models, or internal application state. The changes are strictly confined to the Caddy reverse proxy configuration.

## Rate Limiting Configuration
- **Zone**: `login_limit`
- **Key**: `{client_ip}` (placeholder nativo de Caddy)
- **Trusted Proxies**: NO se configura la directiva `trusted_proxies` (Q15). Railway usa un edge AWS dinámico sin rango público estable; `private_ranges` no lo cubre.
- **Key Resolution (Q15)**: Sin `trusted_proxies`, `{client_ip}` se resuelve a la IP de la conexión remota (IP interna del contenedor/ingress de Railway con 1 réplica), NO a la IP del usuario final.
- **Window**: `15m` (Time window)
- **Events**: `5` (Maximum number of requests per window)
- **Directive Order**: `{ order rate_limit before basicauth }` (bloque global de opciones)
- **Match (Target Paths)**:
  - `/api/login*`
  - `/api/auth*`
  - `/_event/auth_state.login*`
  - `/_event/estado_autenticacion.iniciar_sesion*`

## Rate Limit Response (429)
- **Status code**: HTTP 429 Too Many Requests
- **Content-Type**: `application/json`
- **Body**: `{"detail": "Demasiados intentos de inicio de sesión"}`
- **Implementation**: bloque `handle_errors` con matcher de expresión `{http.error.status_code} == 429` y `respond "...JSON..." 429`

## Fallback / Failure Behavior
- **Plugin no disponible**: Postura **fail-open** — Caddy arranca sin rate limiting, priorizando disponibilidad.
- **Versión del plugin (Q16)**: Se **fija la versión** de `github.com/mholt/caddy-ratelimit` (≥ v1.1.0) en el `Dockerfile` para garantizar la compatibilidad de la sintaxis de bloque `zone` en builds futuros. Build determinista (SHIFT LEFT).
- **Identificación del cliente (Q15)**: Sin `trusted_proxies`, `{client_ip}` = IP de conexión remota. **Limitación de seguridad**: el rate limit aplica a nivel de contenedor (todas las peticiones a la instancia comparten el contador), no por usuario final detrás del proxy. Protección efectiva contra fuerza bruta a nivel de instancia. Aceptada como limitación conocida.
- **Persistencia del estado**: Los contadores del rate limit viven en memoria del proceso (`mholt/caddy-ratelimit`) y se resetean en cada reinicio/redeploy de Caddy. Limitación documentada; sin almacén externo compartido.
- **Rollback**: `git revert` del commit; Railway re-despliega la versión anterior automáticamente.
