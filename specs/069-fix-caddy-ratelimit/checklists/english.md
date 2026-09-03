# Unit Tests for English: Fix Caddy Rate Limit Parsing Error

**Purpose**: Validate language/terminology consistency and compliance with the constitutional 100% ESPAÑOL mandate across all spec artifacts
**Created**: 2026-09-02
**Feature**: [spec.md](../spec.md)
**Depth**: Standard
**Audience**: Author/Reviewer
**Theme**: Requirements language quality — "Unit Tests for English" in the context of a Spanish-language project

## Language Policy Adherence

- [x] CHK001 - Does the spec comply with the constitutional mandate of 100% ESPAÑOL across all requirement content, or is each deviation (English headings, Caddy directives) justified by a convention or technical constraint? [Compliance, Constitution §1 / Spec §All] — Cumple: el spec es en español; los términos en inglés se limitan a directivas/vocabulario técnico de Caddy justificado por convención técnica.
- [x] CHK002 - Are user-facing runtime artifacts (429 response payload, Content-Type description) specified in Spanish consistently? [Consistency, Spec §FR-3, §Success Criteria] — Cumple: payload `{"detail": "Demasiados intentos de inicio de sesión"}` en español, idéntico en FR-3 y Success Criteria.
- [x] CHK003 - Are English-only terms (HTTP status codes, `Content-Type`, Caddy directives like `rate_limit`, `handle_errors`, `trusted_proxies`) limited to technical vocabulary where a Spanish translation would be meaningless or non-standard? [Clarity] — Cumple: los términos en inglés son vocabulario técnico del dominio (directivas Caddy, cabeceras HTTP) donde la traducción sería no estándar.

## Terminology Consistency

- [x] CHK004 - Is the concept of rate limiting referred to with a single canonical term throughout the spec (e.g., always "rate limiting" or always "limitación de tasa"), avoiding mixing translations? [Consistency, Spec §FR-2, §Edge Cases] — Cumple: se usa "rate_limit"/"rate limiting" como término técnico canónico del plugin, sin mezclar traducciones.
- [x] CHK005 - Is the client identification key term (`{client_ip}` vs "IP del cliente" vs "clave de rate limit") used consistently across FR-1, FR-2, Edge Cases, and Clarifications? [Consistency, Spec §FR-1, §FR-2, §Clarifications] — Cumple: `{client_ip}` consistente; las referencias a "IP de la conexión remota" lo describen sin conflicto.
- [x] CHK006 - Is `handle_errors` referenced consistently (not alternating between "bloque de manejo de errores", "error handler", and `handle_errors`) when referring to the Caddy directive? [Consistency, Spec §FR-3, §Quickstart] — Cumple: `handle_errors` se usa como directiva técnica del nombre.
- [x] CHK007 - Is the fail-open posture referred to with a single consistent term (e.g., "fail-open", "postura de apertura", "priorizar disponibilidad") throughout Edge Cases and Clarifications? [Consistency, Spec §Edge Cases, §Clarifications Q2] — Cumple: "fail-open" consistente.
- [x] CHK008 - Is the zone name `login_limit` referenced identically (no variant spellings like `login-limit`, `loginLimit`) across spec, plan, data-model, and quickstart? [Consistency, Cross-Artifact] — Cumple: `login_limit` idéntico en todos los artefactos.

## Spec-Prose vs Runtime Artifact Alignment

- [x] CHK009 - Does the 429 JSON payload text in the Clarification (Q7) match character-for-character the payload specified in FR-3? [Consistency, Spec §Clarifications Q7 vs §FR-3] — Cumple: carácter por carácter.
- [x] CHK010 - Does the 429 payload in FR-3 match the payload in the Success Criteria section? [Consistency, Spec §FR-3 vs §Success Criteria] — Cumple: idéntico.
- [x] CHK011 - Is the `Content-Type` header value in the 429 response specified identically (not "JSON" in one place and `application/json` in another)? [Clarity, Spec §FR-3, §Quickstart] — Cumple: `application/json` consistente.
- [x] CHK012 - Does the Caddyfile sample in quickstart.md use the same key (`{client_ip}`) as specified in FR-2, not the superseded `{http.request.header.X-Forwarded-For}`? [Consistency, Spec §FR-2 vs Quickstart Caddyfile] — Cumple: quickstart usa `{client_ip}`.

## Cross-Artifact Terminology Consistency

