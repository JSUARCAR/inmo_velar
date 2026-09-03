# Quickstart / Validation Guide: fix-admin-value-liquidation

This guide provides steps to validate the cascade synchronization of the administration value from a property to its draft liquidations.

## Prerequisites
- Local database running with `test.db` (or local PostgreSQL).
- Application running via `reflex run --env dev`.

## Validation Scenarios

### Scenario 1: Cascade Update without Manual Overrides
1. Go to the Liquidaciones module and create a new liquidation for a property (e.g. Property ID 1) with an initial administration value of $100,000. Ensure it is in 'En Proceso'.
2. Go to the Propiedades module and edit Property ID 1. Change the "Valor Administración" to $150,000 and save.
3. Observe the success toast notification.
4. Go back to the Liquidaciones module. Check the "En Proceso" liquidation.
5. **Expected Outcome**: The "Gastos Admin" should now be $150,000, and the "Neto a Pagar" should be reduced by the $50,000 difference.

### Scenario 2: Protection of Manual Overrides
1. Go to the Liquidaciones module and edit an 'En Proceso' liquidation. Manually change "Gastos Admin" to $80,000 (or $0) and save.
2. Go to the Propiedades module and update the property's administration value to $150,000.
3. Go back to Liquidaciones.
4. **Expected Outcome**: The liquidation should STILL show $80,000 (or $0). The cascade should not have overwritten the manual override.

### Scenario 3: Immutability of Closed Liquidations
1. Approve or pay a liquidation (changing state to 'Aprobada' or 'Pagada').
2. Update the property's administration value.
3. **Expected Outcome**: The approved/paid liquidation remains completely unchanged.

### Scenario 4: Temporal Boundaries (Current Period Only)
1. Create two 'En Proceso' liquidations for the same property: one for the current billing cycle, and one artificially set to a previous billing cycle.
2. Update the property's administration value.
3. **Expected Outcome**: Only the liquidation for the current billing cycle is updated. The past period liquidation remains unchanged.
