# Unit Tests for Requirements: Fix Caddy Rate Limit Parsing Error

**Purpose**: Validate requirement quality, clarity, completeness, and consistency
**Created**: 2026-09-02
**Updated**: 2026-09-02 (Session 2 - post-clarify Q7-Q11)
**Feature**: [spec.md](../spec.md)
**Depth**: Standard
**Audience**: Author/Reviewer

## Requirement Completeness

- [x] CHK001 - Are all rate limiting parameters (key, window, events, match paths) explicitly defined in the functional requirements? [Completeness, Spec §FR-1] — Cumple: FR-2 define `key {client_ip}`, `window 15m`, `events 5` y el bloque `match` con las 4 rutas.
- [x] CHK002 - Are requirements defined for the scenario where the rate_limit plugin fails to load? [Coverage, Edge Case, Spec §Edge Cases] — Cumple: postura fail-open en Edge Cases.
- [x] CHK003 - Is the fail-open behavior specified with concrete requirements (what exactly happens when plugin fails)? [Clarity, Spec §Edge Cases] — Cumple: "Caddy arranca sin rate limiting", priorizando disponibilidad.
- [x] CHK004 - Are requirements defined for handling missing or malformed X-Forwarded-For header? [Gap, Edge Case] — Resuelto por Q12/Q15: se usa `{client_ip}` (fallback nativo de Caddy a la IP de conexión remota sin `trusted_proxies`); la cabecera XFF cruda queda obsoleta.
- [x] CHK005 - Is the `order rate_limit before basicauth` directive requirement documented? [Gap, Spec §FR-1] — Cumple: FR-1 documenta la directiva en el bloque global.

## Requirement Clarity

- [x] CHK006 - Is "valid syntax" quantified with reference to specific plugin version or syntax specification? [Clarity, Spec §FR-1] — Cumple: Q16/FR-6 fijan versión ≥ v1.1.0 del plugin y FR-2 describe la sintaxis de bloque `zone`.
- [x] CHK007 - Are the login route paths (`/api/login*`, `/_event/auth_state.login*`) specified with exact glob pattern semantics? [Clarity, Spec §FR-1] — Cumple: Q9/FR-2 listan las 4 rutas exactas con `/` y `*`.
- [x] CHK008 - Is the "successful Caddy startup" criteria defined with specific log messages or exit codes? [Measurability, Spec §Success Criteria] — Cumple: SC/FR-4 sin errores específicos ("wrong argument count", "unexpected line ending after '5'") y SC-1 log de arranque.
- [x] CHK009 - Is "route traffic to the backend" quantified with specific health check or response criteria? [Measurability, Spec §FR-3] — Cumple: FR-5/SC-2 (bind 8080 + acceso al backend vía reverse proxy).

## Requirement Consistency

- [x] CHK010 - Does the clarification session key (`{remote.host}` in Q1) conflict with FR-1 key (`{http.request.header.X-Forwarded-For}`)? [Conflict, Spec §Clarifications vs §FR-1] — Resuelto: Q12/Q15 unificaron la clave a `{client_ip}`; la entrada Q1 es histórica y lleva cross-ref. Sin conflicto vigente.
- [x] CHK011 - Are the rate limit thresholds (5 events/15m) consistent between clarifications and functional requirements? [Consistency, Spec §Clarifications vs §FR-1] — Cumple: 5/15m consistentes.
- [x] CHK012 - Is the fail-open requirement consistent with the stated security objective of protecting authentication endpoints? [Consistency, Spec §Edge Cases vs §User Needs] — Cumple: la disponibilidad primada está documentada y aceptada como decisión (Q2); la protección de endpoints se mantiene cuando el plugin opera.

## Acceptance Criteria Quality

- [x] CHK013 - Can "no parsing errors" be objectively verified from deployment logs? [Measurability, Spec §Success Criteria] — Cumple: FR-4 define los errores concretos a ausentes en logs.
- [x] CHK014 - Is the success criteria for "application becomes accessible" defined with specific HTTP status codes or health endpoints? [Measurability, Spec §User Scenarios] — Cumple: FR-5/SC-2 (bind 8080 y ruteo al backend).
- [x] CHK015 - Are acceptance criteria defined for the rate limiting actually working (429 responses)? [Gap, Spec §Success Criteria] — Cumple: Q13/SC-4 + T006 (DoD).

