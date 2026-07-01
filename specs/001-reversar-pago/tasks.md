# Tasks: Reversar Pago de Liquidación

**Input**: Design documents from `/specs/001-reversar-pago/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests included per spec requirement for audit trail and idempotency verification.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing infrastructure and register new permission

- [x] T001 Verify existing AUDITORIA_CAMBIOS table and LIQUIDACIONES trigger are active in the database
- [x] T002 Register "REVERSAR_PAGO" permission for "Liquidaciones" module in `scripts/add_liquidaciones_permissions.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend layer that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `reversar_pago()` method signature to `IRepositorioLiquidacion` Protocol in `src/dominio/interfaces/repositorio_liquidacion.py`
- [x] T004 [P] Implement `reversar_pago()` method in `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` — state check (Pagada), UPDATE clearing payment fields, explicit AUDITORIA_CAMBIOS insert for MOTIVO_REVERSION, transaction commit; return dict with exitosa/mensaje/id_liquidacion/estado_anterior/estado_nuevo; idempotent (if not Pagada, return success without changes)
- [x] T005 Implement `reversar_pago_liquidacion()` method in `src/aplicacion/servicios/servicio_financiero.py` — validate motivo >= 10 chars, call repo.reversar_pago(), handle idempotency, return result dict
- [x] T006 Add state variables to `LiquidacionesState` in `src/presentacion_reflex/state/liquidaciones_state.py`: `show_reverse_pago_confirm: bool = False`, `reverse_pago_liquidacion_id: int = 0`, `reverse_pago_motivo: str = ""`

**Checkpoint**: Backend complete — reversal logic works via direct service call

---

## Phase 3: User Story 1 — Reversar Pago Individual (Priority: P1) 🎯 MVP

**Goal**: Allow authorized users to reverse a payment on a single liquidation, transitioning it from "Pagada" to "Aprobada" with full audit trail.

**Independent Test**: Register a liquidation as paid, then reverse it; verify state returns to "Aprobada", payment fields cleared, audit record exists.

### Implementation for User Story 1

