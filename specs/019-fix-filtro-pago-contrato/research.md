# Phase 0: Research

## Unknowns Resolved

### 1. What does the "Pago Contrato" filter currently do in the UI and backend?
- **Decision**: Replace the `id_contrato` filter logic with a `dia_pago` filter logic for the "Pago Contrato" filter.
- **Rationale**: Currently, `recaudos.py` has a dropdown labeled "Pago Contrato" which lists full contracts and binds to `filter_contrato` (sending `id_contrato`). However, the backend (`repositorio_recaudo.py`) completely ignores this `id_contrato`. The user expects this filter to select records by the "day of payment" (`FECHA_PAGO` in `CONTRATOS_ARRENDAMIENTOS`) instead of selecting a specific contract.
- **Alternatives considered**: Fixing the `id_contrato` filter to actually filter by contract. Rejected because the user explicitly stated that the filter should use the "día de pago del contrato" as its functional criteria, not the contract itself.

### 2. How to implement the fallback for missing `FECHA_PAGO`?
- **Decision**: Use `COALESCE(NULLIF(ca.FECHA_PAGO, ''), EXTRACT(DAY FROM ca.FECHA_INICIO_CONTRATO_A::DATE)::TEXT)` in the PostgreSQL queries.
- **Rationale**: Per the clarification session, if a contract lacks a payment day, the system should fall back to the start day (`FECHA_INICIO_CONTRATO_A`). In PostgreSQL, since `FECHA_INICIO_CONTRATO_A` is stored as an ISO 8601 string, we can cast it to `DATE` and use `EXTRACT(DAY ...)` to get the day of the month.
- **Alternatives considered**: Handling the fallback in Python after fetching data. Rejected because doing it at the database level allows correct pagination and filtering in the `WHERE` clause.

### 3. How to provide options for the "Pago Contrato" filter in the UI?
- **Decision**: Provide a static list of days (1 to 31) plus "Todos" in the `RecaudosState`.
- **Rationale**: The day of payment is an integer between 1 and 31. Providing these as static options avoids a complex distinct query and aligns with how `Ciclo Operativo` is handled in the `Liquidaciones` module.
- **Alternatives considered**: Querying `SELECT DISTINCT FECHA_PAGO FROM CONTRATOS_ARRENDAMIENTOS`. Rejected because it could be slow and would return an unpredictable set of options depending on current active contracts.