## Scenario Coverage

- [x] CHK016 - Are requirements defined for concurrent deployments or rapid successive deployments? [Gap, Coverage] — Documentado: contadores en memoria se reseteen en cada redeploy (Q14/Edge Cases), aceptado como limitación.
- [x] CHK017 - Are requirements defined for rollback scenario beyond "git revert"? [Coverage, Spec §Edge Cases] — Cumple: rollback vía `git revert` + redeploy automático de Railway (Edge Cases).
- [x] CHK018 - Is the scenario where Caddy starts but rate limiting is ineffective documented? [Gap, Exception Flow] — Cumple: Edge Cases documentan fail-open y la limitación de alcance a nivel instancia sin `trusted_proxies` (Q15).

## Edge Case Coverage

- [x] CHK019 - Are requirements defined for X-Forwarded-For header containing multiple IP addresses (comma-separated)? [Gap, Edge Case] — Resuelto por Q11/Q12: se usa `{client_ip}` (placeholder nativo) en lugar de la cabecera cruda; la lista con comas deja de ser un problema.
- [x] CHK020 - Are requirements defined for IPv6 client addresses in rate limiting key? [Gap, Edge Case] — Cubierto: `{client_ip}` maneja IPv6 nativamente; no requiere configuración adicional.
- [x] CHK021 - Is the behavior specified when the same client IP exceeds the limit from different paths? [Gap, Edge Case] — Cumple: el bloque `match` agrupa las 4 rutas en la misma zona `login_limit`, por lo que comparten un único contador.

## Non-Functional Requirements

- [x] CHK022 - Are performance requirements specified for rate limit checking overhead? [Gap, Non-Functional] — N/A: feature de corrección de parsing; el overhead del rate limit nativo es despreciable y no es objetivo de la feature. Aceptado.
- [x] CHK023 - Are logging requirements defined beyond "429 in stdout" (structured logging, log levels)? [Gap, Non-Functional] — Cumple Q4: se confía en el logging nativo de Caddy (429 en stdout); Railway captura logs. Sin configuración adicional (decisión documentada).
- [x] CHK024 - Are monitoring/alerting requirements defined for rate limit threshold breaches? [Gap, Non-Functional, Spec §Clarifications] — Cumple Q4: sin alertas adicionales; los 429 quedan visibles en logs de Railway (decisión documentada).

## Dependencies & Assumptions

- [x] CHK025 - Is the assumption that "Railway injects X-Forwarded-For" validated or documented as external dependency? [Assumption, Spec §Clarifications] — Cumple Q15: se reconoce que Railway inyecta la cabecera, pero sin `trusted_proxies` no se usa; documentado como limitación con racional.
- [x] CHK026 - Is the plugin version compatibility assumption (syntax matches compiled version) documented as risk? [Assumption, Spec §Edge Cases] — Cumple Q16/FR-6: se fija la versión (≥ v1.1.0) para eliminar el riesgo de compatibilidad por versión flotante.

## Ambiguities & Conflicts

- [x] CHK027 - Is the term "login routes" clearly defined to exclude other authentication endpoints? [Ambiguity, Spec §FR-1] — Cumple Q9: las 4 rutas exactas (`/api/login*`, `/api/auth*`, `/_event/auth_state.login*`, `/_event/estado_autenticacion.iniciar_sesion*`).
- [x] CHK028 - Is the scope of "other rules of the proxy" in rollback scenario defined? [Ambiguity, Spec §Edge Cases] — Definido: cualquier regresión en el proxy revierte con `git revert`; el alcance del fix se limita a `entrypoint.sh` y `Dockerfile`.

## Post-Clarify Session 2 (Q7-Q11) — Requirement Quality

### Requirement Completeness

- [x] CHK029 - Is the exact 429 JSON response payload (`{"detail": "Demasiados intentos de inicio de sesión"}`) specified as a formal requirement, not only as a clarification? [Completeness, Spec §FR-3 vs §Clarifications] — Cumple: FR-3 la formaliza.
- [x] CHK030 - Are the `Content-Type: application/json` header requirements for the 429 response explicitly documented with exact value? [Completeness, Spec §FR-3] — Cumple: FR-3/SC-4 explicitan `Content-Type: application/json`.
- [x] CHK031 - Is the `{ order rate_limit before basicauth }` global directive captured as a dedicated functional requirement distinct from the zone configuration? [Completeness, Spec §FR-1] — Cumple: FR-1 (orden global) distinto de FR-2 (zona).

