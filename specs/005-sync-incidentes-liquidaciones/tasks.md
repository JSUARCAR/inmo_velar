---
description: "Task list template for feature implementation"
---

# Tasks: Sincronización Incidentes y Liquidaciones

**Input**: Design documents from `/specs/005-sync-incidentes-liquidaciones/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths are included in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Review `quickstart.md` to setup local environment and prepare test data.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Verify that `RepositorioIncidentesPostgres`, `RepositorioPlanPagoPostgres` y `RepositorioCuotaPostgres` están correctamente enlazados por el `DatabaseManager` en `src/infraestructura/persistencia/`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Visualización del Plan de Pago en Incidentes (Priority: P1) 🎯 MVP

**Goal**: Permitir a los usuarios ver el plan de pago asociado a un incidente aprobado directamente en el módulo de Incidentes.

**Independent Test**: Aprobar una cotización en la UI de incidentes y comprobar que el plan de pago generado se muestra correctamente en los detalles del incidente, persistiendo los datos.

### Implementation for User Story 1

- [ ] T003 [US1] Update `src/infraestructura/persistencia/repositorio_incidentes_postgres.py` to fetch `PlanPagoIncidente` data when querying incidents by ID.
- [ ] T004 [P] [US1] Update `src/aplicacion/servicios/servicio_plan_pago.py` to ensure `crear_plan_con_cuotas` runs atomically when an incident quotation is approved.
- [ ] T005 [P] [US1] Update UI components in `src/presentacion_reflex/` (specifically the incident detail view) to render the `PlanPagoIncidente` state and values if it exists.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Propagación de Cuotas a Liquidación de Propietario (Priority: P1)

**Goal**: Descontar automáticamente las cuotas pendientes de un incidente en la liquidación del propietario y gestionar su transición de estado.

**Independent Test**: Generar una liquidación mensual para una propiedad con un incidente activo y verificar que el descuento se refleja en el campo `valor_incidentes`. Al finalizar la liquidación, la cuota debe pasar a estado "Pagada/Descontada".

### Implementation for User Story 2

- [ ] T006 [P] [US2] Update `src/infraestructura/persistencia/repositorio_cuota_postgres.py` to add a method for fetching all "Pendiente" quotas given a property ID or contract ID.
- [ ] T007 [US2] Update `src/aplicacion/servicios/servicio_financiero.py` (`generar_liquidacion_mensual`) to sum pending quotas and subtract them via the `valor_incidentes` field.
- [ ] T008 [US2] Update `src/aplicacion/servicios/servicio_financiero.py` to update the quotas' state to "Asociada" and set their `id_liquidacion` upon successful liquidation draft creation.
- [ ] T009 [US2] Update `src/aplicacion/servicios/servicio_financiero.py` (liquidation finish flow) to transition associated quotas' states to "Pagada/Descontada" when the liquidation is paid/approved.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T010 [P] Code cleanup and removing any debug print statements across modified files.
- [ ] T011 Run `quickstart.md` validation scripts to ensure no regressions in both modules.

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
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on US1, but realistically depends on data created by US1 to test properly.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- Once Foundational phase completes, all user stories can start in parallel.
- Database query updates (`T003`, `T006`) can be done in parallel by backend devs while frontend devs update the UI (`T005`).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently in Reflex UI.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add User Story 1 → Test UI persistence → Deploy.
3. Add User Story 2 → Test Financial Service discount logic → Deploy.
4. Each story adds value without breaking previous stories.
