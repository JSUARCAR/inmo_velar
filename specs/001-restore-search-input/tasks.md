# Tasks: Restore Search Input in Advanced Filters

**Feature**: Restore Search Input in Advanced Filters
**Generated**: 2026-07-08
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

---

## Phase 1: Setup

No setup tasks required - this is a modification to an existing component.

---

## Phase 2: Foundational

No foundational tasks required - the component and all dependencies already exist.

---

## Phase 3: User Story 1 - Search Input Restoration

**Story Goal**: Restore the search input field in the Advanced Filters section of all 7 affected modules by adding search input rendering to the shared `advanced_filter_bar` component.

**Independent Test Criteria**:
- Search input is visible in all 7 module pages
- Search input accepts text input
- Search input uses consistent styling (`NEU_FILTER_INPUT_STYLE`)
- Search input is positioned as the first filter control
- Mobile drawer displays search input correctly

### Tasks

- [x] T001 [US1] Add search input rendering to `advanced_filter_bar` component in `src/presentacion_reflex/components/shared/advanced_filter_bar.py` — Create search input box with label "Buscar" and `rx.input` using existing props (`search_placeholder`, `on_search`, `search_value`) with `NEU_FILTER_INPUT_STYLE` and width `["100%", "100%", "250px"]`

- [x] T002 [US1] Insert search input as first child in desktop filter content in `src/presentacion_reflex/components/shared/advanced_filter_bar.py` — Add the search input box as the first element in `desktop_filter_content` flex container (line ~69-77)

- [x] T003 [US1] Insert search input as first child in mobile filter content in `src/presentacion_reflex/components/shared/advanced_filter_bar.py` — Add the search input box as the first element in `mobile_filter_content` flex container (line ~80-86)

---

## Phase 4: User Story 2 - Cross-Module Verification

**Story Goal**: Verify that the search input appears and functions correctly across all 7 affected modules without modifying individual module pages.

**Independent Test Criteria**:
- Search input visible in Personas module
- Search input visible in Propiedades module
- Search input visible in Contratos module
- Search input visible in Liquidaciones module
- Search input visible in Liquidación de Asesores module
- Search input visible in Recaudos module
- Search input visible in Incidentes module
- Search functionality works in all modules
- Clear button resets search value

### Tasks

- [x] T004 [P] [US2] Run linting on modified component — Execute `ruff check src/presentacion_reflex/components/shared/advanced_filter_bar.py` to verify code quality

- [x] T005 [P] [US2] Verify search input in Personas module — Navigate to Personas page, confirm search input visible in Advanced Filters, test search functionality

- [x] T006 [P] [US2] Verify search input in Propiedades module — Navigate to Propiedades page, confirm search input visible in Advanced Filters, test search functionality

- [x] T007 [P] [US2] Verify search input in Contratos module — Navigate to Contratos page, confirm search input visible in Advanced Filters, test search functionality

- [x] T008 [P] [US2] Verify search input in Liquidaciones module — Navigate to Liquidaciones page, confirm search input visible in Advanced Filters, test search functionality

- [x] T009 [P] [US2] Verify search input in Liquidación de Asesores module — Navigate to Liquidación de Asesores page, confirm search input visible in Advanced Filters, test search functionality

- [x] T010 [P] [US2] Verify search input in Recaudos module — Navigate to Recaudos page, confirm search input visible in Advanced Filters, test search functionality

- [x] T011 [P] [US2] Verify search input in Incidentes module — Navigate to Incidentes page, confirm search input visible in Advanced Filters, test search functionality

---

## Phase 5: Polish & Cross-Cutting Concerns

### Tasks

- [x] T012 Verify responsive behavior — Test desktop view (md breakpoint and above) shows horizontal filter layout with search input, test mobile view shows drawer with search input at top

- [x] T013 Verify filter integration — Test that search works combined with other filters (dropdowns, toggles), verify clear button resets all filters including search, verify active filter count badge includes search

- [x] T014 Visual consistency validation — Confirm search input dimensions match other filter controls (40px height, 8px border radius), confirm alignment and spacing are consistent

---

## Dependencies

```
Phase 3 (US1) ──→ Phase 4 (US2) ──→ Phase 5
     │                  │
     └── T001 ──→ T002 ──→ T003
                         │
                         └── T004, T005-T011 (parallel)
                                    │
                                    └── T012, T013, T014 (parallel)
```

## Parallel Execution Opportunities

**Within US1**: T002 and T003 can be executed in parallel (different locations in same file)

**Within US2**: T004-T011 can all be executed in parallel (independent verification tasks)

**Within Phase 5**: T012, T013, T014 can all be executed in parallel (independent validation tasks)

## Implementation Strategy

**MVP Scope**: T001-T003 (core implementation)

This is a single-point fix — modifying one component file restores search functionality across all 7 modules. The implementation is minimal and low-risk:

1. Add search input rendering to `advanced_filter_bar.py` (T001)
2. Insert in desktop view (T002)
3. Insert in mobile view (T003)

Total implementation tasks: 3
Total verification tasks: 11
Estimated effort: Small (1-2 hours implementation, 1-2 hours verification)
