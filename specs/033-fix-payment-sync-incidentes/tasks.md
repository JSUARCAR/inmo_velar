# Tasks: Fix Payment Status Synchronization Between Liquidaciones and Incidentes

**Input**: Design documents from `/specs/033-fix-payment-sync-incidentes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in feature specification. Tests are OPTIONAL.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing database schema and service layer integrity

- [x] T001 Verify database schema for CUOTA_INCIDENTE, PLAN_PAGO_INCIDENTE, INCIDENTE_LIQUIDACION tables exist and have correct relationships
- [x] T002 [P] Verify ServicioFinanciero and ServicioEstadoPagoAutomatico services are importable and functional

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Analyze transaction boundaries in ServicioFinanciero.marcar_liquidacion_pagada() to understand commit timing
- [x] T004 [P] Analyze ServicioEstadoPagoAutomatico.recalcular_estado_pago_incidente() SQL query to verify it reads correct data
- [x] T005 [P] Verify RepositorioCuotaPostgres.obtener_por_liquidacion() returns correct cuota list

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Payment Status Sync After Liquidación Payment (Priority: P1) 🎯 MVP

**Goal**: When a Liquidación is marked as "Pagada", the associated Incidente's payment plan cuotas and payment status badge are updated correctly

**Independent Test**: Mark a liquidación as paid and verify the incident's cuota status changes from "Pendiente" to "Pagada" and the incident's estado_pago updates correctly

### Implementation for User Story 1

- [x] T006 [US1] Modify ServicioFinanciero.marcar_liquidacion_pagada() in src/aplicacion/servicios/servicio_financiero.py to call ServicioEstadoPagoAutomatico after cuota updates
- [x] T007 [US1] Add proper error handling in LiquidacionesState.marcar_como_pagada() in src/presentacion_reflex/state/liquidaciones_state.py to log sync errors with details instead of silently swallowing
- [x] T008 [US1] Verify the fix works for single payment by testing with Incidente #53 and Liquidación #573

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Payment Status Display Consistency (Priority: P1)

**Goal**: The incident card immediately shows the correct payment status after a liquidación is marked as paid, without manual page reload

**Independent Test**: Mark a liquidación as paid and verify the incident card badge updates in real-time without page refresh

### Implementation for User Story 2

- [x] T009 [US2] Verify LiquidacionesState.load_liquidaciones() is called after payment to refresh UI data
- [x] T010 [US2] Verify incidentes_base.py state reloads payment plan data after liquidación changes
- [x] T011 [US2] Test UI update by marking liquidación as paid and observing incident card badge change

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Bulk Payment Status Sync (Priority: P2)

**Goal**: When bulk payments are made, all affected incident payment statuses are updated correctly

**Independent Test**: Select multiple liquidaciones for a property owner, mark them as paid in bulk, and verify all associated incidents update their payment status

### Implementation for User Story 3

- [x] T012 [US3] Modify LiquidacionesState.marcar_como_pagada_masiva() in src/presentacion_reflex/state/liquidaciones_state.py to call ServicioEstadoPagoAutomatico for each liquidación after bulk payment
- [x] T013 [US3] Add error handling for bulk payment sync to log any failures without breaking the bulk operation
- [x] T014 [US3] Test bulk payment by selecting multiple liquidaciones and verifying all incidents update

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Payment Reversal Status Sync (Priority: P2)

**Goal**: When a liquidación payment is reversed, the associated incident's payment status is recalculated correctly

**Independent Test**: Reverse a liquidación payment and verify the incident's payment status updates to reflect the reversal

### Implementation for User Story 4

- [x] T015 [US4] Modify LiquidacionesState.confirmar_reversar() in src/presentacion_reflex/state/liquidaciones_state.py to call ServicioEstadoPagoAutomatico.revertir_estado_pago_por_liquidacion() after reversal
- [x] T016 [US4] Add error handling for reversal sync to log any failures
- [x] T017 [US4] Test reversal by reversing a payment and verifying incident status updates correctly

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T018 [P] Add logging to ServicioEstadoPagoAutomatico.actualizar_estado_pago_por_liquidacion() to track sync operations
- [x] T019 [P] Add logging to ServicioEstadoPagoAutomatico.revertir_estado_pago_por_liquidacion() to track reversal sync
- [x] T020 Run quickstart.md validation scenarios to verify all fixes work end-to-end
- [x] T021 Verify no regressions in existing payment functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tasks for User Story 1 together:
Task: "Modify ServicioFinanciero.marcar_liquidacion_pagada() in src/aplicacion/servicios/servicio_financiero.py"
Task: "Add error handling in LiquidacionesState.marcar_como_pagada() in src/presentacion_reflex/state/liquidaciones_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 2 (P1 priority)
   - Developer B: User Story 3 + 4 (P2 priority)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
