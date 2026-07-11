# Tasks: Fix Edit Liquidación Incidents Loading

**Input**: Design documents from `/specs/041-fix-edit-liquidacion-incidents/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested. Manual validation via quickstart.md scenarios.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup needed — existing project structure, no new dependencies

*(Skipped — all changes target existing files)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add state variables that the UI components will depend on

- [X] T001 Add `incidentes_asociados_liquidacion: List[Dict[str, Any]] = []` state var to `LiquidacionesState` in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T002 Add `loading_incidentes_asociados: bool = False` state var to `LiquidacionesState` in `src/presentacion_reflex/state/liquidaciones_state.py`

**Checkpoint**: State vars ready — UI components can now reference them

---

## Phase 3: User Story 1 - Visualizar Incidentes Asociados al Editar una Liquidación (Priority: P1) 🎯 MVP

**Goal**: When opening the edit modal, the user sees all associated incidents in a read-only table and the observations field loads correctly.

**Independent Test**: Open edit modal for a liquidation with 2+ associated incidents → verify table shows all incidents with descriptions, states, and amounts. Open edit modal for a liquidation with observations → verify textarea shows stored text.

### Implementation for User Story 1

- [X] T003 [US1] Add `cargar_incidentes_asociados(id_liquidacion: int)` event handler to `LiquidacionesState` in `src/presentacion_reflex/state/liquidaciones_state.py` — executes SQL JOIN query on INCIDENTE_LIQUIDACION + INCIDENTES, populates `incidentes_asociados_liquidacion`, handles errors with toast notification
- [X] T004 [US1] Fix `observaciones` None handling in `open_edit_modal` at `src/presentacion_reflex/state/liquidaciones_state.py` line 656 — change `str(liquidacion.get("observaciones", ""))` to `str(liquidacion.get("observaciones") or "")`
- [X] T005 [US1] Call `cargar_incidentes_asociados(id_liquidacion)` at the end of `open_edit_modal` in `src/presentacion_reflex/state/liquidaciones_state.py` after populating `form_data`
- [X] T006 [P] [US1] Add incidents display section to `liquidacion_edit_form` in `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` — read-only table with columns: ID, Descripción, Estado, Estado Pago, Valor Descuento; loading spinner; empty state message
- [X] T007 [US1] Add error toast with retry button to `open_edit_modal` in `src/presentacion_reflex/state/liquidaciones_state.py` — show `rx.toast` with error message and "Reintentar" action when data fetch fails, keep modal open
- [X] T008 [US1] Clear `incidentes_asociados_liquidacion` and `loading_incidentes_asociados` in `close_modal` handler in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T009 [US1] Refresh `incidentes_asociados_liquidacion` after successful association in `asociar_incidentes_seleccionados` in `src/presentacion_reflex/state/liquidaciones_state.py` — call `cargar_incidentes_asociados` after closing the selection modal

**Checkpoint**: Edit modal now shows associated incidents and observations load correctly

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Regression validation and edge case handling

- [X] T010 [P] Validate single incident display — verify edit modal shows exactly 1 row when liquidation has 1 associated incident
- [X] T011 [P] Validate empty state — verify edit modal shows "No hay incidentes asociados" when liquidation has 0 incidents
- [X] T012 [P] Run quickstart.md validation scenarios V1-V9 to confirm no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped — no setup needed
- **Foundational (Phase 2)**: T001, T002 can run in parallel — no dependencies
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
  - T003 (event handler) must complete before T005 (call from open_edit_modal)
  - T006 (UI component) can run in parallel with T003/T004/T005 (different files)
  - T007, T008, T009 depend on T003 completion
- **Polish (Phase 4)**: Depends on Phase 3 completion

### Within User Story 1

```
T001, T002 (parallel) → T003 → T005 → T007, T008, T009
                       T004 (parallel with T003)
                       T006 (parallel with T003-T005, different file)
```

### Parallel Opportunities

- T001 + T002: Different state vars, same file, no conflict
- T003 + T004: Same file but different methods, can be done sequentially or in parallel
- T006: Different file (component vs state), fully parallel with T003-T005
- T010 + T011 + T012: Independent validation scenarios

---

## Parallel Example: User Story 1

```bash
# Phase 2 (parallel):
Task: "Add incidentes_asociados_liquidacion state var"
Task: "Add loading_incidentes_asociados state var"

# Phase 3 (mixed):
Task: "Add cargar_incidentes_asociados event handler" (state file)
Task: "Fix observaciones None handling" (state file, sequential with above)
Task: "Add incidents display section to edit form" (component file, PARALLEL)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Add state variables
2. Complete Phase 3: Implement incident display + observations fix
3. **STOP and VALIDATE**: Test with quickstart.md scenarios V1-V7
4. Complete Phase 4: Regression testing

### Incremental Delivery

1. State vars added → Foundation ready
2. Event handler + UI component → Users can see incidents in edit modal (MVP!)
3. Error handling + cleanup → Production-ready
4. Regression testing → Quality assured

---

## Notes

- This is a frontend-only fix (no DB schema changes, no repository changes)
- All SQL queries follow existing patterns in `open_seleccion_incidentes_modal`
- The incidents table is READ-ONLY in the edit modal (view only, no edit/delete)
- "Seleccionar Incidentes" button remains for ADDING new associations
- After adding new incidents, the list refreshes automatically
