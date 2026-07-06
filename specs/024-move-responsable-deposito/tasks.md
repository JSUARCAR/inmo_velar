---
description: "Task list for move-responsable-deposito feature implementation"
---

# Tasks: move-responsable-deposito

**Input**: Design documents from `/specs/024-move-responsable-deposito/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure (Skipped as the project already exists)

- [ ] T001 Verify project runs and PostgreSQL is accessible

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Apply PostgreSQL schema migration to drop `responsable_deposito_id` from `CONTRATOS_MANDATOS` and add it to `CONTRATOS_ARRENDAMIENTOS`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Eliminar Responsable del Depósito de Mandato (Priority: P1) 🎯 MVP

**Goal**: El campo "Responsable del Depósito" ya no debe aparecer en el modal de Contrato de Mandato ni persistirse.

**Independent Test**: Can be fully tested by abriendo el modal de creación y edición de Contrato de Mandato y verificando la ausencia del campo, sin afectar el resto del proceso.

### Implementation for User Story 1

- [ ] T003 [P] [US1] Remove `responsable_deposito_id` from `ContratoMandato` entity in `src/dominio/entidades/contrato_mandato.py`
- [ ] T004 [P] [US1] Remove `responsable_deposito_id` from `repositorio_contrato_mandato_postgres.py` (`INSERT` and `UPDATE` queries)
- [ ] T005 [P] [US1] Update application service to ignore `responsable_deposito_id` in `src/aplicacion/servicios/servicio_contrato_mandato.py`
- [ ] T006 [P] [US1] Remove `responsable_deposito_id` field from UI form in `src/presentacion_reflex/components/contratos/formulario_contrato_mandato.py`
- [ ] T007 [US1] Update `ContratosState` to prevent passing `responsable_deposito_id` to Mandato form handlers in `src/presentacion_reflex/state/contratos_state.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (Mandatos should work fine without the field)

---

## Phase 4: User Story 2 - Implementar Responsable del Depósito en Arrendamiento (Priority: P1)

**Goal**: Poder asignar un "Responsable del Depósito" al crear o editar un Contrato de Arrendamiento seleccionándolo de una lista de asesores.

**Independent Test**: Can be fully tested by creando un Contrato de Arrendamiento, seleccionando un asesor y verificando que el dato persista.

### Implementation for User Story 2

- [x] T008 [P] [US2] Add `responsable_deposito_id` (optional integer) to `ContratoArrendamiento` entity in `src/dominio/entidades/contrato_arrendamiento.py`
- [x] T009 [P] [US2] Add `responsable_deposito_id` to queries (`INSERT`, `UPDATE`) in `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py`
- [x] T010 [P] [US2] Update application service to pass `responsable_deposito_id` in `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- [x] T011 [P] [US2] Add ComboBox field for `responsable_deposito_id` to UI form in `src/presentacion_reflex/components/contratos/formulario_contrato_arrendamiento.py`
- [x] T012 [US2] Update `ContratosState` to populate asesores array in Arrendamiento form and handle inactive asesores logic when editing in `src/presentacion_reflex/state/contratos_state.py`
- [x] T013 [US2] Update read-only details query to fetch Asesor Responsable if the contract is Arrendamiento in `src/aplicacion/servicios/servicio_contratos.py`
- [x] T014 [US2] Update read-only UI modal to show Responsable del Depósito ONLY for Arrendamientos in `src/presentacion_reflex/components/contratos/modal_detalle_contrato.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T015 Run quickstart.md validation to ensure everything works
- [x] T016 Verify Reflex app compiles successfully (`reflex export --frontend-only --no-zip`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2). Integrates with `ContratosState` which might overlap with US1, so it is recommended to do T007 and T012 sequentially or carefully.

### Parallel Opportunities

- All entity and repository changes (T003, T004, T005, T008, T009, T010) can be done in parallel.
- UI form modifications (T006, T011) can be done in parallel.

---

## Implementation Strategy

### Incremental Delivery

1. Complete Setup + Foundational (Database schema changed).
2. Complete User Story 1 (Remove from Mandato) → Test independently.
3. Complete User Story 2 (Add to Arrendamiento) → Test independently.
4. Finalize polish and UI verification.
