---
description: "Task list for playwright-validation feature"
---

# Tasks: playwright-validation

**Input**: Design documents from `/specs/007-playwright-validation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths are included in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Initialize/Verify testing environment (pytest, pytest-playwright) in the existing project root
- [X] T002 [P] Create `tests/e2e/` directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implement authentication fixture and trace capture configuration in `tests/e2e/conftest.py`
- [X] T004 Implement common UI navigation/login helpers in `tests/e2e/utils.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validación del Plan de Pago en Incidentes (Priority: P1) 🎯 MVP

**Goal**: Verificar que el Plan de Pago se visualice correctamente en el detalle de un incidente.

**Independent Test**: Can be fully tested by navigating to the Incidentes module and checking the UI state.

### Implementation for User Story 1

- [X] T005 [P] [US1] Create test file `tests/e2e/test_incidentes.py` and implement `test_visualizacion_plan_pago`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Selección de Incidentes en Liquidaciones (Priority: P1)

**Goal**: Verificar la funcionalidad de selección de incidentes en el modal de edición de liquidaciones.

**Independent Test**: Can be fully tested by opening the liquidation edit modal and selecting incidents.

### Implementation for User Story 2

- [X] T006 [P] [US2] Create test file `tests/e2e/test_liquidaciones.py` and implement `test_modal_seleccion_incidentes`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Eliminación de Liquidaciones (Priority: P1)

**Goal**: Validar la acción destructiva de eliminar una liquidación en un entorno seguro (Sandbox).

**Independent Test**: Can be fully tested by triggering the delete action on the Sandbox property and verifying the UI and Network response.

### Implementation for User Story 3

- [X] T007 [P] [US3] Implement `test_eliminar_liquidacion_sandbox` in `tests/e2e/test_liquidaciones.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T008 Run the full test suite using instructions from `specs/007-playwright-validation/quickstart.md` to ensure traces and screenshots are correctly generated upon failure or success.
- [X] T009 Document any issues found in the diagnostic report format.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1, US2, US3 can then proceed in parallel since they don't depend on each other.
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- All User Stories can be worked on in parallel by different developers.
- `test_incidentes.py` and `test_liquidaciones.py` can be written independently once `conftest.py` is ready.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently
4. Add User Story 3 → Test independently

---

## Phase 6: Convergence

- [X] T010 Implement robust login selectors or explicit waits in `tests/e2e/conftest.py` per US1 (partial)

---

## Phase 7: Convergence

- [X] T011 Update table row and modal locators in `tests/e2e/utils.py` and test files using flexible `get_by_text` selectors per US1/US2/US3 (partial)
