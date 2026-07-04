---
description: "Task list for fix-prod-diag-bugs implementation"
---

# Tasks: fix-prod-diag-bugs

**Input**: Design documents from `/specs/009-fix-prod-diag-bugs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify active environment and database access for production debugging setup.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Implement Pointer-events override globally in `src/presentacion_reflex/styles.py` (BASE_STYLE) for `rx.dialog.content` and `rx.popover.content`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Estabilidad en la Tabla de Incidentes (Priority: P1) 🎯 MVP

**Goal**: Paginación Server-Side (Limit/Offset) en tabla de Incidentes para prevenir desconexión de websockets de Reflex.

**Independent Test**: La vista de Incidentes carga en menos de 5 segundos sin arrojar el error `Disconnect websocket on page navigation`.

### Implementation for User Story 1

- [x] T003 [US1] Update `src/infraestructura/repositorios/repositorio_incidentes.py` to include `listar_incidentes_paginados(limit, offset)` and `contar_total_incidentes()`.
- [x] T004 [US1] Update `src/presentacion_reflex/estados/estado_incidentes.py` to handle pagination state variables and transition methods.
- [x] T005 [US1] Modify UI components in `src/presentacion_reflex/vistas/` (or wherever Incidentes UI is located) to include pagination controls (Prev/Next) and link to the state.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Apertura Confiable del Modal de Edición de Liquidaciones (Priority: P1)

**Goal**: Manejo seguro de valores nulos (None) en liquidaciones y script de backfill.

**Independent Test**: El modal "Editar Liquidación" abre exitosamente al primer click sin excepciones silenciosas de Pydantic.

### Implementation for User Story 2

- [x] T006 [P] [US2] Create data sanitization script `scripts/diagnostico/backfill_liquidaciones_nulas.py`.
- [x] T007 [US2] Update `src/aplicacion/dtos/liquidacion_dto.py` to use defensive `Optional[T]` types or default values for DB fields prone to nulls.
- [x] T008 [US2] Review `src/presentacion_reflex/estados/estado_liquidaciones.py` to ensure hydration process tolerates missing data correctly.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Eliminación de Liquidaciones sin Bloqueos de UI (Priority: P2)

**Purpose**: Fix UI lockups after closing modals, by enforcing strict Radix UI `pointer-events: auto` defaults.

- [x] T009 [US3] Verify delete interaction UI components in `src/presentacion_reflex/vistas/` ensure they inherit the global `BASE_STYLE` overrides made in Phase 2 correctly.

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T010 [P] Ejecutar validación local según `specs/009-fix-prod-diag-bugs/quickstart.md`.
- [ ] T011 [P] Correr `pytest tests/diagnostics/test_prod_diag.py --headed` con variables de entorno para confirmar resolución total de bugs reportados.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies.
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies.
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends heavily on T002 from Phase 2.

### Parallel Opportunities

- T003, T004, T005 must be sequential within US1.
- T006 can run in parallel with T007/T008 in US2.
- US1, US2, and US3 can be worked on in parallel by different team members once Phase 2 is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Incidentes Paginación)
4. **STOP and VALIDATE**: Test User Story 1 independently.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add User Story 1 → Test independently.
3. Add User Story 2 → Test independently.
4. Add User Story 3 → Test independently.
