# Research: Corrección de Carga de Datos en Edición de Liquidaciones

**Date**: 2026-07-13
**Feature**: 052-fix-edit-liquidacion-data

## 1. Root Cause Analysis

### Data Flow for Edit Modal

```
UI Click → LiquidacionFormState.open_edit_modal(id)
  → ServicioLiquidacionAsesores.obtener_detalle_completo(id)
    → repo_liquidacion.obtener_por_id(id)          # LIQUIDACIONES_ASESORES
    → repo_descuento.listar_por_liquidacion(id)     # DESCUENTOS_ASESORES
    → repo_pago.listar_por_liquidacion(id)          # PAGOS_ASESORES
    → repo_bonificacion.listar_por_liquidacion(id)  # BONIFICACIONES_ASESORES
    → repo_liquidacion.obtener_contratos_de_liquidacion(id)  # LIQUIDACIONES_CONTRATOS
  → Populate form_data, existing_discounts, existing_bonuses, advisor_properties
```

### Data Flow for Generation

```
LiquidacionFormState.generar_liquidacion_masiva(form_data)
  → ServicioLiquidacionAsesores.generar_liquidaciones_masivas_optimizado(periodo, usuario)
    → FOR EACH asesor:
      → generar_liquidacion_multi_contrato(id_asesor, periodo, contratos_lista)
        → BEGIN TRANSACTION
        → repo_liquidacion.crear(liquidacion)                    # INSERT LIQUIDACIONES_ASESORES
        → repo_liquidacion.guardar_contratos_liquidacion(...)    # INSERT LIQUIDACIONES_CONTRATOS
        → agregar_descuento(seguro)                              # INSERT DESCUENTOS_ASESORES
        → agregar_descuento(4x1000)                              # INSERT DESCUENTOS_ASESORES
        → COMMIT TRANSACTION
```

### Potential Root Cause: Transaction Nesting Issue

**Finding**: In `generar_liquidacion_multi_contrato()` (line 216-356 of `servicio_liquidacion_asesores.py`):

1. The method opens a transaction: `with self.repo_liquidacion.db_manager.transaccion():` (line 238)
2. Inside this transaction, it calls `self.agregar_descuento()` (lines 322, 330)
3. `agregar_descuento()` (line 492) calls `self.repo_descuento.crear()` which opens its OWN transaction: `with self.db_manager.transaccion() as conn:` (line 38 of `repositorio_descuento_asesor.py`)

**Risk**: If the database manager uses `psycopg2` with autocommit=False, nested transactions may cause issues:
- If using SAVEPOINTs: nested `BEGIN` may be treated as SAVEPOINT (correct behavior)
- If using separate connections: the inner transaction may not see the outer transaction's uncommitted data
- If using the same connection: the inner `BEGIN` may fail or cause deadlock

**Hypothesis**: The discounts created inside `agregar_descuento()` within the generation transaction may not be properly committed if:
- The nested transaction handling is incorrect
- The `agregar_descuento()` method uses a different connection than the outer transaction
- The `_invalidar_caches()` call at line 355 interferes with transaction state

### Secondary Finding: Missing LIQUIDACIONES_CONTRATOS Table Definition

**Finding**: The SQL schema file `create_liquidaciones_tables.sql` does NOT define the `LIQUIDACIONES_CONTRATOS` table. This table is only referenced in:
- `repositorio_liquidacion_asesor.py` (guardar_contratos_liquidacion, obtener_contratos_de_liquidacion)
- `migration_add_comision_contrato.sql` (ALTER TABLE)

**Risk**: If the `LIQUIDACIONES_CONTRATOS` table was created separately (perhaps via a different migration or manual script), it may have different constraints or missing indexes that affect query performance.

## 2. Transaction Boundary Analysis

### Current Implementation

```python
# servicio_liquidacion_asesores.py line 238
with self.repo_liquidacion.db_manager.transaccion():
    # ... creation logic ...
    self.repo_liquidacion.crear(liquidacion, usuario)        # Uses repo's connection
    self.repo_liquidacion.guardar_contratos_liquidacion(...)  # Uses repo's connection
    self.agregar_descuento(...)                               # Opens NEW transaction?
```

### agregar_descuento() Implementation

```python
# servicio_liquidacion_asesores.py line 492
def agregar_descuento(self, id_liquidacion, tipo, descripcion, valor, usuario):
    descuento = DescuentoAsesor(
        id_liquidacion_asesor=id_liquidacion,
        tipo_descuento=tipo,
        descripcion_descuento=descripcion,
        valor_descuento=valor,
    )
    self.repo_descuento.crear(descuento, usuario)
    self._recalcular_valor_neto(id_liquidacion)
```

### repositorio_descuento_asesor.crear() Implementation

```python
# repositorio_descuento_asesor.py line 38
with self.db_manager.transaccion() as conn:
    cursor = self.db_manager.get_dict_cursor(conn)
    cursor.execute(query, params)
    row = cursor.fetchone()
    # ...
```

**Critical Issue**: `self.db_manager.transaccion()` may create a NEW connection if called from a different repository instance. This would mean the discount INSERT runs on a different connection than the liquidation INSERT, potentially causing:
1. The discount INSERT commits before the liquidation INSERT (if the inner transaction commits independently)
2. The discount INSERT fails silently if the connection pool is exhausted
3. The discount INSERT uses a different isolation level

