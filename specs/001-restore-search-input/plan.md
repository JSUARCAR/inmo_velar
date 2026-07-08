# Implementation Plan: Restore Search Input in Advanced Filters

## Technical Context

- **Technology Stack**: Reflex (Python-based React framework), Hexagonal Architecture
- **Module Location**: `src/presentacion_reflex/` (presentation layer)
- **Key Component**: `src/presentacion_reflex/components/shared/advanced_filter_bar.py`
- **Affected Modules**: 7 pages (Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Incidentes)
- **State Management**: Each module has its own Reflex State class with `set_search()` method

## Root Cause Analysis

The `advanced_filter_bar` component accepts search-related props (`search_placeholder`, `on_search`, `search_value`) but does NOT render a search input. All 7 module pages pass these props but never receive a rendered search input.

**Evidence**:
- `advanced_filter_bar.py` lines 12-14 define search props
- Component only renders `*children` (filter dropdowns, toggles) in desktop/mobile views
- No `rx.input` is created using the search props

## Constitution Check

No constitution file exists. Proceeding with standard best practices.

## Implementation Strategy

**Single-point fix**: Add the search input inside `advanced_filter_bar` component using the already-defined search props. This ensures:
1. Consistent search input across all 7 modules
2. No changes needed to individual module pages
3. The search props (already passed by all pages) become functional

## Phase 0: Research

See `research.md` for detailed analysis.

## Phase 1: Design & Contracts

### Data Model
No data model changes required - this is a UI component restoration.

### Interface Contract
The search input will be rendered inside `advanced_filter_bar` as the first child element, maintaining the existing prop interface that all 7 modules already use.

### Quickstart Validation
See `quickstart.md` for validation scenarios.

## Phase 2: Implementation Tasks

1. **Modify `advanced_filter_bar.py`**: Add search input rendering using existing props
2. **Verify styling**: Ensure search input uses `NEU_FILTER_INPUT_STYLE` for consistency
3. **Test all 7 modules**: Verify search input appears and functions correctly
4. **Visual validation**: Confirm dimensions, alignment, and spacing match design standards

## Success Criteria

1. All 7 modules display the search input in Advanced Filters
2. Search input filters data correctly in all modules
3. UI dimensions and alignment match existing filter controls
4. No regressions to existing filter functionality
