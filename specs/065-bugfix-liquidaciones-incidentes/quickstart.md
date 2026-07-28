# Quickstart & Validation Guide

## Validation Steps

1. **Start the application**
   ```bash
   reflex run
   ```
   *Note: Ensure the local test database is populated with properties and incidents, particularly "CONJ CIUDADELA COMFENALCO MZ H CS 29".*

2. **Navigate to Liquidaciones**
   - Log into the application as an Administrator.
   - Go to the "Liquidaciones" module.

3. **Validate Incident Rendering in Edit Modal**
   - Locate a liquidation for the property "CONJ CIUDADELA COMFENALCO MZ H CS 29" (or any other property with associated incidents).
   - Click the "Edit" (pencil) button.
   - **Expected Outcome:** The "Incidentes Asociados" table inside the edit modal correctly lists the associated incidents and their discount values. It should not be empty or throw UI errors.

4. **Validate Incident Selection Modal Deployment**
   - While inside the Edit Modal, click the "Seleccionar Incidentes" button (with the link/chain icon).
   - **Expected Outcome:** A secondary modal correctly deploys on top of the edit modal.
   - The secondary modal should display a table of available incidents for that specific property.
   - It should not show any "Error al cargar incidentes: 'ID_PROPIEDAD'" message.
   - There should be no browser console errors regarding `pointer-events` or Z-index blockages.

5. **Validate Zero-Regressions**
   - Verify that adding a new incident to the liquidation correctly updates the internal table.
   - Save the liquidation and verify the total value is calculated successfully.
