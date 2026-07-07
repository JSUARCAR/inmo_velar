# Phase 0: Research

## Unknowns Resolved

1. **Why are the fields in "Editar Liquidación" and "Editar Recaudo" disabled/readonly?**
   - **Decision/Finding**: The inputs use the `neuro_floating_input` component, which is passed `value=Estado.form_data["campo"]`. In Reflex, binding `value` without providing an `on_change` event handler creates a controlled component that cannot be modified by the user (it immediately reverts to the state's fixed value on every keystroke). 
   - **Rationale**: Reflex enforces standard React semantics where a controlled component needs a state updater to change visually.
   - **Fix**: The solution is to add `on_change=lambda v: Estado.set_form_field("campo", v)` to the inputs that currently lack it. This explicitly completes the controlled component cycle.

2. **Affected fields**:
   - **Liquidaciones**: `gastos_administracion`, `gastos_servicios`, `valor_incidentes`, `pago_predial`, `otros_egresos`, `otros_ingresos` (all processed through `form_field_editable` in `liquidacion_edit_form.py`).
   - **Recaudos**: `fecha_pago`, `referencia_bancaria`, `periodo` (in `recaudos/modal_form.py`).

3. **Backend and Business Rules**:
   - Both modules (`LiquidacionesState` and `RecaudosState`) properly validate editability when opening the modal (`open_edit_modal`), verifying states like "Pendiente" or "Vencido" before allowing the form to appear. Thus, the RBAC and business rules at the Python backend level are correctly enforcing the editing conditions. The issue is purely a missing frontend event handler.

## Technology Choices

- **Reflex Forms**: Will continue using Reflex's controlled inputs with explicit state-updating handlers (`on_change`) for consistency with the rest of the application's forms.
