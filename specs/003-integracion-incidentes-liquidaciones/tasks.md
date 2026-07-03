# Tasks: Integración Incidentes y Liquidaciones de Propietarios

---

## Phase 1: Setup

- [X] T001 Create database migration script for INCIDENTES table (add estado_pago column) in `scripts/migration_001.sql`
- [X] T002 Create database migration script for LIQUIDACIONES table (add valor_incidentes column) in `scripts/migration_002.sql`
- [X] T003 Create PLAN_PAGO_INCIDENTE table migration in `scripts/migration_003.sql`
- [X] T004 Create CUOTA_INCIDENTE table migration in `scripts/migration_004.sql`
- [X] T005 Create INCIDENTE_LIQUIDACION table migration in `scripts/migration_005.sql`
- [X] T006 Create database indexes for performance in `scripts/migration_006.sql`
- [X] T007 Run all migrations on development database

---

## Phase 2: Foundational

- [X] T008 Create PlanPagoIncidente entity class in `src/dominio/entidades/plan_pago_incidente.py`
- [X] T009 Create CuotaIncidente entity class in `src/dominio/entidades/cuota_incidente.py`
- [X] T010 Create IncidenteLiquidacion entity class in `src/dominio/entidades/incidente_liquidacion.py`
- [X] T011 Update Incidente entity with estado_pago field in `src/dominio/entidades/incidente.py`
- [X] T012 Update Liquidacion entity with valor_incidentes field in `src/dominio/entidades/liquidacion.py`
- [X] T013 Create RepositorioPlanPago interface in `src/dominio/interfaces/repositorio_plan_pago.py`
- [X] T014 Create RepositorioCuota interface in `src/dominio/interfaces/repositorio_cuota.py`
- [X] T015 Create RepositorioIncidenteLiquidacion interface in `src/dominio/interfaces/repositorio_incidente_liq.py`
- [X] T016 Create RepositorioPlanPagoPostgres implementation in `src/infraestructura/persistencia/repositorio_plan_pago_postgres.py`
- [X] T017 Create RepositorioCuotaPostgres implementation in `src/infraestructura/persistencia/repositorio_cuota_postgres.py`
- [X] T018 Create RepositorioIncidenteLiquidacionPostgres implementation in `src/infraestructura/persistencia/repositorio_incidente_liq_postgres.py`
- [X] T019 Register new permission actions (DEFINIR_PLAN_PAGO, SELECCIONAR_INCIDENTES) in database
- [X] T020 Add pessimistic locking mechanism for incident editing in `src/infraestructura/persistencia/repositorio_bloqueos.py`

---

## Phase 3: US1 - Definir Plan de Pago del Incidente

**Goal**: Allow Administrators and Advisors to define payment plans for approved incidents.

**Independent Test**: Open incident modal for approved incident with approved quotation, select payment modality, verify plan is created correctly.

- [X] T021 [US1] Create ServicioPlanPagoIncidente in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T022 [US1] Implement crear_plan method with validation rules in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T023 [US1] Implement obtener_plan_por_incidente method in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T024 [US1] Implement modificar_plan method (only if no associations) in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T025 [US1] Implement cancelar_plan method in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T026 [US1] Add audit logging for payment plan operations in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T027 [US1] Update IncidentesState with payment plan state variables in `src/presentacion_reflex/state/incidentes_state.py`
- [X] T028 [US1] Add open_modal_plan_pago event handler in `src/presentacion_reflex/state/incidentes_state.py`
- [X] T029 [US1] Add close_modal_plan_pago event handler in `src/presentacion_reflex/state/incidentes_state.py`
- [X] T030 [US1] Add crear_plan_pago event handler in `src/presentacion_reflex/state/incidentes_state.py`
- [X] T031 [US1] Create modal_plan_pago component in `src/presentacion_reflex/components/incidentes/modal_plan_pago.py`
- [X] T032 [US1] Add payment modality selection UI (1, 2, 3+ cannons) in `src/presentacion_reflex/components/incidentes/modal_plan_pago.py`
- [X] T033 [US1] Add payment plan summary display before confirmation in `src/presentacion_reflex/components/incidentes/modal_plan_pago.py`
- [X] T034 [US1] Add permission check for DEFINIR_PLAN_PAGO action in `src/presentacion_reflex/components/incidentes/modal_plan_pago.py`
- [X] T035 [US1] Add "En edición por [usuario]" indicator for concurrent edit prevention in `src/presentacion_reflex/components/incidentes/modal_plan_pago.py`

