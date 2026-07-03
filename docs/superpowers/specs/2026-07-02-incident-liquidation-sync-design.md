# Design: Sincronización Incidentes-Liquidaciones

**Date:** 2026-07-02
**Feature:** 003-integracion-incidentes-liquidaciones
**Status:** Approved

## Problem Statement

La integración entre los módulos Incidentes y Liquidaciones de Propietarios presenta dos incidencias:

1. **El valor de la cuota asociada al incidente no se refleja en el campo "Incidentes" de la liquidación.**
   - Aunque la asociación entre la cuota y la liquidación ya existe en BD, el valor no se visualiza en el campo destinado para descuentos por incidentes.

2. **El campo "Observaciones" debe incluir el identificador del incidente asociado.**
   - Requiere que, una vez una cuota sea vinculada a una liquidación, el campo Observaciones registre automáticamente el ID del incidente.

## Root Cause Analysis

### Incidencia 1: `valor_incidentes` no se muestra

El campo `valor_incidentes` existe en la entidad `Liquidacion` y en la tabla `LIQUIDACIONES` (valor = 70000 para liquidación #572), pero hay 4 puntos de ruptura en la cadena de datos:

| Capa | Archivo | Línea | Problema |
|------|---------|-------|----------|
| Repository | `repositorio_liquidacion_postgres.py` | 1192-1243 | `obtener_datos_para_pdf()` NO incluye `valor_incidentes` en el mapping |
| State (Edit) | `liquidaciones_state.py` | 596-617 | `open_edit_modal()` NO incluye `valor_incidentes` en `form_data` |
| State (Detail) | `liquidaciones_state.py` | 646-683 | `open_detail_modal()` NO crea `valor_incidentes_view` |
| Component (Edit) | `liquidacion_edit_form.py` | 129-133 | Campo "Incidentes" mapeado a `gastos_reparaciones` (INCORRECTO) |
| Component (Detail) | `liquidacion_detail_modal.py` | 187-189 | Solo muestra "Gastos Reparaciones", NO "Incidentes" |

**Nota crítica:** El campo "Incidentes" en el formulario de edición está confundido con `gastos_reparaciones` (costos de mantenimiento directo), que es un concepto diferente a `valor_incidentes` (descuentos por cuotas de planes de pago).

### Incidencia 2: `observaciones` no se actualiza

El servicio `servicio_incidente_liquidacion.py` en `asociar_incidente()` (líneas 164-176):
1. Crea la relación en `INCIDENTE_LIQUIDACION`
2. Actualiza el estado de la cuota
3. **NUNCA actualiza** el campo `observaciones` de la liquidación

## Current DB State

```sql
LIQUIDACIONES #572:  valor_incidentes=70000, observaciones=''
INCIDENTE_LIQUIDACION: (1, 52, 572, 1, 70000)
CUOTA_INCIDENTE: (1, 1, 1, 70000, 572, 'Asociada')
```

**Nota:** No existen triggers en la BD. El servicio asume que un trigger actualizará `valor_incidentes` pero nunca se crearon.

## Design Decisions

### Enfoque Seleccionado: DB Trigger + Backend

Se implementará sincronización a través de triggers PL/pgSQL como capa primaria, con actualización backend como fallback.

**Justificación:**
- Sincronización garantizada a nivel de base de datos
- Protege contra race conditions
- El servicio ya asume la existencia de triggers (pero no están creados)
- Consistente con el patrón de usar la BD como fuente de verdad

## Detailed Design

### 1. Database Triggers

#### 1.1 Función PL/pgSQL

```sql
CREATE OR REPLACE FUNCTION recalcular_valor_incidentes()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE LIQUIDACIONES 
    SET valor_incidentes = (
        SELECT COALESCE(SUM(valor_descuento), 0)
        FROM INCIDENTE_LIQUIDACION
        WHERE id_liquidacion = COALESCE(NEW.id_liquidacion, OLD.id_liquidacion)
    )
    WHERE id_liquidacion = COALESCE(NEW.id_liquidacion, OLD.id_liquidacion);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

#### 1.2 Triggers

```sql
CREATE TRIGGER trg_incidente_liq_insert
AFTER INSERT ON INCIDENTE_LIQUIDACION
FOR EACH ROW
EXECUTE FUNCTION recalcular_valor_incidentes();

CREATE TRIGGER trg_incidente_liq_delete
AFTER DELETE ON INCIDENTE_LIQUIDACION
FOR EACH ROW
EXECUTE FUNCTION recalcular_valor_incidentes();
```

#### 1.3 Migración SQL

Crear archivo: `scripts/migration_007_triggers_valor_incidentes.sql`

### 2. Backend Repository Updates

#### 2.1 `repositorio_liquidacion_postgres.py`

**Cambio en `obtener_datos_para_pdf()` (~línea 1235):**

Agregar después de `"otros_egr"`:
```python
"valor_incidentes": row.get("VALOR_INCIDENTES") or 0,
```

**Nuevo método `actualizar_valor_incidentes()`:**

```python
def actualizar_valor_incidentes(self, id_liquidacion: int) -> int:
    """Recalcula y actualiza valor_incidentes desde INCIDENTE_LIQUIDACION."""
    conn = self.db.obtener_conexion()
    cursor = conn.cursor()
    placeholder = self.db.get_placeholder()
    
    cursor.execute(f"""
        UPDATE LIQUIDACIONES 
        SET valor_incidentes = (
            SELECT COALESCE(SUM(valor_descuento), 0)
            FROM INCIDENTE_LIQUIDACION
            WHERE id_liquidacion = {placeholder}
        )
        WHERE id_liquidacion = {placeholder}
        RETURNING valor_incidentes
    """, (id_liquidacion, id_liquidacion))
    
    result = cursor.fetchone()
    conn.commit()
    return result[0] if result else 0
```

### 3. Backend Service Updates

#### 3.1 `servicio_incidente_liquidacion.py`

**En `asociar_incidente()` (después de línea 176), AGREGAR:**

```python
# 9b. Actualizar observaciones con ID del incidente (reemplazo completo)
liquidacion.observaciones = f"Inc #{id_incidente}"
self.repositorio_liquidacion.actualizar(liquidacion)
```

**En `desasociar_incidente()` (después de línea 272), AGREGAR:**

```python
# 5b. Actualizar observaciones (reemplazo completo)
if liquidacion:
    liquidacion.observaciones = ""
    self.repositorio_liquidacion.actualizar(liquidacion)
```

### 4. Frontend State Updates

#### 4.1 `liquidaciones_state.py` - `open_edit_modal()` (~línea 617)

AGREGAR en `form_data`:
```python
"valor_incidentes": str(liquidacion.get("valor_incidentes", 0)),
```

#### 4.2 `liquidaciones_state.py` - `open_detail_modal()` (después de línea 683)

AGREGAR:
```python
l_fmt["valor_incidentes_view"] = format_currency(
    liquidacion.get("valor_incidentes", 0)
)
```

### 5. Frontend Component Updates

#### 5.1 `liquidacion_edit_form.py` (línea 129-133)

REEMPLAZAR el campo "Incidentes" actual:

```python
# NUEVO (CORRECTO):
form_field_editable(
    "Incidentes (Plan Pago)",
    "valor_incidentes",
    LiquidacionesState.form_data["valor_incidentes"],
),
```

#### 5.2 `liquidacion_detail_modal.py` (después de línea 189)

AGREGAR nueva fila:
```python
info_row(
    "Incidentes (Plan Pago):",
    LiquidacionesState.liquidacion_actual["valor_incidentes_view"],
),
```

## Files to Modify

| File | Change Type |
|------|-------------|
| `scripts/migration_007_triggers_valor_incidentes.sql` | NEW |
| `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py` | MODIFY |
| `src/aplicacion/servicios/servicio_incidente_liquidacion.py` | MODIFY |
| `src/presentacion_reflex/state/liquidaciones_state.py` | MODIFY |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_edit_form.py` | MODIFY |
| `src/presentacion_reflex/components/liquidaciones/liquidacion_detail_modal.py` | MODIFY |

## Testing Strategy

1. **Unit Tests:**
   - Verify trigger calculates `valor_incidentes` correctly on INSERT
   - Verify trigger recalculates on DELETE
   - Verify `observaciones` is set on association
   - Verify `observaciones` is cleared on disassociation

2. **Integration Tests:**
   - Complete flow: Create incident → Create plan → Create liquidation → Associate → Verify UI shows correct values
   - Verify `neto_a_pagar` calculation includes `valor_incidentes`

3. **Manual Testing:**
   - Open liquidation detail → Verify "Incidentes (Plan Pago)" shows $70,000
   - Open edit form → Verify "Incidentes (Plan Pago)" field shows 70000
   - Verify "Observaciones" shows "Inc #52"