## 3. Database Schema Verification

### Tables Involved

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| LIQUIDACIONES_ASESORES | Main liquidation record | ID_LIQUIDACION_ASESOR (PK), ID_ASESOR, PERIODO_LIQUIDACION |
| LIQUIDACIONES_CONTRATOS | Properties linked to liquidation | ID_LIQUIDACION_ASESOR (FK), ID_CONTRATO_A, CANON_INCLUIDO |
| DESCUENTOS_ASESORES | Discounts applied | ID_LIQUIDACION_ASESOR (FK), TIPO_DESCUENTO, VALOR_DESCUENTO |
| BONIFICACIONES_ASESORES | Bonuses applied | ID_LIQUIDACION_ASESOR (FK), TIPO_BONIFICACION, VALOR_BONIFICACION |

### Relationships

```
LIQUIDACIONES_ASESORES (1) ──< (N) LIQUIDACIONES_CONTRATOS
LIQUIDACIONES_ASESORES (1) ──< (N) DESCUENTOS_ASESORES
LIQUIDACIONES_ASESORES (1) ──< (N) BONIFICACIONES_ASESORES
LIQUIDACIONES_ASESORES (1) ──< (N) PAGOS_ASESORES
```

## 4. Edit Modal Data Loading Analysis

### obtener_contratos_de_liquidacion() Query

```sql
SELECT lc.ID_CONTRATO_A, lc.CANON_INCLUIDO, 
       lc.COMISION_PORCENTAJE_CONTRATO, lc.COMISION_MONTO_CONTRATO,
       ca.CANON_ARRENDAMIENTO, 
       p.DIRECCION_PROPIEDAD, per.NOMBRE_COMPLETO as ARRENDATARIO,
       cm.COMISION_PORCENTAJE_CONTRATO_M as PCT_MANDATO_ACTUAL
FROM LIQUIDACIONES_CONTRATOS lc 
JOIN CONTRATOS_ARRENDAMIENTOS ca ON lc.ID_CONTRATO_A = ca.ID_CONTRATO_A 
JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD 
JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO 
JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA 
LEFT JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
WHERE lc.ID_LIQUIDACION_ASESOR = %s
```

**Risk**: This query uses INNER JOINs to CONTRATOS_ARRENDAMIENTOS, PROPIEDADES, ARRENDATARIOS, and PERSONAS. If any of these records are deleted or have integrity issues, the query returns fewer rows than expected.

### listar_por_liquidacion() Query (Discounts)

```sql
SELECT * FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = %s ORDER BY FECHA_REGISTRO DESC
```

**Risk**: This query is straightforward. If discounts are missing, the issue is in persistence, not retrieval.

## 5. Hypothesis Summary

| # | Hypothesis | Likelihood | Impact | Investigation Needed |
|---|-----------|------------|--------|---------------------|
| H1 | Nested transaction in agregar_descuento() causes discounts to not persist | HIGH | HIGH | Verify transaction nesting behavior |
| H2 | LIQUIDACIONES_CONTRATOS INSERT fails silently during generation | MEDIUM | HIGH | Check if table exists and has correct schema |
| H3 | Connection pool exhaustion during massive generation | LOW | HIGH | Check connection pool config |
| H4 | Cache invalidation interferes with transaction commit | LOW | MEDIUM | Check _invalidar_caches() behavior |
| H5 | Data exists in DB but edit query has JOIN issues | LOW | HIGH | Verify JOIN integrity |

## 6. Recommended Investigation Steps

1. **Query PostgreSQL directly** for CRISTIAN JAMIOY period 2026-07:
   - Check LIQUIDACIONES_ASESORES record exists
   - Check LIQUIDACIONES_CONTRATOS records exist for that liquidation
   - Check DESCUENTOS_ASESORES records exist for that liquidation

2. **Add logging** to `agregar_descuento()` and `guardar_contratos_liquidacion()` to verify INSERT success

3. **Verify transaction nesting** by checking `db_manager.transaccion()` implementation

4. **Test generation** for a new asesor and immediately query DB to verify all records exist

## 7. Decision: Fix Strategy

**Decision**: Implement a multi-layer fix:

1. **Atomicity Fix**: Ensure `agregar_descuento()` and `guardar_contratos_liquidacion()` reuse the outer transaction connection instead of opening new transactions
2. **Post-Generation Verification**: Add a verification step after generation that queries all three tables and confirms record counts match expectations
3. **Data Migration Script**: Create a script to reconstruct missing LIQUIDACIONES_CONTRATOS and DESCUENTOS_ASESORES records for affected liquidaciones
4. **Edit Modal Resilience**: Add fallback logic in `obtener_detalle_completo()` to handle partial data gracefully

**Rationale**: The nested transaction issue is the most likely root cause. Fixing atomicity addresses the prevention side, while migration and fallback address the recovery side.

**Alternatives Considered**:
- Only fix retrieval queries: Rejected because data may genuinely be missing from DB
- Only add migration: Rejected because doesn't prevent future occurrences
- Rewrite entire persistence layer: Rejected as overkill for a targeted fix