- [x] T007 [US1] Implement `open_reverse_pago_confirm(id_liquidacion: int)` event handler in `src/presentacion_reflex/state/liquidaciones_state.py` — loads liquidation data, sets reverse_pago_liquidacion_id, opens dialog
- [x] T008 [US1] Implement `close_reverse_pago_confirm()` event handler in `src/presentacion_reflex/state/liquidaciones_state.py` — clears state variables, closes dialog
- [x] T009 [US1] Implement `set_reverse_pago_motivo(value: str)` event handler in `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T010 [US1] Implement `confirmar_reversar_pago()` event handler in `src/presentacion_reflex/state/liquidaciones_state.py` — validates motivo >= 10 chars, calls servicio.reversar_pago_liquidacion(), closes dialog, refreshes list, shows toast
- [x] T011 [P] [US1] Create confirmation dialog component in `src/presentacion_reflex/components/liquidaciones/reverse_pago_confirm_dialog.py` — alert_dialog with propietario, dirección, período, monto, fecha_pago, required motivo textarea, cancel/confirm buttons; follows existing reverse_confirm_dialog.py pattern
- [x] T012 [US1] Add "Reversar Pago" button to table rows in `src/presentacion_reflex/pages/liquidaciones.py` — visible only when estado=="Pagada" AND AuthState.check_action("Liquidaciones", "REVERSAR_PAGO"); icon: rotate_ccw, color_scheme: orange
- [x] T013 [US1] Add "Reversar Pago" button to detail modal in `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` — visible only when estado=="Pagada"; triggers open_reverse_pago_confirm
- [x] T014 [US1] Import reverse_pago_confirm_dialog in `src/presentacion_reflex/pages/liquidaciones.py` and add to liquidaciones_page() component tree

**Checkpoint**: Individual payment reversal fully functional and testable via UI

---

## Phase 4: User Story 2 — Confirmación con Impacto (Priority: P1)

**Goal**: Display a clear confirmation dialog with liquidation details before executing reversal.

**Independent Test**: Open the confirmation dialog and verify it shows all required fields; verify cancel closes without changes.

### Implementation for User Story 2

> **NOTE**: This story is primarily fulfilled by T011 (dialog component) from US1. The following tasks add remaining detail.

- [x] T015 [US2] Verify dialog shows propietario, dirección de propiedad, período, neto a pagar, and fecha de pago original in `src/presentacion_reflex/components/liquidaciones/reverse_pago_confirm_dialog.py`
- [x] T016 [US2] Add loading state to confirm button during reversal execution in `src/presentacion_reflex/components/liquidaciones/reverse_pago_confirm_dialog.py`

**Checkpoint**: Confirmation dialog complete with all required information fields

---

## Phase 5: User Story 3 — Auditoría Completa (Priority: P2)

**Goal**: Every reversal generates a complete audit trail with usuario, fecha/hora, motivo, estado anterior/posterior.

**Independent Test**: Execute a reversal, query AUDITORIA_CAMBIOS, verify all required fields present including MOTIVO_REVERSION record.

### Implementation for User Story 3

> **NOTE**: Audit trail is primarily implemented in T004 (repository). The following tasks add verification.

- [x] T017 [US3] Add explicit AUDITORIA_CAMBIOS insert for MOTIVO_REVERSION in `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` — insert record with CAMPO_MODIFICADO='MOTIVO_REVERSION', VALOR_NUEVO=motivo_text, same ID_REGISTRO and USUARIO as the UPDATE records
- [ ] T018 [US3] Verify audit trail completeness in `tests/integration/test_reversar_pago_integration.py` — test that reversal generates records for ESTADO_LIQUIDACION, FECHA_PAGO, METODO_PAGO, REFERENCIA_PAGO, PAGADA_POR, PAGADA_EN, and MOTIVO_REVERSION

**Checkpoint**: Audit trail complete and verifiable

---

## Phase 6: User Story 4 — Permisos y Seguridad (Priority: P2)

**Goal**: Only authorized users can see and execute the reversal action.

**Independent Test**: Login as user without REVERSAR_PAGO permission; verify button is not visible. Login as admin; verify button is always visible.

### Implementation for User Story 4

> **NOTE**: Permission checks are integrated into T012 and T013. The following tasks verify and complete permission enforcement.

- [x] T019 [US4] Add AuthState.check_action("Liquidaciones", "REVERSAR_PAGO") guard to "Reversar Pago" button in table view in `src/presentacion_reflex/pages/liquidaciones.py`
- [x] T020 [US4] Add AuthState.check_action("Liquidaciones", "REVERSAR_PAGO") guard to "Reversar Pago" button in detail modal in `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py`

**Checkpoint**: Permission enforcement complete at UI level

---

## Phase 7: User Story 5 — Reversión Masiva por Propietario (Priority: P3)

**Goal**: Allow bulk reversal of all paid liquidations for a owner in a specific period, selectively reversing only those in "Pagada" state.

**Independent Test**: Owner with 3 liquidations (2 Pagada, 1 Aprobada) for a period; execute bulk reversal; verify 2 reversed, 1 ignored.

### Implementation for User Story 5

- [x] T021 [US5] Implement `reversar_pago_por_propietario_y_periodo()` method in `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` — iterate liquidations for owner+period, reverse only Pagada ones, return dict with reversed/ignored counts and IDs
- [x] T022 [US5] Implement `reversar_pago_propietario()` service method in `src/aplicacion/servicios/servicio_financiero.py` — validate inputs, call repo method, return bulk result
- [ ] T023 [US5] Add `open_reverse_pago_bulk_confirm(id_propietario, periodo)` event handler in `src/presentacion_reflex/state/liquidaciones_state.py`
- [x] T024 [US5] Add `confirmar_reversar_pago_masivo()` event handler in `src/presentacion_reflex/state/liquidaciones_state.py` — calls servicio.reversar_pago_propietario(), shows result toast with counts
- [ ] T025 [US5] Add bulk "Reversar Pagos" button to grouped table view in `src/presentacion_reflex/pages/liquidaciones.py` — visible only when estado=="Pagada" AND AuthState.check_action("Liquidaciones", "REVERSAR_PAGO")
- [ ] T026 [US5] Create bulk reversal confirmation dialog component in `src/presentacion_reflex/components/liquidaciones/reverse_pago_bulk_confirm_dialog.py`

**Checkpoint**: Bulk reversal complete and independently testable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T027 [P] Write unit tests for reversar_pago in `tests/unit/test_entidades/test_reversar_pago.py` — test idempotency, state validation, motivo validation
- [ ] T028 [P] Write integration tests in `tests/integration/test_reversar_pago_integration.py` — test full flow from service to DB, audit trail verification
- [ ] T029 Run quickstart.md validation scenarios V1-V8
- [ ] T030 Verify no regressions in existing liquidaciones functionality (create, edit, approve, pay, cancel, existing reversal)
- [x] T031 Run linter (ruff) and type checker (mypy) on all modified files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — MVP
- **Phase 4 (US2)**: Depends on Phase 3 (T011)
- **Phase 5 (US3)**: Depends on Phase 2 (T004, T017)
- **Phase 6 (US4)**: Depends on Phase 3 (T012, T013)
- **Phase 7 (US5)**: Depends on Phase 2 (T004, T005)
- **Phase 8 (Polish)**: Depends on all desired phases

### User Story Dependencies

- **US1 (P1)**: After Foundational — No dependencies on other stories
- **US2 (P1)**: After US1 — Extends the confirmation dialog from US1
- **US3 (P2)**: After Foundational — Audit trail is in repository layer
- **US4 (P2)**: After US1 — Permission guards added to US1's buttons
- **US5 (P3)**: After Foundational — Independent from US1-US4

### Parallel Opportunities

- T003 + T004: Interface and implementation can be developed together
- T011 (dialog): Can be developed in parallel with T007-T010 (state handlers)
- T027 + T028: Unit and integration tests can run in parallel
- US3 + US4 can run in parallel after US1 completes
- US5 can start as soon as Phase 2 is complete (parallel with US1)

---

## Parallel Example: User Story 1

```bash
# Parallel: Dialog component + State handlers (different files)
Task T011: Create reverse_pago_confirm_dialog.py
Task T007-T010: Implement event handlers in liquidaciones_state.py

# Sequential: UI integration (depends on both above)
Task T012: Add button to liquidaciones.py
Task T013: Add button to liquidacion_detail_modal.py
Task T014: Import and integrate dialog in page
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (permissions)
2. Complete Phase 2: Foundational (backend: interface + repo + service)
3. Complete Phase 3: User Story 1 (state + UI)
4. Complete Phase 4: User Story 2 (dialog completeness)
5. **STOP and VALIDATE**: Test individual reversal end-to-end
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Backend ready
2. Add US1 + US2 → Individual reversal works → **MVP!**
3. Add US3 → Audit trail complete
4. Add US4 → Permission enforcement
5. Add US5 → Bulk reversal
6. Polish → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
