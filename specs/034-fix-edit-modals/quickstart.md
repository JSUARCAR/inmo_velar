# Quickstart Validation Guide: Fix Edit Modals

## Prerequisites
- Local PostgreSQL database running with development data.
- Reflex server running (`reflex run --env dev`).

## Validation Scenarios

### Scenario 1: Edit Liquidación
1. Open the browser to the application and log in.
2. Navigate to the **Liquidaciones** page.
3. Find a liquidación in "En Proceso" or a state that allows editing, and open the context menu to click **Editar**.
4. **Validation Check**: Verify that the numeric input fields in the "Ingresos" and "Egresos Variables" sections allow you to click into them and modify the numbers.
5. Change a value (e.g., set `Gastos Administración` to `150000`) and click **Guardar Cambios**.
6. **Validation Check**: Verify that the toast confirms the save operation, the modal closes, and the table updates with the newly saved values immediately.

### Scenario 2: Edit Recaudo
1. Navigate to the **Recaudos** page.
2. Locate a Recaudo that is in "Pendiente" or "Vencido" state and click **Editar** in its actions menu.
3. **Validation Check**: Verify that `Fecha de Pago`, `Referencia Bancaria`, and `Período` fields are interactive and can be changed.
4. Modify the `Fecha de Pago` and change the `Referencia Bancaria`.
5. Click **Guardar Pago**.
6. **Validation Check**: Verify that the changes successfully persist, the modal dismisses, and the Recaudos table reflects the updated data.
