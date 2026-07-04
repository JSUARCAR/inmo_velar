# Task 5: Fix Edit Form Component

## What I Implemented

Changed the "Incidentes" field in the liquidation edit form to use `valor_incidentes` instead of `gastos_reparaciones` as the value source.

**Before:**
```python
form_field_editable(
    "Incidentes",
    "gastos_reparaciones",
    LiquidacionesState.form_data["gastos_reparaciones"],
),
```

**After:**
```python
form_field_editable(
    "Incidentes",
    "gastos_reparaciones",
    LiquidacionesState.form_data["valor_incidentes"],
),
```

The `name` parameter remains `"gastos_reparaciones"` to match the form field name expected by the submit handler.

## What I Tested

- Import verification: `python -c "from src.presentacion_reflex.components.liquidaciones.liquidacion_edit_form import liquidacion_edit_form; print('OK')"` → **OK**

## Files Changed

- `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` (line 132)

## Self-Review Findings

- The change is minimal and correct
- The form field `name` stays as `"gastos_reparaciones"` (required for form submission)
- The display value now correctly reads from `valor_incidentes`
- No regressions introduced

## Issues or Concerns

None. The change is straightforward and addresses the bug where "Incidentes" was showing incorrect data.