- [x] CHK013 - Are the match paths identical (character-for-character, including leading `/` and wildcard `*`) across spec FR-2, Edge Cases, data-model.md, and quickstart.md? [Consistency, Spec §FR-2 vs Edge Cases vs data-model.md vs quickstart.md] — Cumple: las 4 rutas idénticas en todos.
- [x] CHK014 - Is the `trusted_proxies` directive referenced consistently across spec, plan, and quickstart (not mixing with the deprecated `client_ip_headers`)? [Consistency, Spec §FR-1 vs Plan vs Quickstart] — Cumple: sin mezcla con `client_ip_headers`.
- [x] CHK015 - Do all historical clarification entries (Q1-Q10) reference the final key decision (Q12) without leaving contradictory unqualified references to `{http.request.header.X-Forwarded-For}` as the active key? [Consistency, Spec §Clarifications] — Cumple: las referencias históricas llevan nota/cross-ref a Q12/Q15; no queda texto sin calificar tratando XFF como clave activa.
- [x] CHK016 - Are the persistence limitation and NAT limitation described with consistent terminology between Edge Cases and Clarifications (Q14, Q5)? [Consistency, Spec §Edge Cases vs §Clarifications] — Cumple: terminología consistente.

## Completeness of Language-Sensitive Requirements

- [x] CHK017 - Is the exact 429 JSON payload (`{"detail": "Demasiados intentos de inicio de sesión"}`) specified with character-level precision (accent marks, no trailing whitespace, UTF-8 encoding)? [Completeness, Spec §FR-3] — Cumple: con acento, sin trailing whitespace, UTF-8.
- [x] CHK018 - Is the Spanish text `"Demasiados intentos de inicio de sesión"` free of ambiguity regarding formal/informal tone and accent mark accuracy? [Clarity, Spec §FR-3] — Cumple: tono formal neutral, acentuación correcta.
- [x] CHK019 - Are requirements specified for the language of any user-facing messages beyond the 429 response body (e.g., error pages, health check responses, default landing page)? [Gap, Coverage] — Fuera de alcance: el único mensaje user-facing del fix es el payload 429. Sin otros mensajes en el alcance de la feature. Aceptado.
- [x] CHK020 - Is the scope of the 100% ESPAÑOL mandate clarified for code-level artifacts (Caddyfile comments, entrypoint.sh script comments, log messages) vs. user-facing responses? [Gap, Clarity, Constitution §1] — Aclarado: el mandato aplica a contenido user-facing y a la documentación/prosa de los artefactos; las directivas y vocabulario técnico de Caddy se mantienen en inglés por convención técnica (nota en CHK003).

## Post-Clarify Session (Q15) — Language/Terminology Consistency

### Requirement Consistency

- [x] CHK021 - Is the `trusted_proxies` terminology consistent across the spec (FR-1, FR-2, Edge Cases, Q15) — every mention clearly states it is NOT configured, with no leftover text implying it IS configured? [Consistency, Spec §FR-1 vs §FR-2 vs §Edge Cases vs §Clarifications Q15] — Cumple: toda mención indica que NO se configura.
- [x] CHK022 - Do all historical clarification entries (Q3, Q10, Q12, Q17) that previously referenced configuring `trusted_proxies` now carry an explicit cross-reference to Q15 (the final decision), leaving no unqualified contradictory statement? [Consistency, Spec §Clarifications Q3/Q10/Q12/Q17 vs Q15] — Cumple: las entradas históricas llevan cross-ref a Q15.
- [x] CHK023 - Is the key-resolution description consistent between FR-2 ("IP de la conexión remota") and Edge Cases ("IP interna del contenedor/ingress") — no conflicting granularity that changes the meaning? [Consistency, Spec §FR-2 vs §Edge Cases] — Cumple: ambas descripciones son coherentes (misma resolución a nivel contenedor).

### Requirement Clarity

- [x] CHK024 - Is the term describing the rate limit scope (`nivel de instancia`, `nivel del contenedor/ingress`, `no por usuario final`) used precisely and unambiguously wherever the Q15 implication is described? [Clarity, Spec §Edge Cases, §Clarifications Q15] — Cumple: término preciso y consistente.
- [x] CHK025 - Is the cross-artifact terminology consistent between the spec and the design docs (plan.md, data-model.md, quickstart.md, research.md) — e.g., the key always described as `{client_ip}` without `trusted_proxies`, never reverting to `X-Forwarded-For` or `private_ranges`? [Consistency, Cross-Artifact, Spec §FR-2] — Cumple: `{client_ip}` sin `trusted_proxies`, sin revertir.
- [x] CHK026 - Is the phrase "NO se configura trusted_proxies" consistently worded (not alternating with "sin trusted_proxies", "se omite trusted_proxies", "no hay trusted_proxies") across all sections and artifacts? [Clarity, Consistency] — Cumple: formulación consistente en toda la doc.

