# Quickstart Validation Guide: standardize-advanced-filters

**Date**: 2026-07-07

## Prerequisites

- Reflex development server running (`reflex run`)
- Browser open at `http://localhost:3000`
- All 7 modules accessible via navigation

## Validation Scenarios

### V1: Visual Consistency Across Modules

**Objective**: Verify all 7 modules display identical filter bar styling.

**Steps**:
1. Navigate to Personas module → observe filter bar styling (background, border, spacing)
2. Navigate to Propiedades → compare filter bar with Personas
3. Repeat for Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Incidentes
4. Verify: white background, light gray border, no shadow, 16px internal padding

**Expected**: All modules show identical container styling. No visual differences in background color, border, or shadow.

### V2: Component Dimensions

**Objective**: Verify all filter input components have uniform height and border-radius.

**Steps**:
1. Open any module with filters (e.g., Personas)
2. Inspect a text search input → verify height is 40px, border-radius is 8px
3. Inspect a Select/ComboBox → verify same dimensions
4. Inspect a DatePicker (if present) → verify same dimensions
5. Inspect a Toggle/Switch → verify vertical alignment with other components

**Expected**: All components share identical height (40px) and border-radius (8px).

### V3: Spacing Consistency

**Objective**: Verify uniform horizontal and vertical spacing between filter components.

**Steps**:
1. Open a module with multiple filters (e.g., Contratos with 4 filters + checkbox)
2. Measure horizontal gap between adjacent filter components → verify 16px
3. If filters wrap to multiple rows, measure vertical gap → verify 12px
4. Verify 24px padding inside the filter container

**Expected**: 16px horizontal gap, 12px vertical gap, 24px container padding.

### V4: Label Positioning

**Objective**: Verify filter labels follow the established pattern.

**Steps**:
1. Open Personas module
2. Verify search input has placeholder text only (no label above)
3. Verify "Filtrar por Rol" Select has label ABOVE the component
4. Verify "Desde"/"Hasta" DatePickers have labels ABOVE
5. Verify "Inactivos"/"Sin contrato" Toggles have labels to the RIGHT
6. Repeat verification for all 7 modules

**Expected**: Search = placeholder only; Select/DatePicker = label above; Toggle/Checkbox = label right.

### V5: Action Buttons (Icon-Only)

**Objective**: Verify all filter action buttons are icon-only with tooltips.

**Steps**:
1. Open any module with action buttons (e.g., Liquidaciones)
2. Verify buttons display only icons (no text labels)
3. Hover over each button → verify tooltip appears
4. Verify buttons are right-aligned in the filter row
5. Verify button height is 40px

**Expected**: All action buttons are icon-only, right-aligned, 40px height, with hover tooltips.

### V6: Active Filter Badge

**Objective**: Verify badge appears on "Limpiar" button when filters are active.

**Steps**:
1. Open a module with a "Limpiar" button (e.g., Personas)
2. Verify no badge is visible when all filters are at default values
3. Change one filter (e.g., select a Rol) → verify badge shows "1"
4. Change another filter → verify badge updates to "2"
5. Press "Limpiar" → verify badge disappears

**Expected**: Badge shows count of active filters, disappears when all filters are cleared.

### V7: Responsive Layout

**Objective**: Verify filter bar adapts to different screen widths.

**Steps**:
1. Open a module with many filters (e.g., Liquidaciones with 5 filters)
2. Set browser width to 1920px → filters should be in 1-2 rows
3. Set browser width to 1440px → filters should reflow if needed
4. Set browser width to 1024px → filters should wrap to additional rows
5. Set browser width to 768px → filters should remain usable, no overflow
6. Verify no horizontal scrollbar appears at any width

**Expected**: Filter bar is fully usable at all widths from 768px to 1920px+.

### V8: Auto-Apply Behavior

**Objective**: Verify filters apply automatically without a manual "Apply" button.

**Steps**:
1. Open any module with filters
2. Change a filter value (e.g., select a different Estado)
3. Verify the data table/grid updates automatically without clicking any button
4. Clear the filter → verify data updates again automatically

**Expected**: Filter changes take effect immediately without manual submission.

### V9: Zero Regressions

**Objective**: Verify all existing filter functionality still works.

**Steps**:
1. For each module, test every filter type:
   - Text search: type query → verify results filter
   - Select/ComboBox: change selection → verify results filter
   - DatePicker (if present): change date → verify results filter
   - Toggle/Switch: toggle on/off → verify results filter
   - Checkbox (if present): check/uncheck → verify results filter
2. Verify "Limpiar" resets all filters
3. Verify view toggle (grid/list) still works
4. Verify export buttons still work

**Expected**: All existing functionality is preserved with zero regressions.
