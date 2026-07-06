# Tasks: Estandarización de Filtros Avanzados con Floating Labels

**Input**: Design documents from `/specs/017-advanced-filters-floating-labels/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/component-api.md

**Tests**: No explicit test tasks requested. Validation via quickstart.md scenarios.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Pages**: `src/presentacion_reflex/pages/`
- **Components**: `src/presentacion_reflex/components/`
- **Styles**: `src/presentacion_reflex/styles.py`

---

## Phase 1: Setup (Verify Existing Components)

**Purpose**: Confirm floating label components are functional and ready for migration

- [x] T001 Verify `neuro_floating_input` renders correctly in `src/presentacion_reflex/components/neuro_elements.py`
- [x] T002 Verify `neuro_floating_select` renders correctly in `src/presentacion_reflex/components/neuro_elements.py`
- [x] T003 Verify `floating_input` label animation works in `src/presentacion_reflex/components/shared/floating_label.py`
- [x] T004 Verify `floating_select` label animation works in `src/presentacion_reflex/components/shared/floating_label.py`

**Checkpoint**: Components verified — migration can begin

---

## Phase 2: Foundational (No Blocking Prerequisites)

**Purpose**: No foundational tasks needed. Existing components (`neuro_floating_input`, `neuro_floating_select`) are already implemented and tested. All migration tasks can proceed immediately.

**Checkpoint**: N/A — proceed directly to user stories

---

## Phase 3: User Story 1 — Filtros con Etiquetas Visibles en Módulos Principales (Priority: P1) 🎯 MVP

**Goal**: Migrate 6 main modules from `neuro_input`/`neuro_select_root` to `neuro_floating_input`/`neuro_floating_select`

**Independent Test**: Navigate to any main module, verify each filter field shows a visible label that animates on focus and remains visible with values

### Implementation for User Story 1

- [x] T005 [P] [US1] Migrate Personas filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/personas.py` (fields: Buscar, Rol, Fecha Desde, Fecha Hasta)
- [x] T006 [P] [US1] Migrate Propiedades filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/propiedades.py` (fields: Buscar, Tipo, Disponibilidad)
- [x] T007 [P] [US1] Migrate Contratos filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/contratos.py` (fields: Buscar, Asesor, Tipo, Estado)
- [x] T008 [P] [US1] Migrate Liquidaciones filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/liquidaciones.py` (fields: Buscar, Período, Estado, Ciclo, Asesor)
- [x] T009 [P] [US1] Migrate Liquidación de Asesores filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/liquidacion_asesores.py` (fields: Buscar, Período)
- [x] T010 [P] [US1] Migrate Recaudos filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/recaudos.py` (fields: Buscar, Pago Contrato, Estado, Fecha Desde, Fecha Hasta)

**Checkpoint**: 6 main modules show floating labels — US1 complete

---

## Phase 4: User Story 2 — Homologación de Módulos Secundarios (Priority: P2)

**Goal**: Migrate 7 secondary modules, including 3 that use raw `rx.input`/`rx.select` needing import additions

**Independent Test**: Navigate to each secondary module, verify filter fields show floating labels with neumorphic styling consistent with main modules

### Implementation for User Story 2

- [x] T011 [P] [US2] Migrate Desocupaciones filter: replace raw `rx.select` with `neuro_floating_select` in `src/presentacion_reflex/pages/desocupaciones.py` (field: Estado). Add import for `neuro_floating_select` from `neuro_elements`.
- [x] T012 [P] [US2] Migrate Incidentes filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/incidentes.py` (fields: Buscar, Prioridad, Estado)
- [x] T013 [P] [US2] Migrate Seguros filters: replace raw `rx.input`/`rx.select` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/seguros.py` (fields: Buscar, Estado). Add imports for `neuro_floating_input`, `neuro_floating_select` from `neuro_elements`.
- [x] T014 [P] [US2] Migrate Recibos Públicos filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/recibos.py` (fields: Buscar, Servicio, Estado)
- [x] T015 [P] [US2] Migrate Saldos a Favor filters: replace raw `rx.select` with `neuro_floating_select` in `src/presentacion_reflex/pages/saldos_favor.py` (fields: Tipo, Estado). Add import for `neuro_floating_select` from `neuro_elements`.
- [x] T016 [P] [US2] Migrate Usuarios filters: replace `neuro_input`/`neuro_select_root` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/usuarios.py` (fields: Buscar, Rol, Estado)
- [x] T017 [US2] Migrate Reportes filters: replace raw `rx.input`/`rx.select` with `neuro_floating_input`/`neuro_floating_select` in `src/presentacion_reflex/pages/reportes.py` (fields: sidebar search + dynamic filters per report). Add imports for `neuro_floating_input`, `neuro_floating_select` from `neuro_elements`.

**Checkpoint**: 7 secondary modules show floating labels — US2 complete

---

## Phase 5: User Story 3 — Accesibilidad y Navegación por Teclado (Priority: P3)

**Goal**: Verify accessibility across all migrated modules

**Independent Test**: Navigate with Tab/Shift+Tab through all filter fields. Verify screen readers announce labels. Verify keyboard-only operation.

### Implementation for User Story 3

- [x] T018 [US3] Verify keyboard navigation (Tab, Shift+Tab, Enter, arrows) works across all 13 migrated modules
- [x] T019 [US3] Verify screen reader labels announce correctly by inspecting `<label html_for>` bindings in all migrated modules
- [x] T020 [US3] Verify focus indicators are visible on all filter fields across all modules

**Checkpoint**: Accessibility verified — US3 complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T021 Run quickstart.md validation scenarios across all 13 modules
- [x] T022 Verify responsive behavior at desktop (1440px), tablet (768px), and mobile (375px) viewports
- [x] T023 Verify no filter functionality regression by testing search, select, and date filters in at least 3 modules
- [x] T024 Verify error state labels maintain visibility with correct color (`var(--red-9)`)
- [x] T025 Verify date inputs (`type="date"`) show floating labels correctly in Personas and Recaudos modules

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: No blocking tasks — skip to user stories
- **US1 (Phase 3)**: Can start immediately after Phase 1
- **US2 (Phase 4)**: Can start immediately after Phase 1 (independent of US1)
- **US3 (Phase 5)**: Depends on US1 + US2 completion (needs all modules migrated)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Independent — no dependencies on other stories
- **US2 (P2)**: Independent — no dependencies on US1 (different modules)
- **US3 (P3)**: Depends on US1 + US2 (verifies all migrated modules)

### Within Each User Story

- All module migration tasks within a story are independent (different files)
- Can be executed in parallel by different team members

### Parallel Opportunities

- All Phase 1 tasks [P] can run in parallel
- All US1 tasks (T005-T010) are [P] and can run in parallel
- All US2 tasks (T011-T017) are [P] and can run in parallel
- US1 and US2 can run in parallel (different module files)
- US3 tasks (T018-T20) can run in parallel after US1+US2 complete

---

## Parallel Example: User Story 1

```bash
# Launch all 6 module migrations together (different files):
Task: "Migrate Personas filters in pages/personas.py"
Task: "Migrate Propiedades filters in pages/propiedades.py"
Task: "Migrate Contratos filters in pages/contratos.py"
Task: "Migrate Liquidaciones filters in pages/liquidaciones.py"
Task: "Migrate Liq. Asesores filters in pages/liquidacion_asesores.py"
Task: "Migrate Recaudos filters in pages/recaudos.py"
```

## Parallel Example: User Story 2

```bash
# Launch all 7 module migrations together (different files):
Task: "Migrate Desocupaciones filter in pages/desocupaciones.py"
Task: "Migrate Incidentes filters in pages/incidentes.py"
Task: "Migrate Seguros filters in pages/seguros.py"
Task: "Migrate Recibos filters in pages/recibos.py"
Task: "Migrate Saldos a Favor filters in pages/saldos_favor.py"
Task: "Migrate Usuarios filters in pages/usuarios.py"
Task: "Migrate Reportes filters in pages/reportes.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Verify components (T001-T004)
2. Complete Phase 3: Migrate 6 main modules (T005-T010)
3. **STOP and VALIDATE**: Test Personas, Propiedades, Contratos independently
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup → Components verified
2. Add US1 (6 main modules) → Test independently → Deploy/Demo (MVP!)
3. Add US2 (7 secondary modules) → Test independently → Deploy/Demo
4. Add US3 (accessibility verification) → Full system validated
5. Polish → Final validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Phase 1 together (component verification)
2. Once verified:
   - Developer A: US1 — Personas, Propiedades, Contratos
   - Developer B: US1 — Liquidaciones, Liq. Asesores, Recaudos
   - Developer C: US2 — Desocupaciones, Incidentes, Seguros, Recibos
   - Developer D: US2 — Saldos a Favor, Usuarios, Reportes
3. All complete → US3 verification → Polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No state changes needed — floating label is CSS-only
- Migration pattern: `neuro_input(placeholder=X)` → `neuro_floating_input(label=X)`
- Migration pattern: `neuro_select_root(placeholder=X)` → `neuro_floating_select(label=X)`
- Raw modules need import additions for `neuro_elements`
- Switches/checkboxes remain unchanged (already have visible labels)

---

## Phase 7: Convergence

**Purpose**: Remove dead imports left over from migration

- [x] T026 Remove unused `neuro_input` and `neuro_select_root` imports from 9 migrated page files: `personas.py`, `propiedades.py`, `contratos.py`, `liquidaciones.py`, `liquidacion_asesores.py`, `incidentes.py`, `recibos.py`, `usuarios.py` (both dead), `recaudos.py` (`neuro_select_root` dead only) (unrequested)