### Requirement Clarity

- [x] CHK032 - Is the key fallback behavior (`X-Forwarded-For` → `{remote.host}`) specified with an unambiguous triggering condition (exact scenario where fallback activates)? [Clarity, Spec §FR-2, §Edge Cases] — Resuelto por Q12/Q15: la clave es `{client_ip}` con fallback nativo a la IP de conexión remota; la condición no es ambigua.
- [x] CHK033 - Is "selecting the first client IP in multi-IP headers" defined with the exact mechanism/placeholder to achieve it? [Clarity, Spec §FR-2] — Resuelto por Q12: es el placeholder nativo `{client_ip}`; la cabecera cruda `{http.request.header.X-Forwarded-For}` queda obsoleta (Q15, sin `trusted_proxies`).
- [x] CHK034 - Are the extended match paths (`/api/*`, `/_event/estado_autenticacion.iniciar_sesion*`) consistent between Clarifications, FR-2, and Edge Cases sections? [Consistency, Spec §Clarifications vs §FR-2 vs §Edge Cases] — Cumple: las 4 rutas idénticas en todas las secciones y artefactos.

### Requirement Consistency

- [x] CHK035 - Does the fail-open posture (Q2) conflict with the new JSON 429 response requirement (Q7) when the plugin is unavailable? [Conflict, Spec §Clarifications] — Clarificado: si el plugin no carga → fail-open (arranca sin 429 de rate limit); si carga → 429 JSON. No hay conflicto: el `handle_errors` 429 solo aplica cuando existe la directiva `rate_limit`.
- [x] CHK036 - Is there a conflict between multi-IP first-IP extraction (Edge Cases) and the use of `{http.request.header.X-Forwarded-For}` as key (which returns the full header)? [Conflict, Spec §FR-2 vs §Edge Cases] — Resuelto por Q12/Q15: la clave es `{client_ip}`, que no devuelve la lista completa; el conflicto queda eliminado.

### Acceptance Criteria Quality

- [x] CHK037 - Are acceptance criteria defined to verify the 429 JSON response is actually returned (when threshold is exceeded) in addition to successful Caddy startup? [Measurability, Spec §Success Criteria] — Cumple: Q13/SC-4 (DoD) + T006.
- [x] CHK038 - Is the "first client IP" extraction behavior verifiable via an objective test (e.g., sending a known comma-separated header)? [Measurability, Spec §FR-2] — Resuelto: la clave `{client_ip}` es verificable (placeholder nativo de Caddy); la extracción manual de primera-IP ya no aplica.

### Edge Case Coverage

- [x] CHK039 - Are requirements defined for the 429 response when the client sends an `Accept` header preferring non-JSON content? [Gap, Coverage] — Aceptado: el `handle_errors` devuelve JSON fijado (sin negociación de contenido). No se requiere requisito adicional; el payload es fijo.
- [x] CHK040 - Are requirements defined for the behavior when BOTH `X-Forwarded-For` is absent AND the connection is over IPv6 (`{remote.host}` = IPv6 address)? [Gap, Edge Case] — Cubierto por `{client_ip}`: el placeholder nativo maneja ausencia del header y direcciones IPv6 sin configuración adicional.
- [x] CHK041 - Are requirements defined for rate limit state persistence across Caddy restarts/redeploys (in-memory vs persisted)? [Gap, Coverage] — Cumple Q14: contadores en memoria, se reseteen en cada reinicio/redeploy; documentado como limitación (sin almacén externo).

### Non-Functional Requirements

- [x] CHK042 - Is a retry hint (`Retry-After` header) requirement defined for the 429 response to guide legitimate clients? [Gap, Non-Functional] — Gap aceptado: no se añade `Retry-After`; el alcance fija el payload JSON y el código 429, sin requisito adicional de cabecera de reintento (decisión documentada, no bloqueante para el DoD).
