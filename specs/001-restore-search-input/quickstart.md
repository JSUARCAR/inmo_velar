# Quickstart Validation Guide: Restore Search Input

## Prerequisites

- Development environment running (`reflex run`)
- Access to all 7 module pages
- Browser with desktop and mobile viewport capabilities

## Validation Scenarios

### Scenario 1: Visual Verification (All Modules)

**Steps**:
1. Navigate to each module page: Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Incidentes
2. Locate the "Filtros Avanzados" section
3. Verify search input is visible as the first filter control

**Expected Outcome**:
- Search input appears with placeholder text (e.g., "Buscar por nombre o documento...")
- Input has consistent dimensions (40px height, 8px border radius)
- Input is aligned with other filter controls
- Label "Buscar" appears above the input

### Scenario 2: Search Functionality (Per Module)

**Steps**:
1. Navigate to a module (e.g., Personas)
2. Enter a search term in the search input
3. Verify the search value is reflected in the state
4. Verify filtering occurs (either real-time or on next data load)

**Expected Outcome**:
- Text input accepts characters
- Search value is stored in module state
- Results are filtered based on search term
- Clear button resets search value

### Scenario 3: Cross-Module Consistency

**Steps**:
1. Navigate through all 7 modules
2. Compare search input dimensions, spacing, and alignment
3. Verify mobile responsive behavior (drawer)

**Expected Outcome**:
- Search input maintains consistent appearance across all modules
- Mobile drawer shows search input at top of filter list
- No visual regressions in filter layout

### Scenario 4: Filter Integration

**Steps**:
1. Apply search term
2. Apply additional filters (dropdowns, toggles)
3. Verify combined filtering works correctly

**Expected Outcome**:
- Search and other filters work together without conflicts
- Clear button resets all filters including search
- Active filter count badge includes search in count

## Test Commands

```bash
# Start development server
reflex run

# Run linting
ruff check src/presentacion_reflex/components/shared/advanced_filter_bar.py

# Run type checking (if configured)
mypy src/presentacion_reflex/components/shared/advanced_filter_bar.py
```

## Success Metrics

1. **Visual**: Search input visible in 7/7 modules
2. **Functional**: Search filters data correctly in all modules
3. **Consistent**: Dimensions match `NEU_FILTER_INPUT_STYLE` (40px height, 8px radius)
4. **Responsive**: Mobile drawer displays search input correctly
5. **Integrated**: Search works with other filters without conflicts

## Regression Check

- [ ] Existing filter dropdowns still function
- [ ] Toggle switches still function
- [ ] Clear button resets all filters
- [ ] Active filter count badge updates correctly
- [ ] Desktop and mobile views render correctly
- [ ] No visual regressions in filter bar layout
