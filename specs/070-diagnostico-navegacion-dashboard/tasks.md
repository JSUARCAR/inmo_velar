# Tasks: 070-diagnostico-navegacion-dashboard

**Input**: Design documents from `/specs/070-diagnostico-navegacion-dashboard/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify local environment, PostgreSQL connection, and ensure clean working tree.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T002 Ensure consistent Loading/Spinner component is available for pages (or rely on `rx.spinner`).
- [x] T003 Implement `NavigationGenerationMixin` in `src/presentacion_reflex/state/navigation_mixin.py` (o similar) to manage `generation_id` timestamps. Debe incluir soporte para descartar mutaciones e imprimir `[DROP] Mutación caducada (Generación mismatch)` en los logs.
- [x] T004 Implementar helpers para "Graceful Rollback" en el Mixin o Base State (e.g. redirigir a `/` con `rx.toast("Error de conexión. Redirigiendo al Dashboard", color="yellow")`).

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Navegación Exitosa y Concurrencia Post-Login (Priority: P1) — MVP

**Goal**: Navegar fluidamente, renderizar loaders, evitar race conditions y manejar fallos de red con rollback.

**Independent Test**: Scenario 1, Scenario 2, Scenario 3 in `quickstart.md`.

### Implementation for User Story 1

- [x] T005 [P] [US1] Refactor `on_load` in `src/presentacion_reflex/state/personas_state.py` to use `@rx.event(background=True)`, pass the generation ID, and trigger Graceful Rollback if the backend task throws an exception.
- [x] T006 [P] [US1] Refactor `on_load` in `src/presentacion_reflex/state/alertas_state.py` to use `@rx.event(background=True)` with generation ID and exception handling for Rollback.
- [x] T007 [P] [US1] Refactor `on_load` in `src/presentacion_reflex/state/alertas_dashboard_state.py` to use `@rx.event(background=True)` with generation ID and exception handling for Rollback.
- [x] T008 [P] [US1] Update `src/presentacion_reflex/pages/personas.py` UI to show `rx.spinner()` when `is_loading` is true.
- [x] T009 [P] [US1] Update `src/presentacion_reflex/pages/alertas.py` UI to show `rx.spinner()` when `is_loading` is true.
- [x] T010 [P] [US1] Update `src/presentacion_reflex/pages/dashboard.py` UI to show `rx.spinner()` when `is_loading` is true.

**Checkpoint**: At this point, User Story 1 should be fully functional (Navigation and Race conditions controlled).

---

## Phase 4: User Story 2 - Validación de Sesión Transparente (Priority: P1)

**Goal**: Garantizar que el auth state expulse al usuario si el token falla, preservando el token sin bloqueos sincrónicos.

**Independent Test**: Scenario 4 in `quickstart.md`.

### Implementation for User Story 2

- [x] T011 [US2] Refactor `on_load` in `src/presentacion_reflex/state/auth_state.py`. Convert to background task, check token validity. Si falla, redirigir a `/login` explícitamente y mostrar `rx.toast`.

**Checkpoint**: Authentication flows fully stabilized.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T012 Run all `quickstart.md` validation scenarios.
- [x] T013 Commit changes with clear conventional commits mapping to the feature.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories**: Depend on Foundational phase
- **Polish (Final Phase)**: Depends on all user stories being complete

### Parallel Opportunities

- UI Updates (T008, T009, T010) and State updates (T005, T006, T007) can be done in parallel once the Mixin is built.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and 2.
2. Complete Phase 3 (US1).
3. Validate independent tests before moving to Phase 4 (Auth Fixes).
