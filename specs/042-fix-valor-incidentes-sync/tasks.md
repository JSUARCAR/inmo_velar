# Tasks: Fix Valor Incidentes Auto-Sync

**Input**: Design documents from `/specs/042-fix-valor-incidentes-sync/`

**Prerequisites**: plan.md (template only), spec.md (complete with 1 user story P1)

**Tests**: Not requested in spec — test tasks omitted.

**Organization**: Single user story (US1) — all tasks belong to Phase 3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1)
- File paths are exact and verifiable

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing infrastructure — no new files needed

- [X] T001 Verify PostgreSQL database connection and `UpperCaseCursorWrapper` working in `src/infraestructura/persistencia/database.py`
- [X] T002 Verify `LIQUIDACIONES` table has `VALOR_INCIDENTES INTEGER DEFAULT 0` column in `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix the backend sync mechanism that US1 depends on

**⚠️ CRITICAL**: US1 cannot work until this phase is complete

- [X] T003 [P] Ensure `asociar_incidente` uses DB transaction wrapping for atomicity in `src/aplicacion/servicios/servicio_incidente_liquidacion.py` (lines 310-333)
- [X] T004 [P] Ensure `desasociar_incidente` uses DB transaction wrapping for atomicity in `src/aplicacion/servicios/servicio_incidente_liquidacion.py` (lines 445-472)

**Checkpoint**: Backend sync is atomic — US1 implementation can begin

---

## Phase 3: User Story 1 - Sincronización Automática del Valor de Incidentes (Priority: P1) 🎯 MVP

**Goal**: When an incident is associated/disassociated with a liquidation, `valor_incidentes` updates automatically and the edit form shows the correct value.

**Independent Test**: Associate incident ID 54 ($75.000) to liquidation 622 → verify `valor_incidentes` = $75.000 in edit modal and DB.

### Implementation for User Story 1

- [X] T005 [US1] Change `valor_incidentes` field in `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` (lines 191-193) to use `form_field_readonly` instead of `form_field_editable` since it's computed automatically.
- [X] T006 [US1] Fix `open_edit_modal` to always load `valor_incidentes` from DB (not local state) in `src/presentacion_reflex/state/liquidaciones_state.py` (line 661)
- [X] T007 [US1] Fix `asociar_incidentes_seleccionados` to refresh `form_data["valor_incidentes"]` from DB after sync completes in `src/presentacion_reflex/state/liquidaciones_state.py` (line 2287) — add explicit reload instead of relying on `load_liquidaciones()` background task
- [X] T008 [US1] Fix `desasociar_incidente_ui` to refresh `form_data["valor_incidentes"]` from DB after sync completes in `src/presentacion_reflex/state/liquidaciones_state.py` (line 2077)
- [X] T009 [US1] Fix `save_liquidacion` to NOT overwrite `valor_incidentes` — explicitly remove it from the payload sent to `actualizar_liquidacion` in `src/presentacion_reflex/state/liquidaciones_state.py` (line 1205)
- [X] T010 [US1] Enforce protection in `servicio_financiero.py` (line 862) inside `actualizar_liquidacion` by preventing overwriting of `valor_incidentes` con form data — always ignore the `valor_incidentes` field in `datos_actualizados`.

**Checkpoint**: US1 fully functional — `valor_incidentes` syncs in real-time and displays correctly in edit modal

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validation and edge case handling

- [X] T010 [US1] Add toast notification on sync failure with "Reintentar" button in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T011 [US1] Validate edge case: associate incident with $0 discount does not corrupt `valor_incidentes` in `src/aplicacion/servicios/servicio_incidente_liquidacion.py` (Confirmed guard clause `if valor_descuento <= 0:`)
- [X] T012 Manual end-to-end test: login as jsuarcar, liquidation 622, associate incident 54, verify $75.000 in edit modal and DB

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS US1
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **Polish (Phase 4)**: Depends on Phase 3 completion

### Within User Story 1

- T005 (form read-only) — independent, can run first
- T006 (open_edit_modal) — independent, can run in parallel with T005
- T007 (asociar refresh) — depends on T006 pattern
- T008 (desasociar refresh) — depends on T006 pattern, parallel with T007
- T009 (form overwrite guard) — independent, can run in parallel with T005-T008

### Parallel Opportunities

```
# Phase 1 — both tasks independent:
T001 + T002

# Phase 2 — both tasks independent:
T003 + T004

# Phase 3 — max parallelism:
T005 + T006 + T009 (all different files)
T007 + T008 (same file, sequential)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify infrastructure)
2. Complete Phase 2: Foundational (atomic transactions)
3. Complete Phase 3: User Story 1 (all 5 tasks)
4. **STOP and VALIDATE**: Test liquidation 622 end-to-end
5. Deploy if ready

### Recommended Task Order (Sequential)

```
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012
```

---

## Notes

- Root causes identified: (a) `valor_incidentes` editable in form, (b) `load_liquidaciones()` runs async causing race conditions, (c) `actualizar_liquidacion` overwrites from stale form data
- Backend sync code (`asociar_incidente`/`desasociar_incidente`) already works correctly — the bug is in the UI layer and form save path
- DB uses `UpperCaseCursorWrapper` — all column access must use UPPER_CASE keys
- `calcular_totales()` does NOT reset `valor_incidentes` — safe to call after update
