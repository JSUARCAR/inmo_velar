# Tasks: standardize-advanced-filters

**Feature**: standardize-advanced-filters
**Branch**: `[035-standardize-advanced-filters]`
**Date**: 2026-07-07
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## Summary

- **Total tasks**: 14
- **User Stories**: 4 (US1-P1, US2-P1, US3-P2, US4-P2)
- **Parallel opportunities**: 7 (module migrations can run in parallel)
- **Estimated phases**: 5

## Implementation Strategy

**MVP Scope**: User Story 1 + User Story 2 (shared component + first 2 module migrations)

**Rationale**: The `AdvancedFilterBar` component is the foundation for all user stories. Once created and migrated to 2 modules, visual consistency is achieved. Remaining modules can be migrated incrementally.

**Delivery Order**:
1. Setup tokens → 2. Create component → 3. Migrate modules (parallel) → 4. Polish

---

## Phase 1: Setup

> Add filter-specific design tokens to the centralized style system.

- [x] T001 Add `NEU_FILTER_BAR_STYLE` token to `src/presentacion_reflex/styles.py` with white background (#FFFFFF), light gray border (#E5E7EB), no shadow, border-radius 16px, padding 24px
- [x] T002 Add `NEU_FILTER_INPUT_STYLE` token to `src/presentacion_reflex/styles.py` based on `NEU_INPUT_STYLE` with height 40px and border-radius 8px
- [x] T003 Add `NEU_FILTER_SELECT_STYLE` token to `src/presentacion_reflex/styles.py` based on `NEU_SELECT_STYLE` with height 40px and border-radius 8px
- [x] T004 Add `NEU_FILTER_ICON_BUTTON_STYLE` token to `src/presentacion_reflex/styles.py` based on `NEU_ICON_BUTTON_STYLE` with height 40px
- [x] T005 Add `NEU_FILTER_LABEL_STYLE` token to `src/presentacion_reflex/styles.py` for consistent filter label typography (font-size, font-weight, color, spacing)

**Gate**: All tokens must be defined and importable before proceeding to Phase 2.

---

## Phase 2: Foundational — AdvancedFilterBar Component

> Create the reusable filter bar component that encapsulates standardized layout, spacing, dimensions, and behavior.

- [x] T006 Create `AdvancedFilterBar` component in `src/presentacion_reflex/components/shared/advanced_filter_bar.py` with: container using `NEU_FILTER_BAR_STYLE`, flex layout with `rx.breakpoints(initial="column", md="row")`, `wrap="wrap"`, `gap="4"` horizontal / `gap="3"` vertical, search input slot, children slot for filters, action buttons slot (right-aligned), "Limpiar" button with active filter count badge
- [x] T007 Implement `advanced_filter_bar()` function signature with props: `*children`, `search_placeholder`, `on_search`, `search_value`, `on_clear`, `action_buttons`, `**props` per contracts/component-api.md
- [x] T008 Implement active filter count badge logic: count non-default filter children, display numeric badge on "Limpiar" button, hide badge when count is 0

**Gate**: Component must render correctly with sample filters before migrating modules.

---

## Phase 3: User Story 1 — Navegación consistente entre módulos (P1)

> Migrate all 7 modules to use the new `AdvancedFilterBar` component, ensuring visual consistency.

### Independent Test
Navigate sequentially through all 7 modules and verify the filter section displays identical dimensions, spacing, alignment, and behavior.

### Module Migrations (Parallel)

- [x] T009 [P] [US1] Migrate `src/presentacion_reflex/pages/personas.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Rol Select, Fecha Desde/Hasta DatePickers, Inactivos/Sin contrato Toggles as children, add icon-only action buttons (view toggle, export, refresh)
- [x] T010 [P] [US1] Migrate `src/presentacion_reflex/pages/propiedades.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Tipo Select, Disponibilidad Select as children, add icon-only action buttons (view toggle, export)
- [x] T011 [P] [US1] Migrate `src/presentacion_reflex/pages/contratos.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Asesor Select, Tipo Select, Estado Select, Sin arriendo Checkbox as children, add icon-only action buttons (view toggle, export)
- [x] T012 [P] [US1] Migrate `src/presentacion_reflex/pages/liquidaciones.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Periodo Select, Estado Select, Ciclo Select, Asesor Select, Vista Agrupada Toggle as children, add icon-only action buttons (export ZIP, new, bulk, refresh)
- [x] T013 [P] [US1] Migrate `src/presentacion_reflex/pages/liquidacion_asesores.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Periodo Select as children, add icon-only action buttons (bulk generate, new, refresh)
- [x] T014 [P] [US1] Migrate `src/presentacion_reflex/pages/recaudos.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Estado Select, Fecha Desde/Hasta DatePickers as children, add icon-only action buttons (register payment, bulk generate, refresh, export)
- [x] **T015**: Migrate `src/presentacion_reflex/pages/incidentes.py` filter section to use `AdvancedFilterBar`: replace inline filter layout with component, pass search input, Prioridad Select, Estado Select, Estado de Pago Select as children, replace `rx.segmented_control` view toggle with icon-only buttons, add icon-only action buttons (report)

**Gate**: All 7 modules must render with identical filter bar styling. Visual inspection confirms no differences.

---

## Phase 4: User Stories 2-4 — Componentes, Espaciado, Responsive (P1/P2)

> These stories are automatically satisfied by the `AdvancedFilterBar` component created in Phase 2 and migrated in Phase 3. Verification tasks confirm compliance.

### Independent Test
- US2: Inspect component dimensions (40px height, 8px border-radius) across all 7 modules
- US3: Measure spacing (16px horizontal, 12px vertical, 24px padding) across all 7 modules
- US4: Resize browser to 768px, 1024px, 1440px, 1920px and verify no overflow/overlap

### Phase 4: Validation
- [x] T016 [T] [US1, US2] Run UI regression: Verify filters collapse correctly into `drawer` on screens `< md`
- [x] T017 [T] [US2] Verify layout dimensions: Check `AdvancedFilterBar` takes full width, and `gap="4"` is applied.
- [x] T018 [T] [US1] State flow validation: Confirm `active_filter_count` accurately reflects the number of applied filters and that `clear_filters` resets *all* filter state variables in every migrated module.
**Gate**: All visual elements are identical and functioning properly. "Apply" button

---

## Phase 5: Polish & Cross-Cutting Concerns

> Final validation and cleanup.

- [x] T019 Verify all action buttons are icon-only with tooltip on hover across all 7 modules
- [x] T020 Verify "Limpiar" button badge shows correct active filter count and disappears when zero
- [x] T021 Verify filter auto-apply behavior: changing any filter value immediately updates the data grid without manual "Apply" button
- [x] T022 Verify zero regressions: test all filter types (search, select, datepicker, toggle, checkbox) in all 7 modules — data filtering must work identically to pre-migration behavior
- [x] T023 Verify placeholder text consistency across all input fields in all 7 modules
- [x] T024 Verify label positioning: search=placeholder only, Select/DatePicker=label above, Toggle/Checkbox=label right — across all 7 modules

---

## Dependencies

```text
Phase 1 (Setup) ──────► Phase 2 (Component) ──────► Phase 3 (Module Migrations) ──────► Phase 4 (Verification) ──────► Phase 5 (Polish)
                                    │
                                    └──► T009-T015 can run in PARALLEL (different files)
```

## Parallel Execution Examples

### Example 1: Module Migrations (Phase 3)

All 7 module migrations (T009-T015) can execute in parallel since they modify different files with no shared state:

```text
Agent 1: T009  personas.py
Agent 2: T010  propiedades.py
Agent 3: T011  contratos.py
Agent 4: T012  liquidaciones.py
Agent 5: T013  liquidacion_asesores.py
Agent 6: T014  recaudos.py
Agent 7: T015  incidentes.py
```

### Example 2: Verification Tasks (Phase 4)

T016, T017, T018 can run in parallel since they test different aspects:

```text
Agent 1: T016  Component dimensions verification
Agent 2: T017  Spacing verification
Agent 3: T018  Responsive behavior verification
```

## File Summary

| File | Action | Tasks |
|------|--------|-------|
| `src/presentacion_reflex/styles.py` | MODIFY | T001-T005 |
| `src/presentacion_reflex/components/shared/advanced_filter_bar.py` | CREATE | T006-T008 |
| `src/presentacion_reflex/pages/personas.py` | MODIFY | T009 |
| `src/presentacion_reflex/pages/propiedades.py` | MODIFY | T010 |
| `src/presentacion_reflex/pages/contratos.py` | MODIFY | T011 |
| `src/presentacion_reflex/pages/liquidaciones.py` | MODIFY | T012 |
| `src/presentacion_reflex/pages/liquidacion_asesores.py` | MODIFY | T013 |
| `src/presentacion_reflex/pages/recaudos.py` | MODIFY | T014 |
| `src/presentacion_reflex/pages/incidentes.py` | MODIFY | T015 |