---

## Phase 4: US2 - Asociar Incidentes a Liquidación

**Goal**: Allow Administrators to associate incident installments to liquidations.

**Independent Test**: Open liquidation modal, click "Seleccionar Incidentes", select incidents, verify discounts are applied correctly.

- [X] T036 [US2] Create ServicioIncidenteLiquidacion in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [X] T037 [US2] Implement asociar_incidente method with validation in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [X] T038 [US2] Implement desasociar_incidente method in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [X] T039 [US2] Implement obtener_incidentes_por_liquidacion method in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [X] T040 [US2] Implement obtener_liquidaciones_por_incidente method in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [X] T041 [US2] Add audit logging for association operations in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [X] T042 [US2] Update LiquidacionesState with association state variables in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T043 [US2] Add open_modal_seleccion_incidentes event handler in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T044 [US2] Add close_modal_seleccion_incidentes event handler in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T045 [US2] Add asociar_incidentes event handler in `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T046 [US2] Create modal_seleccion_incidentes component in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`
- [X] T047 [US2] Add incident selection checkboxes UI in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`
- [X] T048 [US2] Add discount sum calculation display in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`
- [X] T049 [US2] Filter incidents by payment status (exclude Pagado) in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`
- [X] T050 [US2] Add permission check for SELECCIONAR_INCIDENTES action in `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`
- [X] T051 [US2] Add duplicate association prevention in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`

---

## Phase 5: US3 - Visualización del Estado de Pago

**Goal**: Display payment status alongside operational status for all users.

**Independent Test**: View incident list with approved/in repair/finished incidents, verify payment status is displayed correctly.

- [X] T052 [US3] Add calcular_estado_pago method in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T053 [US3] Implement Pendiente status calculation logic in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T054 [US3] Implement Parcialmente Pagado status calculation logic in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T055 [US3] Implement Pagado status calculation logic in `src/aplicacion/servicios/servicio_plan_pago.py`
- [X] T056 [US3] Update IncidentesState with payment status display variables in `src/presentacion_reflex/state/incidentes_state.py`
- [X] T057 [US3] Add payment status badge to incident list view in `src/presentacion_reflex/components/incidentes/incidente_card.py`
- [X] T058 [US3] Add payment status display to incident detail modal in `src/presentacion_reflex/components/incidentes/modal_edit_incidente.py`
- [X] T059 [US3] Add conditional display logic (only for Aprobado, En Reparacion, Finalizado) in `src/presentacion_reflex/components/incidentes/incidente_card.py`
- [X] T060 [US3] Add payment status color coding (Pendiente=gray, Parcial=yellow, Pagado=green) in `src/presentacion_reflex/components/incidentes/incidente_card.py`

---

## Phase 6: US4 - Actualización Automática del Estado de Pago

**Goal**: Automatically update incident payment status when liquidation status changes to "Pagada".

**Independent Test**: Mark a liquidation as paid with associated incidents, verify payment status updates correctly.

- [X] T061 [US4] Create ServicioEstadoPagoAutomatico in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T062 [US4] Implement actualizar_estado_pago_por_liquidacion method in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T063 [US4] Implement recalcular_estado_pago_incidente method in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T064 [US4] Add hook to liquidation payment event in `src/aplicacion/servicios/servicio_liquidaciones.py`
- [X] T065 [US4] Add automatic status recalculation for all associated incidents in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T066 [US4] Update LIQUIDACIONES trigger to call status recalculation in `scripts/migration_007.sql`
- [X] T067 [US4] Add transaction safety for status updates in `src/aplicacion/servicios/servicio_estado_pago.py`

