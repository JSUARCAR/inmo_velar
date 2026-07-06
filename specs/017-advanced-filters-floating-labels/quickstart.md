# Quickstart Validation Guide: Floating Labels en Filtros Avanzados

**Date**: 2026-07-05
**Feature**: 017-advanced-filters-floating-labels

## Prerequisites

- Python 3.11+ environment active
- PostgreSQL database running (or `DATABASE_URL` set)
- Reflex CLI installed (`pip install reflex`)
- All dependencies from `requirements.txt` installed

## Validation Scenarios

### Scenario 1: Visual Verification - Módulo Personas

**Setup**:
```bash
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
reflex run --env dev
```

**Steps**:
1. Navigate to Personas module in the sidebar
2. Open "Filtros Avanzados" section
3. Verify each field shows a visible label:
   - "Buscar por nombre" - label visible inside empty field
   - "Rol" - label visible in select trigger
   - "Fecha Desde" - label visible in date field
   - "Fecha Hasta" - label visible in date field
4. Click on "Buscar por nombre" field
5. Verify label animates upward smoothly (150-300ms)
6. Type "Juan" in the field
7. Verify label remains visible in upper position
8. Clear the field
9. Verify label returns to original position

**Expected**: All 4 fields show permanent floating labels. Labels animate smoothly on focus/value change.

---

### Scenario 2: Visual Verification - Módulos con Componentes Raw

**Steps**:
1. Navigate to Seguros module
2. Verify "Buscar seguro por nombre" label is visible
3. Verify "Estado" select label is visible
4. Navigate to Saldos a Favor module
5. Verify "Tipo" and "Estado" select labels are visible
6. Navigate to Reportes module
7. Verify sidebar search shows "Buscar reportes" label
8. Select a report and verify dynamic filter labels appear

**Expected**: All raw modules now show floating labels with neumorphic styling.

---

### Scenario 3: Keyboard Navigation & Accessibility

**Steps**:
1. Navigate to any module with filters
2. Press Tab to move through filter fields
3. Verify focus indicator is visible on each field
4. Press Shift+Tab to move backward
5. In a select field, press Enter to open dropdown
6. Use arrow keys to navigate options
7. Press Enter to select an option

**Expected**: Full keyboard navigation works. Focus indicators visible. Labels announced by screen readers.

---

### Scenario 4: Responsive Verification

**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test at viewport widths:
   - 1440px (desktop): Labels and fields properly spaced
   - 768px (tablet): Labels remain legible, fields stack if needed
   - 375px (mobile): Labels truncated if too long, fields full-width
4. Test on actual mobile device if available

**Expected**: Labels remain readable at all breakpoints. No layout overflow or clipping.

---

### Scenario 5: Regression - Filter Functionality

**Steps**:
1. Navigate to Liquidaciones module
2. Enter a search term in "Buscar" field
3. Verify table filters correctly
4. Select a value in "Período" dropdown
5. Verify table filters by period
6. Clear all filters
7. Verify table shows all records

**Expected**: All existing filter behavior unchanged. Floating labels don't affect filtering logic.

---

### Scenario 6: Error State Verification

**Steps**:
1. Find a field with validation (if any filter has error state)
2. Trigger the error state
3. Verify label color changes to red (`var(--red-9)`)
4. Verify label remains visible and readable

**Expected**: Error state maintains label visibility with color change.

---

## Quick Smoke Test (Automated)

```bash
# Run existing Playwright tests to catch regressions
cd "C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX"
python playwright_test.py
```

## Checklist

- [ ] All 13 modules show floating labels on filter fields
- [ ] Labels animate smoothly (no jarring jumps)
- [ ] Labels remain visible with values entered
- [ ] Labels return to original position when cleared
- [ ] Keyboard navigation works (Tab, Shift+Tab, Enter, arrows)
- [ ] Screen readers announce labels correctly
- [ ] Responsive at desktop, tablet, mobile viewports
- [ ] No filter functionality regression
- [ ] Error states maintain label visibility
- [ ] Neumorphic styling consistent across all modules