### Completeness of Language-Sensitive Requirements

- [x] CHK027 - Is the security limitation introduced by Q15 (rate limit a nivel instancia, no por usuario final) expressed in the project language (Spanish) with the same precision across Clarifications, Edge Cases, and data-model.md? [Completeness, Spec §Edge Cases vs Data Model] — Cumple: expresada en español con la misma precisión.
- [x] CHK028 - Are the rejected alternatives for `trusted_proxies` (`static private_ranges`, `static <rango fijo>`) documented in research.md with clear Spanish-language rationale, avoiding English-only reasoning? [Completeness, Research.md] — Cumple: en research.md con racional en español.

### Acceptance Criteria Quality

- [x] CHK029 - Can the DoD verification of the 429 behavior be described in Spanish consistently with the payload text, without introducing English-only phrases for the acceptance check? [Measurability, Spec §Success Criteria, §Clarifications Q13] — Cumple: descripción del DoD 429 en español coherente con el payload.

## Post-Clarify Session (Q16) — Language/Terminology Consistency

### Requirement Consistency

- [x] CHK030 - Is the version-pinning decision (Q16) terminology consistent across the spec (Clarifications Q16, Edge Cases), plan.md, research.md, data-model.md, quickstart.md, and tasks.md — all describing the plugin version as "fijada"/"fijar la versión" with no leftover text implying an unpinned floating version remains? [Consistency, Cross-Artifact, Spec §Clarifications Q16] — Cumple: terminología "fijar la versión"/pin consistente; sin texto que implique versión flotante.
- [x] CHK031 - Are the minimum-version constraints expressed uniformly (`≥ v1.1.0` / "≥ v1.1.0") across spec, plan, research, and tasks, avoiding contradictory phrasing like "v1.1" vs "v1.1.0" vs "v1.1+"? [Consistency, Spec §Edge Cases vs Plan vs Tasks] — Cumple: "≥ v1.1.0" uniforme.
- [x] CHK032 - Is the `Dockerfile` reference consistent across artifacts (always `Dockerfile:7` / `xcaddy build --with github.com/mholt/caddy-ratelimit@<versión fija>`) without drift to an unpinned `xcaddy build --with ...` anywhere? [Consistency, Cross-Artifact, Plan §Source Code] — Cumple: referencia `Dockerfile:7` + pin consistente.

### Requirement Clarity

- [x] CHK033 - Is the term "build determinista" (used to justify Q16) used precisely and consistently in Spanish, without alternating to English-only terms ("reproducible build", "deterministic") across artifacts? [Clarity, Cross-Artifact, Plan §Constitution Check] — Cumple: "build determinista" en español.
- [x] CHK034 - Is the rationale for pinning (eliminar el riesgo de regresión por versión flotante) expressed in the project language (Spanish) with the same wording or a clearly equivalent phrasing in spec, plan, and research, avoiding ambiguity? [Clarity, Spec §Clarifications Q16 vs Plan vs Research] — Cumple: racional equivalente en español.

### Completeness of Language-Sensitive Requirements

- [x] CHK035 - Is the Q16 decision documented as part of the feature scope in all relevant artifacts (spec §Edge Cases, plan §Summary/Constraints, research Findings, tasks T007), with no artifact silently omitting the version-pin requirement? [Completeness, Cross-Artifact, Spec §Edge Cases vs Tasks T007] — Cumple: presente en spec (FR-6/Edge Cases/Q16), plan, research, tasks T007.
- [x] CHK036 - Is the New Task T007 wording in tasks.md consistent with the spec's Q16 scope (Dockerfile pin), using matching file path and plugin reference, without introducing a differently-worded scope? [Consistency, Spec §Clarifications Q16 vs Tasks.md T007] — Cumple: T007 coherente con FR-6/Q16 (Dockerfile, `github.com/mholt/caddy-ratelimit@<versión fija ≥ v1.1.0>`).

### Acceptance Criteria Quality

- [x] CHK037 - Is the verification of the version pin in quickstart.md (step 0: `grep "xcaddy build" Dockerfile` must include `@<versión fija>`) expressed in Spanish and consistent with the spec's acceptance criteria, without English-only acceptance language? [Measurability, Quickstart.md step 0 vs Spec §Success Criteria] — Cumple: paso 0 en español, coherente con los criterios de aceptación.