---

## Phase 7: US5 - Reversión de Pago con Impacto en Incidentes

**Goal**: Recalculate incident payment status when liquidation payment is reversed.

**Independent Test**: Reverse payment for liquidation with associated incidents, verify payment status recalculates correctly.

- [X] T068 [US5] Implement revertir_pago_con_impacto method in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T069 [US5] Add hook to liquidation payment reversal event in `src/aplicacion/servicios/servicio_liquidaciones.py`
- [X] T070 [US5] Add automatic status recalculation for all affected incidents in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T071 [US5] Add audit logging for payment reversal operations in `src/aplicacion/servicios/servicio_estado_pago.py`
- [X] T072 [US5] Add rollback support for failed reversal operations in `src/aplicacion/servicios/servicio_estado_pago.py`

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T073 Add comprehensive error handling for all service methods in `src/aplicacion/servicios/`
- [ ] T074 Add IP address capture in audit trail in `src/aplicacion/servicios/servicio_auditoria.py`
- [ ] T075 Add session ID capture in audit trail in `src/aplicacion/servicios/servicio_auditoria.py`
- [ ] T076 Add mandatory justification validation for association operations in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [ ] T077 Add mandatory justification validation for payment plan modifications in `src/aplicacion/servicios/servicio_plan_pago.py`
- [ ] T078 Add idempotency checks for all association operations in `src/aplicacion/servicios/servicio_incidente_liquidacion.py`
- [ ] T079 Add transaction atomicity for all multi-step operations in `src/aplicacion/servicios/`
- [ ] T080 Add performance optimization for status calculation queries in `src/infraestructura/persistencia/`
- [ ] T081 Add cleanup for expired pessimistic locks in `src/infraestructura/persistencia/repositorio_bloqueos.py`
- [X] T082 Update incident list API to include payment status in `src/infraestructura/persistencia/repositorio_incidentes_postgres.py`
- [X] T083 Update liquidation API to include incident discounts in `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

---

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 5 (US3)
                                   ↓                           ↓
                              Phase 4 (US2) → Phase 6 (US4)
                                   ↓
                              Phase 7 (US5)
                                   ↓
                              Phase 8 (Polish)
```

**Independent Stories**:

- US1 (Payment Plan) can be developed in parallel with US2 (Association)
- US3 (Status Display) depends on US1
- US4 (Auto Status Update) depends on US2
- US5 (Payment Reversal) depends on US4

---

## Parallel Execution Examples

### US1 Parallel Tasks:

- T021-T026 (Service layer) can run in parallel with T027-T030 (State handlers)
- T031-T035 (UI components) can run in parallel after T027-T030

### US2 Parallel Tasks:

- T036-T041 (Service layer) can run in parallel with T042-T045 (State handlers)
- T046-T051 (UI components) can run in parallel after T042-T045

### Cross-Story Parallel:

- US1 and US2 can be developed simultaneously
- US3 can start after US1 completes
- US4 can start after US2 completes

---

## Implementation Strategy

**MVP Scope**: US1 (Definir Plan de Pago) + US3 (Visualización del Estado de Pago)

**Delivery Order**:

1. Phase 1-2: Database and domain layer foundation
2. Phase 3+5: MVP with payment plan definition and status display
3. Phase 4+6: Association functionality with automatic status updates
4. Phase 7: Payment reversal integration
5. Phase 8: Polish and cross-cutting concerns

---

## Validation Checklist

- [X] All tasks follow checklist format (checkbox, ID, labels, file paths)
- [X] Each user story has independent test criteria
- [X] Tasks organized by user story priority
- [X] Dependencies clearly defined
- [X] Parallel execution opportunities identified
- [X] MVP scope defined (US1 + US3)
- [X] File paths specified for all tasks
