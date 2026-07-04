---
description: "Task list template for feature implementation"
---

# Tasks: debug-incident-selection

**Input**: Design documents from `/specs/010-debug-incident-selection/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify local environment and Reflex setup in `rxconfig.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T002 Identify State class managing incidents in `src/presentacion_reflex/pages/liquidaciones.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Diagnosticar y Reparar el Modal de Selección de Incidentes (Priority: P1) 🎯 MVP

**Goal**: Reparar el flujo de UI para que el botón abra el modal y liste incidentes pendientes.

**Independent Test**: Lanzar la UI con `reflex run`, cliquear "Seleccionar Incidentes", verificar que el modal se abre y que los incidentes mostrados no están pagados.

### Implementation for User Story 1

- [X] T003 [US1] Fix button `on_click` event in `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` to mutate the correct modal state boolean.
- [X] T004 [US1] Apply `pointer-events: auto` and correct `z-index` styling in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py` to prevent Radix UI block.
- [X] T005 [US1] Update incident filtering logic in the state (associated with `src/presentacion_reflex/pages/liquidaciones.py` or its `Estado`) to exclude `estado_pago == 'Pagado'`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T006 Run quickstart.md validation locally to verify UI rendering without errors.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- UI components and state must be aligned before finalizing the story.

### Parallel Opportunities

- Bug fixes in `liquidacion_edit_form.py` and `modal_seleccion_incidentes.py` can be researched concurrently.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently using `quickstart.md`
5. Deploy/demo si el error está resuelto.
