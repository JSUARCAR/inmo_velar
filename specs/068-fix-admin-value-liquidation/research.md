# Research & Decisions: fix-admin-value-liquidation

## Topic: Temporal Boundaries ("Periodo Actual")

**Decision**: The SQL cascade will filter updates using `AND PERIODO = obtener_periodo_actual()`.
**Rationale**: Clarified in the spec that the update should only affect the active billing cycle. Using the centralized `obtener_periodo_actual()` function guarantees alignment with the rest of the financial modules and avoids discrepancies with calendar months.
**Alternatives considered**: Using SQL date functions (e.g. `EXTRACT(MONTH FROM CURRENT_DATE)`) was discarded because the business billing cycle might not strictly align with the raw calendar month in all edge cases.

## Topic: Concurrency ("Last Write Wins")

**Decision**: The application will allow natural SQL overwrites without optimistic locking. The UI save process is an independent transaction that will simply overwrite the background cascade if it occurs fractionally later.
**Rationale**: It is the industry standard for this type of conflict and avoids blocking users with complex locking or error messages.
**Alternatives considered**: Optimistic locking (e.g., passing a `version` or `updated_at` token to the frontend) was discarded as overkill for a rare edge case.

## Topic: Error Handling & Transaction Integrity

**Decision**: Strict Rollback. Any database failure (e.g., deadlocks, constraint violations) during the cascade will roll back the entire transaction, including the property update.
**Rationale**: Essential for financial data consistency. We cannot have a property showing one value while the system failed to cascade it, leaving a silent discrepancy.
**Alternatives considered**: Partial commits (saving the property and logging a failure for the cascade) were discarded because they violate the "single source of truth" principle for the active billing cycle.

## Topic: Recalculation Math

**Decision**: `NETO_A_PAGAR` will be recalculated using `TOTAL_INGRESOS - TOTAL_EGRESOS`.
**Rationale**: Direct implementation of the core accounting formula, eliminating any drift or cumulative rounding errors that delta-based math (`old_value + diff`) might introduce.
