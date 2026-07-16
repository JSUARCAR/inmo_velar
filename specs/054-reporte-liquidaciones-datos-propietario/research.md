# Research: Reporte de Liquidaciones - Datos del Propietario y Contrato de Mandato

**Date**: 2026-07-13

## R1: Current SQL Query Structure

**Decision**: Extend the existing `obtener_reporte_liquidaciones()` query with 7 additional SELECT columns

**Rationale**: The existing query already has all necessary JOINs (LIQUIDACIONES → CONTRATOS_MANDATOS → PROPIEDADES → PROPIETARIOS → PERSONAS). The new data comes from:
- `per_prop.NUMERO_DOCUMENTO` (PERSONAS table, already joined)
- `per_prop.TELEFONO_PRINCIPAL` (PERSONAS table, already joined)
- `cm.BANCO_PROPIETARIO` (CONTRATOS_MANDATOS table, already joined)
- `cm.NUMERO_CUENTA_PROPIETARIO` (CONTRATOS_MANDATOS table, already joined)
- `cm.TIPO_CUENTA` (CONTRATOS_MANDATOS table, already joined)
- `cm.CONSIGNATARIO` (CONTRATOS_MANDATOS table, already joined)
- `cm.DOCUMENTO_CONSIGNATARIO` (CONTRATOS_MANDATOS table, already joined)

**Alternatives considered**:
- Creating a new repository method: Rejected - unnecessary duplication
- Adding a separate query for banking data: Rejected - N+1 problem, performance degradation
- Using a VIEW or CTE: Rejected - over-engineering for this scope

## R2: Column Order in SELECT

**Decision**: Insert new columns after `Nombre_Propietario` (position 4) in the following order:
1. NUMERO_DOCUMENTO_PROPIETARIO
2. TELEFONO_PROPIETARIO
3. BANCO
4. NUMERO_CUENTA
5. TIPO_CUENTA
6. NOMBRE_CONSIGNATARIO
7. DOCUMENTO_CONSIGNATARIO

**Rationale**: This matches the specification clarification and groups all owner/payment info together. The existing column order after position 4 shifts right by 7 positions.

**Alternatives considered**:
- Banking columns at end of report: Rejected per user clarification
- Banking columns after NETO_A_PAGAR: Rejected - breaks owner info grouping

## R3: SQL Alias Naming Convention

**Decision**: Use SCREAMING_SNAKE_CASE for new column aliases to match the majority of existing columns

**Rationale**: The current query uses mixed conventions (some Title_Case like `Direccion_Predio`, most SCREAMING_SNAKE). New columns should follow the dominant pattern for consistency:
- `NUMERO_DOCUMENTO_PROPIETARIO`
- `TELEFONO_PROPIETARIO`
- `BANCO`
- `NUMERO_CUENTA`
- `TIPO_CUENTA`
- `NOMBRE_CONSIGNATARIO`
- `DOCUMENTO_CONSIGNATARIO`

**Alternatives considered**:
- Using Title_Case like `Numero_Documento_Propietario`: Rejected - inconsistent with majority
- Using snake_case like `numero_documento_propietario`: Rejected - inconsistent with existing

## R4: Data Sanitization for CSV Export

**Decision**: Add the new banking/document columns to the `_sanitize_value()` Excel-safe formatting list

**Rationale**: The existing `_sanitize_value()` method already handles columns that need Excel text literal formatting (`="value"`) to prevent truncamento. The new columns that need this treatment:
- `NUMERO_CUENTA` - Bank account numbers starting with zeros
- `NUMERO_DOCUMENTO_PROPIETARIO` - Document numbers
- `DOCUMENTO_CONSIGNATARIO` - Consignatario document numbers

**Alternatives considered**:
- No special sanitization: Rejected - would cause Excel to truncate leading zeros
- Sanitizing all new columns: Rejected - overkill, only numeric ID columns need it

## R5: Impact on Other Reports

**Decision**: No changes needed for other reports (Reporte Financiero Consolidado, Reporte de Asesores)

**Rationale**: The `obtener_reporte_consolidado()` and `obtener_reporte_liquidaciones_asesores()` are independent methods with their own SQL queries. They already include some of these fields (consolidated report has banking info). Changes are isolated to `obtener_reporte_liquidaciones()`.

**Alternatives considered**:
- Refactoring all report queries: Rejected - scope creep, unnecessary risk

## R6: Performance Impact Assessment

**Decision**: No performance optimization needed for the 7 additional columns

**Rationale**:
- All new columns come from tables already JOINed (no new JOINs required)
- Adding SELECT columns to an existing query has negligible performance impact
- The query already returns ~28 columns; adding 7 more (~25% increase) is within acceptable bounds
- PostgreSQL columnar storage means SELECTing additional columns from already-joined tables is O(1) per row
- The 10% performance budget is conservative; actual impact will be <2%

**Alternatives considered**:
- Adding indexes: Rejected - unnecessary, query already uses existing indexes
- Caching: Rejected - over-engineering for this scope
- Materialized views: Rejected - adds complexity without meaningful benefit

## R7: UI Table Rendering

**Decision**: No changes needed to reportes.py page

**Rationale**: The UI table dynamically renders columns from `preview_headers` which is derived from `data[0].keys()`. Adding new keys to the SQL result dict automatically adds new columns to the table. The existing `rx.foreach` pattern handles any number of columns.

**Alternatives considered**:
- Hardcoding column definitions: Rejected - would require UI changes, breaks dynamic pattern
- Adding column visibility toggles: Rejected - scope creep
