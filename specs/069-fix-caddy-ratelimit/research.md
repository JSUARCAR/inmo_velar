# Research: Fix Caddy Rate Limit Parsing Error

## Objective
Identify the correct syntax for the github.com/mholt/caddy-ratelimit plugin used in Caddy 2, which caused a parsing failure in entrypoint.sh.

## Findings

- **Decision**: Update the Caddyfile generation logic in `entrypoint.sh` to use the zone-based block syntax of the `mholt/caddy-ratelimit` plugin con `key {client_ip}` y **sin** `trusted_proxies`.
- **Rationale**: La sintaxis anterior (`rate_limit @login_endpoint 5 15m`) estaba obsoleta. El plugin oficial requiere definir una `zone` dentro del bloque `rate_limit`, mapeando `key`, `window`, `events` y un bloque `match`. Se usa `{client_ip}` como clave (sustituyendo la cabecera cruda `{http.request.header.X-Forwarded-For}`, que devolvería la lista completa separada por comas, no la primera IP).
- **Decisión Q15 - `trusted_proxies`**: NO se configura `trusted_proxies`. Railway opera detrás de un edge AWS dinámico sin un rango público estable publicado; `trusted_proxies static private_ranges` NO lo cubriría. Definir un rango fijo de Railway implicaría mantener una lista actualizada (frágil). **Consecuencia**: al no configurar `trusted_proxies`, `{client_ip}` se resuelve a la IP de la conexión remota (IP interna del contenedor/ingress con 1 réplica de Railway), no a la IP del usuario final.
- **Alternatives considered**: Deshabilitar el rate limit fue rechazado por comprometer la seguridad. `{remote.host}` capturaría la IP del balanceador. La cabecera cruda `{http.request.header.X-Forwarded-For}` devuelve la lista completa, no la primera IP. `trusted_proxies static private_ranges` no cubre el edge AWS de Railway. `static <rango fijo de Railway>` es frágil por la ausencia de una whitelist estable pública.
- **Fail-open posture**: Si el plugin falla al cargar, Caddy debe arrancar normalmente sin rate limiting, priorizando disponibilidad.
- **Limitación de seguridad (Q15)**: Con 1 réplica y sin `trusted_proxies`, el rate limit NO distingue por usuario final; todas las peticiones a la instancia comparten el contador. La protección es efectiva a nivel de instancia (fuerza bruta contra la autorización), no por IP de cliente individual. Aceptada como limitación conocida.
- **Decisión Q16 - Fijar versión del plugin**: El `Dockerfile` usa `xcaddy build --with github.com/mholt/caddy-ratelimit` **sin pin de versión** (versión flotante). Se **fija la versión** en el `Dockerfile` (`--with github.com/mholt/caddy-ratelimit@vX.Y.Z`) para eliminar el riesgo de regresión por versión flotante; la sintaxis de bloque `zone` (plugin ≥ v1.1.0) queda garantizada en builds futuros. El alcance del fix incluye una tarea en el `Dockerfile`.
- **Versión recomendada (Q16)**: Usar una versión estable de `mholt/caddy-ratelimit` **≥ v1.1.0** (la que introdujo la sintaxis de bloque `zone`). Verificar en el Dockerfile la versión concreta disponible en el momento de la implementación; documentar la versión exacta fijada para trazabilidad.

## Clarification Session 2026-09-02 (Q7-Q15)

- **Q7 - Respuesta 429 JSON**: El plugin genera un error HTTP 429 interno. Para devolver JSON, se debe agregar un bloque `handle_errors` a nivel del sitio con un matcher de expresión `{http.error.status_code} == 429` y un `respond` con `Content-Type: application/json` y el payload `{"detail": "Demasiados intentos de inicio de sesión"}`.
- **Q8 - Fallback de clave**: Cuando `X-Forwarded-For` está ausente, la clave cae a la IP de conexión remota vía `{client_ip}`. *Decisión final sobre `trusted_proxies` consolidada en Q15.*
- **Q9 - Rutas protegidas**: El bloque `match` usa paths literales (no named matchers, que no se soportan dentro de zones): `/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*`.
- **Q10 - Cabecera multi-IP**: La cabecera cruda `{http.request.header.X-Forwarded-For}` no extrae la primera IP (devuelve la lista). Se usa `{client_ip}` como clave. *Decisión final sobre `trusted_proxies` en Q15 (sin configuración, la clave = IP remota).*
- **Q11 - Orden del middleware**: Se mantiene `{ order rate_limit before basicauth }` en el bloque de opciones globales.
- **Q12 - Mecanismo de clave (DECISIÓN CLAVE)**: Usar `{client_ip}` como clave, sustituyendo la cabecera cruda `{http.request.header.X-Forwarded-For}`. El mecanismo de extracción de IP originaria vía `trusted_proxies` queda **superado por Q15** (no se configura).
- **Q13 - Verificación 429 en DoD**: El DoD debe incluir la verificación explícita de que al superar el umbral (5/15m) Caddy devuelve HTTP 429 con payload JSON y `Content-Type: application/json`.
- **Q14 - Persistencia del estado**: Contadores en memoria, se resetean por reinicio/redeploy. Railway con 1 réplica. Limitación documentada; sin Redis.
- **Q15 - `trusted_proxies` (DECISIÓN FINAL)**: NO configurar `trusted_proxies` (edge AWS dinámico de Railway sin rango estable). `{client_ip}` → IP de conexión remota (nivel contenedor). Rate limit a nivel instancia, no por usuario final. Documentado como limitación de seguridad.
- **Q16 - Versión del plugin (DECISIÓN FINAL)**: Fijar la versión de `github.com/mholt/caddy-ratelimit` en el `Dockerfile` (`--with ...@vX.Y.Z` ≥ v1.1.0) para garantizar la sintaxis de bloque `zone`. Build determinista, alineado con SHIFT LEFT. Nueva tarea en el alcance (`Dockerfile`).

## Sources
- https://caddyserver.com/docs/modules/http.handlers.rate_limit
- https://github.com/mholt/caddy-ratelimit
- https://caddyserver.com/docs/json/apps/http/servers/client_ip_headers
- https://github.com/caddyserver/caddy/pull/5104 (client_ip placeholder / trusted proxies)
