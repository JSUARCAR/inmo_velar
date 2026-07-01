# Data Model: Eliminar Liquidación de Propietario

**Date**: 2026-06-30 | **Feature**: 002-eliminar-liquidacion

## Entity Changes

### Liquidacion (LIQUIDACIONES table)

**New Column**:
```sql
ALTER TABLE LIQUIDACIONES ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE;
```

| Column | Type | Default | Nullable | Description |
|--------|------|---------|----------|-------------|
| ELIMINADA | BOOLEAN | FALSE | NOT NULL | Soft delete flag. TRUE = liquidation is deleted but retained for audit. |

**Updated Entity** (`src/dominio/entidades/liquidacion.py`):
```python
@dataclass
class Liquidacion:
    # ... existing fields ...
    eliminada: bool = False  # NEW: soft delete flag
```

### State Transitions (Updated)

```
                    ┌─────────────┐
                    │ En Proceso  │
                    └──────┬──────┘
                           │ Aprobar
                           ▼
                    ┌─────────────┐
              ┌─────│  Aprobada   │─────┐
              │     └──────┬──────┘     │
              │            │ Pagar      │ Reversar
              │            ▼            │
              │     ┌─────────────┐     │
              │     │   Pagada    │     │
              │     └─────────────┘     │
              │                         │
              │ Reversar Pago           │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │  En Proceso │◄─────────│  Aprobada   │
       └─────────────┘          └─────────────┘
              │
              │ Cancelar
              ▼
       ┌─────────────┐
       │  Cancelada  │
       └─────────────┘

NEW: Any non-Pagada state → Eliminar → ELIMINADA=TRUE
     (Record retained, excluded from all queries)
```

### Validation Rules

| Rule | Expression | Error Message |
|------|-----------|---------------|
| Can delete | `estado_liquidacion != "Pagada"` | "Las liquidaciones en estado Pagada forman parte del histórico financiero y no pueden eliminarse." |
| Can delete | `eliminada == False` | "Esta liquidación ya fue eliminada." |
| Is deleted | `eliminada == True` | (silent no-op for idempotency) |

## Relationships

### Liquidacion → Documentos (Soportes)

**Current**: Documents reference LIQUIDACIONES via `TABLA_REFERENCIA='LIQUIDACIONES'` and `ID_ENTIDAD_REFERENCIA=<id_liquidacion>`

**After Deletion**: Documents are orphaned:
- `ID_ENTIDAD_REFERENCIA` set to NULL
- `TABLA_REFERENCIA` preserved for traceability
- Documents remain queryable but unlinked

## Query Impact Analysis

### Queries Requiring ELIMINADA Filter

| Query | Location | Current Filter | New Filter |
|-------|----------|----------------|------------|
| `listar_todas()` | repositorio:300 | None | `AND l.ELIMINADA = FALSE` |
| `listar_por_contrato()` | repositorio:287 | None | `AND ELIMINADA = FALSE` |
| `obtener_por_contrato_y_periodo()` | repositorio:246 | None | `AND ELIMINADA = FALSE` |
| `listar_por_propietario_y_periodo()` | repositorio:827 | None | `AND l.ELIMINADA = FALSE` |
| `listar_agrupadas_por_propietario_paginado()` | repositorio:847 | None | `AND l.ELIMINADA = FALSE` |
| `contar_con_filtros()` | repositorio | None | `AND ELIMINADA = FALSE` |
| `obtener_datos_para_pdf()` | repositorio:1102 | None | `AND l.ELIMINADA = FALSE` |
| `obtener_consolidado_propietario()` | repositorio:1218 | None | `AND l.ELIMINADA = FALSE` |
| `cancelar_por_propietario_y_periodo()` | repositorio:704 | `AND ESTADO_LIQUIDACION IN (...)` | Add `AND ELIMINADA = FALSE` |
| `reversar_por_propietario_y_periodo()` | repositorio:747 | `AND ESTADO_LIQUIDACION = 'Aprobada'` | Add `AND ELIMINADA = FALSE` |
| `aprobar_por_propietario_y_periodo()` | repositorio:1058 | `AND ESTADO_LIQUIDACION = 'En Proceso'` | Add `AND ELIMINADA = FALSE` |
| `obtener_estado_pago_actual()` | repositorio:262 | None | Add `AND ELIMINADA = FALSE` |

### Queries That Should NOT Be Affected

| Query | Reason |
|-------|--------|
| `obtener_por_id()` | Returns entity with `eliminada` field for audit/validation |
| `crear()` | Creates new record (always ELIMINADA=FALSE by default) |
| `actualizar()` | Should check `eliminada == False` before update |

## Audit Record Structure

### AUDITORIA_CAMBIOS Entry for Deletion

```sql
INSERT INTO AUDITORIA_CAMBIOS (
    TABLA_MODIFICADA,
    ID_REGISTRO,
    TIPO_OPERACION,
    CAMPO_MODIFICADO,
    VALOR_ANTERIOR,
    VALOR_NUEVO,
    USUARIO,
    FECHA_MODIFICACION,
    MOTIVO_CAMBIO
) VALUES (
    'LIQUIDACIONES',
    <id_liquidacion>,
    'DELETE',
    'ELIMINADA',
    'FALSE',
    'TRUE',
    <usuario_sistema>,
    <timestamp>,
    'Eliminación de liquidación - estado anterior: <estado>'
);
```

## Migration Script

```sql
-- migration_add_eliminada_column.sql
-- Feature: 002-eliminar-liquidacion
-- Date: 2026-06-30

-- Add soft delete column
ALTER TABLE LIQUIDACIONES ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE;

-- Create index for performance (most queries filter by ELIMINADA=FALSE)
CREATE INDEX idx_liquidaciones_eliminada ON LIQUIDACIONES(ELIMINADA);

-- Verify
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'LIQUIDACIONES' AND COLUMN_NAME = 'ELIMINADA';
```
