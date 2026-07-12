# Data Model: Agregar Columna MONTO COMISIÓN a Liquidaciones

**Date**: 2026-07-11
**Feature**: 001-add-monto-comision-column

## Entities

### Liquidacion (existente, sin cambios en BD)

La entidad `Liquidacion` ya existe en `src/dominio/entidades/liquidacion.py`. Los campos relevantes para esta feature:

| Campo | Tipo | Descripción | Default |
|-------|------|-------------|---------|
| `comision_monto` | `int` | Monto de comisión en pesos colombianos | `0` |
| `comision_porcentaje` | `int` | Porcentaje de comisión (base 10000, ej. 1500 = 15.00%) | `0` |
| `canon_bruto` | `int` | Canon de mandato en pesos colombianos | `0` |

**Relationship**: `comision_monto = canon_bruto * (comision_porcentaje / 10000)`

### LiquidacionDict (modelos de estado, cambios necesarios)

El Pydantic model `LiquidacionDict` en `liquidaciones_state.py` necesita los siguientes campos adicionales:

```python
# Campos existentes (no cambiar)
canon: float
canon_view: str
iva_comision: float
iva_comision_view: str

# Campos nuevos a agregar
comision_monto: float           # Monto formateado para cálculos
comision_monto_view: str        # "$1.500" para visualización
comision_porcentaje: float      # Porcentaje para tooltip (ej. 15.0)
```

### Repository Query Changes

#### listar_paginado (individual)

**SELECT actual** (parcial):
```sql
SELECT l.ID_LIQUIDACION, l.PERIODO, l.CANON_BRUTO, l.IVA_COMISION, ...
```

**SELECT actualizado**:
```sql
SELECT l.ID_LIQUIDACION, l.PERIODO, l.CANON_BRUTO, l.COMISION_MONTO, l.COMISION_PORCENTAJE, l.IVA_COMISION, ...
```

**Sort whitelist**: Agregar `"comision_monto"` a la lista de columnas ordenables.

**Result dict**: Agregar `"comision_monto"` y `"comision_porcentaje"` al diccionario de resultado.

#### listar_agrupadas_por_propietario_paginado (agrupada)

**SELECT actual** (parcial):
```sql
SUM(l.CANON_BRUTO) AS canon, SUM(l.IVA_COMISION) AS iva_comision, ...
```

**SELECT actualizado**:
```sql
SUM(l.CANON_BRUTO) AS canon, SUM(l.COMISION_MONTO) AS comision_monto, SUM(l.IVA_COMISION) AS iva_comision, ...
```

**Sort whitelist**: Agregar `"comision_monto"` a la lista de columnas ordenables.

## Validation Rules

| Rule | Source | Behavior |
|------|--------|----------|
| `comision_monto >= 0` | Domain entity | Valores negativos no permitidos |
| `comision_porcentaje 0-10000` | Domain entity | Base 10000 (0.00% a 100.00%) |
| NULL → $0 | Clarification Q1 | Sin distinción visual |
| Formato COP | Clarification Q2 | `$X.XXX.XXX` sin decimales |
