---
description: "Task list for fix-delete-liquidation implementation"
---

# Tasks: Fix Delete Liquidation

**Input**: Design documents from `/specs/006-fix-delete-liquidation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Read `GEMINI.md` to ensure Radix UI and Reflex z-index conventions are fresh in memory.


---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- No backend changes required (verified in `research.md`). Existing `servicio_financiero.py` soft delete logic is intact and valid.

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Fix Eliminación Silenciosa UI (Priority: P1) 🎯 MVP

**Goal**: Garantizar que la acción de Eliminar invoque correctamente el modal de confirmación, y que éste sea interactuable (no bloqueado por el DismissableLayer de Radix UI ni oculto por Z-Index).

**Independent Test**: Verificar Escenario 1 y 2 en `quickstart.md`. El modal debe abrirse y el checkbox debe ser clickeable.

### Implementation for User Story 1

- [x] T002 [US1] Enforce `pointer-events: auto` explicitly on the `rx.dialog.content` of `src/presentacion_reflex/components/liquidaciones/delete_confirm_dialog.py` to prevent interaction blocking.
- [x] T003 [US1] Apply the appropriate global Z-Index constant (from `styles.py` or inline if missing) to `delete_confirm_dialog.py`.
- [x] T004 [US1] Fix/Verify the `on_click` event binding on the trash icon button in `src/presentacion_reflex/pages/liquidaciones.py` to ensure `liq["id"]` is correctly evaluated and passed to `LiquidacionesState.open_delete_modal`.
- [x] T005 [US1] Fix/Verify the `on_click` event binding on the delete button within `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` to ensure it successfully triggers the state mutation.

**Checkpoint**: At this point, clicking the delete button must visually display the modal and allow checking the box.

---

## Phase 4: User Story 2 - Asegurar Respuesta Backend (Priority: P2)

**Goal**: Garantizar que al confirmar, el comando ejecute exitosamente el soft delete y actualice el UI asincrónicamente.

**Independent Test**: Verificar Escenario 3 y 4 en `quickstart.md`. La liquidación debe desaparecer sin errores y la BD actualizarse.

### Implementation for User Story 2

- [x] T006 [US2] Verify `confirmar_eliminar` inside `src/presentacion_reflex/state/liquidaciones_state.py` handles the loading state and yields `load_liquidaciones` appropriately without silently swallowing state race-conditions.

**Checkpoint**: The soft-delete flow should be 100% operational.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T007 Run the full UI validation workflow using `quickstart.md` (Scenario 1 through 4) locally.
- [x] T008 Code cleanup (remove print statements or debug logs added during the fix).
- [x] T009 Ensure UI matches Anthropic Design System guidelines (red buttons for destructive actions, correct icon sets).


---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Skipped/Ready
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 must be resolved before US2 can be tested.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Fix UI blocking and event binding first.
- **User Story 2 (P2)**: Depends on US1 being interactive.

### Parallel Opportunities

- T002, T003, T004, and T005 are related to UI but modify different files or isolated component trees. They can be inspected or edited sequentially or in parallel depending on the agent's context capability.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fix the `pointer-events` and bindings (US1).
2. Validate locally that the dialog appears.
3. If US2 works organically without further code edits (since the backend is already correct), close the loop.
4. Execute full regression testing (quickstart).
