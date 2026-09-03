# Implementation Tasks: Fix Caddy Rate Limit Parsing Error

## Phase 1: Setup

**Purpose**: Project initialization and basic structure
*No setup tasks needed since the project is already initialized.*

---

## Phase 2: Foundational

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented
*No foundational tasks needed for this localized reverse engineering fix.*

---

## Phase 3: User Story 1 - Fix Caddyfile Rate Limit Syntax (Priority: P1) 🚀 MVP

**Goal**: Update the generated Caddyfile in entrypoint.sh to use the correct block syntax for caddy-ratelimit (with `{client_ip}` y **sin** `trusted_proxies` — Q15, extended match paths, and 429 JSON response) so the server can start successfully on Railway.

**Independent Test**: The container builds and Caddy executes without raising parsing errors on the rate_limit directive; the 429 behavior is verified (DoD).

### Implementation for User Story 1

- [x] T001 [US1] Update rate_limit block syntax in entrypoint.sh (za block zone login_limit)
- [x] T003 [US1] Cambiar la clave de rate limit a `{client_ip}` en el Caddyfile generado en entrypoint.sh. **NO configurar `trusted_proxies`** (Q15). *Nota: la línea actual usa `key {http.request.header.X-Forwarded-For}`, que se sustituye por `key {client_ip}`.*
- [x] T004 [US1] Extender el bloque `match` de login_limit a las 4 rutas requeridas: `/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*` (actualmente solo 2 rutas).
- [x] T005 [US1] Añadir bloque `handle_errors` (a nivel del sitio) que devuelva HTTP 429 con `Content-Type: application/json` y payload `{"detail": "Demasiados intentos de inicio de sesión"}` cuando `{http.error.status_code} == 429`.
- [x] T007 [US1] Fijar la versión del plugin en Dockerfile (Q16): cambiar `RUN xcaddy build --with github.com/mholt/caddy-ratelimit` por `RUN xcaddy build --with github.com/mholt/caddy-ratelimit@<versión fija ≥ v1.1.0>` en Dockerfile:7 para garantizar la sintaxis de bloque `zone` (build determinista).

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T002 [US1] Run quickstart.md validation to verify Caddy syntax locally (if possible) or review carefully.
- [x] T006 [Polish] Verificar el comportamiento 429 (DoD, Q13): realizar >5 peticiones a la ruta de login y confirmar que la 6ª devuelve HTTP 429 con el payload JSON. Documentar resultado en logs de Railway.

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (P1)**: Can start immediately.
- **Polish (Final Phase)**: Depends on User Story 1 being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies.

### Within Each User Story

- Modify the file entrypoint.sh directly (T003-T005) y Dockerfile (T007).

### Parallel Opportunities
- T007 (Dockerfile) es paralelizable con los edits de entrypoint.sh (archivo distinto). Los edits T003-T005 son secuenciales en el mismo heredoc.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1 (T001 done; T003-T005 y T007 pendientes)
2. **STOP and VALIDATE**: Test User Story 1 independently
3. Deploy/demo if ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- T001 marcó la corrección base de sintaxis. T003-T005 (+ T007) completan el alcance final conforme a las clarificaciones Q12 (clave `{client_ip}`), **Q15 (sin `trusted_proxies`)** , Q9 (rutas extendidas), Q7/Q13 (respuesta 429 JSON y su verificación en DoD) y **Q16 (pin de versión del plugin en el Dockerfile)**.