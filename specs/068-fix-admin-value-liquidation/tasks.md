# Implementation Tasks: fix-admin-value-liquidation

**Feature**: fix-admin-value-liquidation
**Branch**: fix-admin-value-liquidation

This document contains the implementation tasks derived from the specification, data model, and research decisions. The tasks are organized by User Story to support independent, incremental delivery.

## Implementation Strategy

1. **MVP Scope**: Complete Phase 3 (US1) to solve the core data inconsistency issue reported by the client (cascading the admin value to the active billing cycle).
2. **Follow-up**: Phase 4 (US2) ensures the UI modal correctly respects intentional `0` values.
3. **Completion**: Phase 5 verifies all edge cases, especially the temporal boundary logic.

---

## Phase 1: Setup

*(No project initialization or infrastructure setup is required for this feature as it modifies existing modules).*

---

## Phase 2: Foundational

**Goal**: Verify dependencies and structure required for the feature.

- [X] T001 Inspect `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` and `src/dominio/value_objects/estado_cumplimiento.py` to confirm how `obtener_periodo_actual()` is imported and used, preparing it for injection into the cascade query.
- [X] T002 Inspect `src/aplicacion/servicios/servicio_propiedades.py` to map the exact location of `actualizar_propiedad` and the transaction context (`with db_manager.obtener_conexion() as conn:`).

---

## Phase 3: User Story 1 - Actualización de Administración Reflejada en Liquidaciones en Proceso

**Goal**: Automatically cascade property administration value changes to the current period's draft liquidations.
**Independent Test**: Scenario 1 and Scenario 4 from `quickstart.md` (Update a property value and verify only the current 'En Proceso' liquidation updates in the DB).

- [X] T003 [US1] In `src/aplicacion/servicios/servicio_propiedades.py`, update `actualizar_propiedad` to inject a raw SQL `UPDATE` statement inside the existing database transaction. The SQL must update `LIQUIDACIONES`, set `GASTOS_ADMINISTRACION`, recalculate `TOTAL_EGRESOS` and `NETO_A_PAGAR` (using formula `NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS`), and update audit fields (`UPDATED_AT`, `UPDATED_BY`). Use strict `%s` placeholders. If the query throws an exception, raise it immediately to ensure a *Strict Rollback* of the entire transaction.
- [X] T004 [US1] In `src/aplicacion/servicios/servicio_propiedades.py`, add the `WHERE` clauses to the SQL: filter by `ID_CONTRATO_M` (linked to the property), `ESTADO_LIQUIDACION = 'En Proceso'`, exclude manual overrides (`GASTOS_ADMINISTRACION = old_valor_admin`), AND filter by `PERIODO = obtener_periodo_actual()`. Return the rowcount of updated liquidations.
- [X] T005 [US1] In `src/presentacion_reflex/state/propiedades_state.py`, modify the save action to capture the rowcount returned by the service and display a UI toast notification (e.g., "Propiedad actualizada. X liquidaciones actualizadas en cascada").

---

## Phase 4: User Story 2 - Precisión en la creación y edición de nuevas Liquidaciones

**Goal**: Ensure the UI modal accurately loads the current value and respects deliberate `0` overrides.
**Independent Test**: Scenario 2 from `quickstart.md`.

- [X] T006 [P] [US2] In `src/presentacion_reflex/state/liquidaciones_state.py`, modify the `open_edit_modal` (or equivalent data load method) to respect `0` as a legitimate manual override. It must not automatically overwrite a deliberate `0` with the property's base value unless the liquidation was originally `0`.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Goal**: Verify resilience and final integration.

- [X] T007 Run the full suite of manual tests in `quickstart.md` locally via `reflex run --env dev` to ensure no stale data errors or transactional deadlocks.
- [X] T008 Run `check_syntax.py` and `mypy` to ensure strict typing is maintained in the modified signatures.

---

## Dependencies

- Phase 2 (Foundational) blocks Phase 3 (US1).
- Phase 3 (US1) and Phase 4 (US2) can technically be executed in parallel (hence `[P]` on T006), but testing them sequentially is recommended.

## Parallel Execution Examples

- Developer A can implement T003/T004/T005 (The Cascade in the properties domain).
- Developer B can implement T006 (The UI Fix in the liquidations domain).
