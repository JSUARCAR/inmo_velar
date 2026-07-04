# Quick Start: Eliminar Liquidación de Propietario

**Date**: 2026-06-30 | **Feature**: 002-eliminar-liquidacion

## Prerequisites

- PostgreSQL database with `LIQUIDACIONES` table
- Python 3.11+ with dependencies from `pyproject.toml`
- Reflex framework installed

## Database Migration

Run the following SQL against your PostgreSQL database:

```sql
-- Add ELIMINADA column for soft delete
ALTER TABLE LIQUIDACIONES ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE;

-- Add index for query performance
CREATE INDEX idx_liquidaciones_eliminada ON LIQUIDACIONES(ELIMINADA);

-- Register permission (optional - depends on RBAC setup)
INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
VALUES ('Liquidaciones', '/liquidaciones', 'ELIMINAR', 'Eliminar liquidaciones', 'Gestión')
ON CONFLICT DO NOTHING;
```

## Files to Modify

| Layer | File | Changes |
|-------|------|---------|
| Domain | `src/dominio/entidades/liquidacion.py` | Add `eliminada: bool = False` |
| Domain | `src/dominio/interfaces/repositorio_liquidacion.py` | Add `eliminar()` method |
| Persistence | `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` | Add `eliminar()` + update ~12 queries |
| Service | `src/aplicacion/servicios/servicio_financiero.py` | Add `eliminar_liquidacion()` |
| State | `src/presentacion_reflex/state/liquidaciones_state.py` | Add delete handlers + state vars |
| UI | `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` | Add delete button |
| UI | `src/presentacion_reflex/pages/liquidaciones.py` | Add table button + import dialog |
| UI | `src/presentacion_reflex/components/liquidaciones/__init__.py` | Export dialog |

## Verification Steps

### 1. Unit Tests
```bash
# From project root
pytest tests/unit/test_eliminar_liquidacion.py -v
```

### 2. Integration Tests
```bash
pytest tests/integration/test_liquidacion_deletion.py -v
```

### 3. Manual Smoke Test
1. Login as admin user with "Liquidaciones" permissions
2. Navigate to Liquidaciones page
3. Select a liquidation in "En Proceso" state
4. Click "Eliminar" button
5. Verify dialog shows summary and financial breakdown
6. Check the confirmation checkbox
7. Click "Eliminar" in dialog
8. Verify: toast notification appears, table reloads, liquidation is hidden
9. Query database: `SELECT * FROM LIQUIDACIONES WHERE ELIMINADA = TRUE` should show the record

### 4. Negative Test
1. Attempt to delete a liquidation in "Pagada" state
2. Verify: error message "Las liquidaciones en estado Pagada forman parte del histórico financiero y no pueden eliminarse."
3. Verify: liquidation remains unchanged

### 5. Idempotency Test
1. Delete a liquidation
2. Attempt to delete the same liquidation again
3. Verify: no error, returns success (idempotent)

## Architecture Overview

```
User clicks "Eliminar"
        │
        ▼
   UI Component
   (delete_confirm_dialog.py)
        │
        ▼
   Reflex State
   (liquidaciones_state.py)
        │
        ▼
   Service Layer
   (servicio_financiero.py)
        │
        ▼
   Repository
   (repositorio_liquidacion_postgres.py)
        │
        ▼
   Database (LIQUIDACIONES, AUDITORIA_CAMBIOS)
```

## Rollback

If the feature needs to be removed:

```sql
-- Remove added column
ALTER TABLE LIQUIDACIONES DROP COLUMN ELIMINADA;

-- Remove index
DROP INDEX idx_liquidaciones_eliminada;

-- Remove permission
DELETE FROM PERMISOS WHERE MODULO = 'Liquidaciones' AND ACCION = 'ELIMINAR';
```

Then revert the code changes in the files listed above.
