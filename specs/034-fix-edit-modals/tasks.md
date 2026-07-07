---
description: "Task list template for feature implementation"
---

# Tasks: fix-edit-modals

**Input**: Design documents from `/specs/034-fix-edit-modals/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual browser validation as described in `quickstart.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `src/presentacion_reflex/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*(No setup tasks required for this UI fix)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*(No foundational tasks required. Both modals can be fixed in parallel)*

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Editar un registro de Liquidación existente (Priority: P1) 🎯 MVP

**Goal**: Permitir la modificación de los campos variables en el modal de liquidaciones agregando manejadores de estado.

**Independent Test**: Verificar que al escribir en los campos numéricos de egresos/ingresos, el valor cambia visualmente y persiste al guardar.

### Implementation for User Story 1

- [X] T001 [P] [US1] Update `form_field_editable` function in `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` to include `on_change=lambda v: LiquidacionesState.set_form_field(name, v)` on the `neuro_floating_input` component.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Liquidaciones edits should work.

---

## Phase 4: User Story 2 - Editar un registro de Recaudo existente (Priority: P1)

**Goal**: Habilitar la edición de campos bloqueados (fecha de pago, referencia, período) en el modal de recaudos.

**Independent Test**: Verificar que los campos Fecha de Pago, Referencia Bancaria y Período permiten ser editados y guardan sus valores actualizados.

### Implementation for User Story 2

- [X] T002 [P] [US2] Update `fecha_pago` input in `src/presentacion_reflex/components/recaudos/modal_form.py` to include `on_change=lambda v: RecaudosState.set_form_field("fecha_pago", v)`.
- [X] T003 [P] [US2] Update `referencia_bancaria` input in `src/presentacion_reflex/components/recaudos/modal_form.py` to include `on_change=lambda v: RecaudosState.set_form_field("referencia_bancaria", v)`.
- [X] T004 [P] [US2] Update `periodo` input in `src/presentacion_reflex/components/recaudos/modal_form.py` to include `on_change=lambda v: RecaudosState.set_form_field("periodo", v)`.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Recaudos edits should work.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T005 Run quickstart.md validation to guarantee end-to-end functionality in the browser.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories.
- **User Story 2 (P1)**: No dependencies on other stories.

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- US1 and US2 touch entirely independent files (`liquidacion_edit_form.py` vs `modal_form.py`) and can be implemented 100% in parallel.
- Tasks T002, T003, and T004 touch different parts of the same file and can be implemented simultaneously.

---

## Parallel Example: User Story 1 and 2

```bash
# Launch implementation for US1 and US2 together:
Task: "Update form_field_editable function in src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py..."
Task: "Update inputs in src/presentacion_reflex/components/recaudos/modal_form.py..."
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1
2. **STOP and VALIDATE**: Test User Story 1 independently in the browser.

### Incremental Delivery

1. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
2. Add User Story 2 → Test independently → Deploy/Demo

### Parallel Team Strategy

With multiple developers:
1. Developer A: User Story 1 (Liquidaciones)
2. Developer B: User Story 2 (Recaudos)
3. Stories complete and integrate independently
