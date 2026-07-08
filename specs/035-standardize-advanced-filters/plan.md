# Implementation Plan: standardize-advanced-filters

**Branch**: `[035-standardize-advanced-filters]` | **Date**: 2026-07-07 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/035-standardize-advanced-filters/spec.md)

**Input**: Feature specification from `/specs/035-standardize-advanced-filters/spec.md`

## Summary

Standardize the Advanced Filters section across all 7 modules (Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Incidentes) to achieve a visually consistent UI. The approach creates a reusable `AdvancedFilterBar` component that encapsulates the standardized layout, spacing, dimensions, colors, and behavior. Each module's existing filter implementation will be migrated to use this shared component while preserving module-specific filter logic.

## Technical Context

**Language/Version**: Python 3.11+ / Reflex 0.8.x

**Primary Dependencies**: Reflex framework, existing `neuro_elements.py` component library, `styles.py` design tokens

**Storage**: PostgreSQL (No changes required — this is a UI-only standardization)

**Testing**: Manual visual validation in browser (Reflex interactive session) + responsive testing at 768px, 1024px, 1440px, 1920px

**Target Platform**: Web application (Frontend UI)

**Project Type**: Full-stack web application (Reflex)

**Performance Goals**: No measurable performance impact — pure UI restructure

**Constraints**: Must follow existing Reflex architecture, preserve all current filter functionality, use existing `neuro_*` component primitives, and maintain the neumorphic design language defined in `styles.py`

**Scale/Scope**: 7 module page files, 1 new shared component file, 1 style updates file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Clean Architecture**: Pass. Changes are strictly in the presentation layer (`src/presentacion_reflex/`). No business logic or data layer modifications.
- **Design System Consistency**: Pass. We extend the existing `styles.py` token system and `neuro_elements.py` component library rather than introducing new patterns.
- **Component Reusability**: Pass. The new `AdvancedFilterBar` component centralizes filter layout logic, reducing duplication across 7 modules.
- **Zero Regression**: Pass. All existing filter functionality (search, dropdowns, date pickers, toggles, checkboxes) is preserved; only visual presentation changes.
- **Responsive Design**: Pass. The component uses `rx.breakpoints()` for responsive behavior, consistent with existing patterns.

## Project Structure

### Documentation (this feature)

```text
specs/035-standardize-advanced-filters/
├── plan.md              # This file
├── research.md          # Analysis of current inconsistencies and design decisions
├── data-model.md        # No DB changes — documents filter state interface
├── quickstart.md        # Visual validation scenarios
├── contracts/
│   └── component-api.md # AdvancedFilterBar component API contract
└── tasks.md             # To be created
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── components/
│   └── shared/
│       └── advanced_filter_bar.py    # NEW: Reusable filter bar component
├── styles.py                          # MODIFIED: Add filter-specific tokens
├── pages/
│   ├── personas.py                    # MODIFIED: Migrate to AdvancedFilterBar
│   ├── propiedades.py                 # MODIFIED: Migrate to AdvancedFilterBar
│   ├── contratos.py                   # MODIFIED: Migrate to AdvancedFilterBar
│   ├── liquidaciones.py               # MODIFIED: Migrate to AdvancedFilterBar
│   ├── liquidacion_asesores.py        # MODIFIED: Migrate to AdvancedFilterBar
│   ├── recaudos.py                    # MODIFIED: Migrate to AdvancedFilterBar
│   └── incidentes.py                  # MODIFIED: Migrate to AdvancedFilterBar
```

**Structure Decision**: The project already has a `components/shared/` directory for reusable components. The new `AdvancedFilterBar` fits naturally here alongside `floating_label.py` and `searchable_select.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
