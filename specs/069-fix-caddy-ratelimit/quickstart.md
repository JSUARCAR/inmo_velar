# Quickstart: Fix Caddy Rate Limit Parsing Error

## Prerequisites
- Docker installed locally.
- Caddy CLI (opcional, para validar la sintaxis localmente con `caddy adapt`).
- **Versión del plugin fijada (Q16)**: `Dockerfile:7` debe usar `xcaddy build --with github.com/mholt/caddy-ratelimit@vX.Y.Z` (≥ v1.1.0) para garantizar la sintaxis de bloque `zone`. Verificar antes del build.

## Validation Steps

0. **Verificar pin de versión del plugin (Q16)**:
   ```bash
   grep "xcaddy build" Dockerfile
   ```
   Debe incluir `@<versión fija>` de `mholt/caddy-ratelimit` (≥ v1.1.0), no una versión flotante sin pin.

1. **Trigger local build**:
   ```bash
   docker build -t inmo_velar_test .
   ```
   *(Si Docker Desktop está disponible, validar la sintaxis; si no, inspeccionar manualmente el heredoc en `entrypoint.sh`).*

2. **Validar sintaxis local (opcional, mejor shift-left)**:
   ```bash
   caddy adapt --config Caddyfile.runtime --adapter caddyfile
   ```
   El adaptador genera JSON; no debe lanzar errores de "wrong argument count" ni "unexpected line ending after '5'".

3. **Review the generated Caddyfile**:
   Inspect the heredoc in `entrypoint.sh`. Debe implementar la estructura de bloque con `order`, zona `login_limit` con `key {client_ip}` (SIN `trusted_proxies` — Q15), `window 15m`, `events 5`, `match` con las rutas de login extendidas, y el bloque `handle_errors` para la respuesta 429 JSON:
   ```caddyfile
   {
       order rate_limit before basicauth
   }

   :8080

   rate_limit {
       zone login_limit {
           key {client_ip}
           window 15m
           events 5
           match {
               path /api/login* /api/auth* /_event/auth_state.login* /_event/estado_autenticacion.iniciar_sesion*
           }
       }
   }

   handle_errors {
       @ratelimit expression {http.error.status_code} == 429
       handle @ratelimit {
           header Content-Type application/json
           respond `{"detail": "Demasiados intentos de inicio de sesión"}` 429
       }
   }
   ```
   *Nota (Q15)*: al no configurar `trusted_proxies`, `{client_ip}` se resuelve a la IP de la conexión remota; el rate limit aplica a nivel de contenedor/ingress (1 réplica), no por usuario final.

4. **Verify Pipeline**:
   After pushing to the repository, observe the Railway deployment logs.
   - **Expected Outcome**: Step 5 ("Starting Caddy") completes successfully without the `parsing caddyfile tokens for 'rate_limit'` error, and the server binds to port 8080.

5. **Verify 429 behavior (post-deploy)**:
   - Realizar >5 peticiones a `/api/login` desde la misma IP.
   - **Expected Outcome**: La 6ª petición devuelve HTTP 429 con `Content-Type: application/json` y body `{"detail": "Demasiados intentos de inicio de sesión"}`.

## Data Model & Contracts
- Detalles de configuración y comportamiento: [data-model.md](data-model.md)
- Este feature no expone contratos de API externos; la única interfaz afectada es el Caddyfile de runtime.
