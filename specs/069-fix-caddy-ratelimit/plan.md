# Implementation Plan: Fix Caddy Rate Limit Parsing Error

**Branch**:  69-fix-caddy-ratelimit | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from specs/069-fix-caddy-ratelimit/spec.md

## Summary

To resolve the Caddy startup error in the deployment pipeline by fixing the malformed `rate_limit` directive in the generated Caddyfile (inside `entrypoint.sh`). The syntax will be updated to match the block-oriented configuration required by the `github.com/mholt/caddy-ratelimit` plugin, using `{client_ip}` como clave de identificación. **NO se configura `trusted_proxies`** (Q15: Railway usa un edge AWS dinámico sin rango público estable), por lo que `{client_ip}` se resuelve a la IP de la conexión remota (nivel contenedor/ingress con 1 réplica) — el rate limit NO distingue por usuario final detrás del proxy. Se mantiene `order rate_limit before basicauth` en el bloque global. El bloque `match` protege las rutas de login extendidas (`/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*`). Respuesta 429 personalizada en JSON vía bloque `handle_errors`. Postura de seguridad: **fail-open** (si el plugin falla, Caddy arranca sin rate limiting). Persistencia en memoria: los contadores se resetean en cada reinicio/redeploy (limitación documentada). El Definition of Done incluye verificación explícita del comportamiento 429 (Q13). **Además (Q16)**: se fija la versión del plugin `github.com/mholt/caddy-ratelimit` (≥ v1.1.0) en el `Dockerfile` para garantizar la compatibilidad de la sintaxis de bloque `zone` en builds futuros (elimina el riesgo de versión flotante).

## Technical Context

**Language/Version**: Bash / Caddyfile

**Primary Dependencies**: Caddy 2, mholt/caddy-ratelimit

**Storage**: N/A

**Testing**: Docker local build / Railway deployment logs

**Target Platform**: Linux server (Docker container via Railway)

**Project Type**: Web service (Reflex Python Framework + Caddy reverse proxy)

**Performance Goals**: N/A (fix parsing error)

**Constraints**: La sintaxis debe ser compatible con la versión del plugin compilada en el Dockerfile. Se **fija la versión** de `github.com/mholt/caddy-ratelimit` (≥ v1.1.0, Q16) en el `Dockerfile` para garantizar la sintaxis de bloque `zone`. La clave de rate limiting usa `{client_ip}`; NO se configura `trusted_proxies` (Q15, Railway sin rango estable), por lo que la clave = IP de conexión remota (nivel contenedor). Rutas protegidas: `/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*`. Respuesta 429 JSON con `handle_errors` (`Content-Type: application/json`). Persistencia de contadores en memoria (se resetean por reinicio/redeploy, limitación documentada). Rollback vía `git revert`. DoD incluye verificación explícita del comportamiento 429.

**Scale/Scope**: Afecta el ingress global de la aplicación. Limitación conocida: usuarios detrás de NAT comparten umbral de 5/15m; además, sin `trusted_proxies` (Q15), todas las peticiones a la instancia comparten el mismo contador a nivel contenedor.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
- ✅ "VALIDACIÓN EN FRONTERAS": Rate limits activos en endpoints de autenticación (`/api/login*`, `/api/auth*`, eventos de estado Reflex) con clave `{client_ip}`. *Nota*: por Q15 (sin `trusted_proxies`), la limitación aplica a nivel de instancia, no por usuario final; aceptada como limitación conocida con la protección contra fuerza bruta a nivel contenedor.
- ✅ "CERO FILTRACIONES": Sin exposición de secrets ni variables sensibles en el Caddyfile generado.
- ✅ "SHIFT LEFT": Sintaxis `caddy adapt` validable localmente; fail-open asegura disponibilidad sin romper CI/CD. *Plus Q16*: pin de versión del plugin `caddy-ratelimit` en el Dockerfile → build determinista y reproducible.
- ✅ "DESPLIEGUE SEGURO": Plan de rollback definido (`git revert` → Railway re-deploy automático).
- ✅ "LINGÜÍSTICA / IDIOMA": Respuesta 429 en español (`"Demasiados intentos de inicio de sesión"`) consistente con el idioma del proyecto.

**Gate status: PASS** (sin violaciones).

## Research Summary (Phase 0)
- **Sintaxis bloque**: `rate_limit { zone login_limit { key ...; window 15m; events 5; match { path ... } } }` (ver [research.md](research.md)).
- **Clave `{client_ip}` sin `trusted_proxies` (Q15)**: Se usa el placeholder nativo de Caddy `{client_ip}` como clave, pero NO se configura `trusted_proxies` (Railway usa edge AWS dinámico sin rango estable; `private_ranges` no lo cubre). En consecuencia `{client_ip}` se resuelve a la IP de la conexión remota. Sustituye la cabecera cruda `{http.request.header.X-Forwarded-For}` (que devolvería la lista completa con comas).
- **Respuesta 429 JSON**: Bloque `handle_errors` con matcher `{http.error.status_code} == 429` y `respond '{json}' 429` con `Content-Type: application/json` (verificación en DoD).
- **Paths en `match`**: Literales (no named matchers, no soportados en zones): `/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*`.
- **Persistencia**: Contadores en memoria; se resetean en cada reinicio/redeploy (limitación documentada).
- **Pin de versión del plugin (Q16)**: Se fija `github.com/mholt/caddy-ratelimit@vX.Y.Z` (≥ v1.1.0) en el `Dockerfile` para garantizar la sintaxis de bloque `zone`; elimina el riesgo de versión flotante.

## Project Structure

### Documentation (this feature)

```
specs/069-fix-caddy-ratelimit/
 plan.md              # This file
 research.md          # Phase 0 output
 data-model.md        # Phase 1 output
 quickstart.md        # Phase 1 output
 tasks.md             # Phase 2 output
```

### Source Code (repository root)

```
entrypoint.sh
Dockerfile
```

**Structure Decision**: The fix will be contained within `entrypoint.sh` (modificando el heredoc del Caddyfile generado) **y** en `Dockerfile:7` (fijando la versión del plugin `mholt/caddy-ratelimit` — Q16). No `contracts/` directory es necesario: este feature es una configuración interna de proxy inverso sin interfaces externas expuestas.

## Complexity Tracking

N/A
