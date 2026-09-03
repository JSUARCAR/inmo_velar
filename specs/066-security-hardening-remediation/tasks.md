---
description: "Task list for feature implementation: 066-security-hardening-remediation"
---

# Tasks: 066-security-hardening-remediation

**Input**: Design documents from `/specs/066-security-hardening-remediation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api-documentos-auth.md, quickstart.md

**Tests**: Tests are excluded from this list as they were not explicitly requested to be implemented first via TDD, but the quickstart.md covers validation steps.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*(No general setup tasks required for this remediation)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 [P] Modify `SesionUsuario` to enforce absolute `fecha_fin` (`fecha_inicio + 8 horas`) in `src/dominio/entidades/sesion_usuario.py` and enforce the validation check.
- [X] T002 [P] Update `ServicioAutenticacion` to populate `fecha_fin` on session creation in `src/aplicacion/servicios/servicio_autenticacion.py`.
- [X] T003 Create authentication dependency `validar_sesion_api` (reads `_s` cookie and validates via `ServicioAutenticacion`) in `src/presentacion_reflex/api/documentos_api.py` to be shared.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Protección Inmediata de Credenciales de Producción (Priority: P1) 🎯 MVP

**Goal**: Eliminar credenciales hardcodeadas del código fuente.

**Independent Test**: Inspeccionar visualmente el código y arrancar la app usando solo variables de entorno (Escenario 1).

### Implementation for User Story 1

- [X] T004 [P] [US1] Remove hardcoded DB credentials and replace with ENV vars in `check_db.py`.
- [X] T005 [P] [US1] Remove hardcoded DB credentials and replace with ENV vars in `check_db_id.py`.
- [X] T006 [P] [US1] Remove hardcoded DB credentials and replace with ENV vars in `migraciones/run_migration_ipc.py`.
- [X] T007 [P] [US1] Remove hardcoded DB credentials and replace with ENV vars in `migraciones/migrate_to_railway.py`.
- [X] T008 [P] [US1] Remove fallback password `7323` and missing DB URL logic in `rxconfig.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Control de Acceso en APIs de Documentos (Priority: P1)

**Goal**: Proteger los 4 endpoints de API de documentos con validación de cookie `_s` y comprobación IDOR.

**Independent Test**: `curl` sin cookies a los endpoints devuelve 401 (Escenario 2).

### Implementation for User Story 2

- [X] T009 [P] [US2] Update `document_download_api.py` to add `dependencies=[Depends(validar_sesion_api)]` on FastAPI mount and remove `allow_credentials=True`.
- [X] T010 [P] [US2] Update `src/presentacion_reflex/api/pdf_download_api.py` to add `dependencies=[Depends(validar_sesion_api)]` on FastAPI mount and remove `allow_credentials=True`.
- [X] T011 [US2] Implement IDOR validation in `ServicioDocumentalElite` within `src/aplicacion/servicios/servicio_documental.py` to ensure user has relation to `entidad_id`.
- [X] T012 [US2] Update all endpoints in `src/presentacion_reflex/api/documentos_api.py` to require `validar_sesion_api` and trigger IDOR validation.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Higiene del Repositorio Git (Priority: P2)

**Goal**: Purgar archivos sensibles e historial del repositorio.

**Independent Test**: Clonar repositorio fresco y ejecutar `gitleaks` y `git log` sobre archivos sensibles (Escenarios 1 y 8).

### Implementation for User Story 3

- [X] T013 [US3] Create shell script `scripts/diagnostico/purge_git.sh` with `git filter-repo` commands to purge specific files (`.env`, `AGREGAR_A_ENV.txt`, `check_db.py`, `.playwright-mcp`, etc.). (Execution left to user/admin due to force-push implications).

---

## Phase 6: User Story 4 - Configuración Segura de Infraestructura HTTP (Priority: P2)

**Goal**: Añadir cabeceras de seguridad en producción.

**Independent Test**: Verificar HTTP headers con `curl -I` (Escenario 3).

### Implementation for User Story 4

- [X] T014 [US4] Modify `entrypoint.sh` to inject strict security headers (HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, -Server) in the `Caddyfile.runtime` generation.

---

## Phase 7: User Story 5 - Configuración Fail-Fast de Variables de Entorno Críticas (Priority: P2)

**Goal**: Evitar el arranque del backend si `SECRET_KEY` es insegura.

**Independent Test**: Iniciar backend sin `SECRET_KEY` termina con sys.exit(1) (Escenario 5).

### Implementation for User Story 5

- [X] T015 [US5] Implement `@field_validator("secret_key", mode="after")` in `src/infraestructura/configuracion/settings.py` and add fail-fast check upon instantiation.

---

## Phase 8: User Story 6 - Seguridad de Contenedor y Cadena de Suministro (Priority: P3)

**Goal**: Contenedor no-root y compilación segura de dependencias (Caddy).

**Independent Test**: `docker run whoami` devuelve `appuser` (Escenario 4).

### Implementation for User Story 6

- [X] T016 [US6] Modify `Dockerfile` to use multi-stage build with `caddy:2-builder` to compile `github.com/mholt/caddy-ratelimit`.
- [X] T017 [US6] Modify `Dockerfile` to create and use non-root `appuser`.

---

## Phase 9: User Story 7 - Fortalecimiento de Sesiones y Autenticación (Priority: P3)

**Goal**: Rate limit en endpoints de autenticación y finalización de requerimientos de sesión.

**Independent Test**: Enviar múltiples peticiones de login falla con HTTP 429 después de 5 intentos (Escenario 8).

### Implementation for User Story 7

- [X] T018 [US7] Update `entrypoint.sh` to include `rate_limit` directive for `@login_endpoint` in the `Caddyfile.runtime`.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T019 Update PostgreSQL users to use `app_velar` with least privileges via `scripts/setup_permissions.py` or new migration script.
- [X] T020 Run full end-to-end quickstart.md validation locally.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A
- **Foundational (Phase 2)**: BLOCKS all user stories (particularly US2).
- **User Stories (Phase 3+)**: Can proceed in priority order or in parallel.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### User Story Dependencies

- All user stories can be worked on independently after Phase 2, but US7 requires US6 for the Caddy ratelimit plugin binary support in Dockerfile.

### Within Each User Story

- Core logic changes before endpoints (e.g. US2 service validation before API routes).

### Parallel Opportunities

- T004 - T008 in US1 can be processed in parallel.
- US1, US3, US4, US5 are highly disjoint and can be worked on in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 2: Foundational
2. Complete Phase 3: User Story 1 (Remove Hardcoded credentials)
3. Complete Phase 4: User Story 2 (Endpoint Auth & IDOR)
4. **STOP and VALIDATE**: Verify critical fixes via Scenarios 1 and 2 in `quickstart.md`.
5. Proceed to P2 stories (US3, US4, US5).
