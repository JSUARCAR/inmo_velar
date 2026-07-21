# Research: Auditoría y Corrección de Persistencia en Módulo de Contratos

**Date**: 2026-07-21
**Feature**: 059-debug-contratos-persistence

## Bug Analysis: Why Data Is Lost on Edit

### Root Cause Investigation

The investigation traced the complete data flow from UI form → State → Service → Repository → PostgreSQL for both Mandato and Arrendamiento contract types.

### Bug #1: ENLACE_VIDEO missing from Mandato UPDATE query

**File**: `src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py`
**Method**: `actualizar()` (lines 275-334)
**Evidence**: The UPDATE SET clause includes 20 columns but **omits `ENLACE_VIDEO`**. The SQL ends with:

```sql
DOCUMENTO_CONSIGNATARIO = %s,
UPDATED_AT = %s,
UPDATED_BY = %s
WHERE ID_CONTRATO_M = %s
```

The `ENLACE_VIDEO` column is present in the INSERT query (`crear()` method, line 30, 56) but absent from the UPDATE query. This means:
- On CREATE: `enlace_video` IS persisted ✅
- On UPDATE: `enlace_video` is SILENTLY LOST ❌

**Impact**: Any edit to a Mandato contract loses the video link value.

**Arrendamiento status**: The Arrendamiento repository (`repositorio_contrato_arrendamiento_postgres.py`) correctly includes `ENLACE_VIDEO` and `RESPONSABLE_DEPOSITO_ID` in its UPDATE query. No bug here.

### Bug #2: Missing uppercase fallback in _row_to_entity() for consignatario fields

**File**: `src/infraestructura/persistencia/repositorio_contrato_mandato_postgres.py`
**Method**: `_row_to_entity()` (lines 336-409)
**Evidence**: All fields use the pattern `row_dict.get("field") or row_dict.get("FIELD")` for case-insensitive access. However:

```python
# Lines 402-404 — MISSING uppercase fallback:
consignatario=row_dict.get("consignatario"),
documento_consignatario=row_dict.get("documento_consignatario"),
enlace_video=row_dict.get("enlace_video"),
```

PostgreSQL returns column names in UPPERCASE by default when using `cursor.fetchall()` with `psycopg2`. Without the uppercase fallback, these fields return `None` even when data exists in the database.

**Impact**: When reading a Mandato contract, `consignatario`, `documento_consignatario`, and `enlace_video` may appear empty in the UI even though data exists in the DB.

### Bug #3 (Potential): State-level form_data hydration

**File**: `src/presentacion_reflex/state/contratos_state.py`
**Method**: `open_edit_modal()` and `save_contrato()`
**Status**: Needs verification — the `open_edit_modal` method hydrates `form_data` from the entity, but if the entity has `None` values due to Bug #2, the form will show empty fields.

## Decisions

### Decision 1: Fix strategy
- **Chosen**: Surgical fix in the repository layer only
- **Rationale**: The bug is a data mapping issue in the SQL query and row-to-entity conversion. The service layer and UI layer correctly handle the data — the problem is specifically in the repository.
- **Alternatives considered**: Refactoring the entire repository (rejected — too risky for a bug fix, violates atomic changes principle)

### Decision 2: Retroactive data correction
- **Chosen**: Write a one-time SQL script to fix existing records where `ENLACE_VIDEO` was lost
- **Rationale**: User explicitly requested correction for existing contracts
- **Note**: Only applicable if the column exists in the DB (it was added via `migration_campos_extra_contratos.sql`)

### Decision 3: Testing approach
- **Chosen**: Integration tests that create a contract, update it, and verify all fields round-trip correctly
- **Rationale**: The bug is specifically about data flowing through the full stack; unit tests on isolated methods won't catch it

## Assumptions Validated

1. ✅ PostgreSQL is the storage layer — confirmed by repository implementations
2. ✅ Clean Architecture is followed — confirmed by layer separation
3. ✅ The UI forms correctly capture all fields — confirmed by inspecting `formulario_contrato_mandato.py`
4. ✅ The services correctly pass all fields to entities — confirmed by inspecting `servicio_contrato_mandato.py`
5. ✅ The INSERT queries include all fields — confirmed by inspecting `crear()` methods
6. ❌ The UPDATE queries include all fields — **FAILED** for Mandato (Bug #1)
7. ✅ The Arrendamiento repository is correct — confirmed by inspection
