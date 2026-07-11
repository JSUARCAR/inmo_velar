# Data Model: Corrección valor_incidentes en Reportes

**Date**: 2026-07-11
**Feature**: 044-fix-valor-incidentes-reportes

## Entity: Liquidaciones (existente - sin cambios estructurales)

La entidad `Liquidaciones` ya contiene el campo `valor_incidentes`. No se requieren migraciones de esquema.

### Campos relevantes

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `ID_LIQUIDACION` | SERIAL PK | - | Identificador único |
| `VALOR_INCIDENTES` | INTEGER | 0 | Valor pre-calculado de incidentes asociados |
| `TOTAL_INGRESOS` | INTEGER | 0 | Suma de canon + otros ingresos |
| `TOTAL_EGRESOS` | INTEGER | 0 | Suma de comisión + IVA + gastos + predial + otros |
| `NETO_A_PAGAR` | INTEGER | 0 | TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES |

### Relaciones

```
LIQUIDACIONES (1) ←→ (N) INCIDENTE_LIQUIDACION (N) ←→ (1) INCIDENTES
```

- `valor_incidentes` es la suma de `VALOR_DESCUENTO` de todos los incidentes asociados
- Se recalcula automáticamente al asociar/desasociar incidentes

## Entity: Reportes (consultas SQL a modificar)

### Reporte de Liquidaciones (`obtener_reporte_liquidaciones`)

**Consulta actual** (repositorio_reportes.py:259-271):
```sql
SELECT 
    l.ID_LIQUIDACION, l.ID_CONTRATO_M,
    p.DIRECCION_PROPIEDAD AS "Direccion_Predio",
    per_prop.NOMBRE_COMPLETO AS "Nombre_Propietario",
    per_ase.NOMBRE_COMPLETO AS "Nombre_Asesor",
    l.PERIODO, l.FECHA_GENERACION, l.CANON_BRUTO, l.OTROS_INGRESOS,
    l.TOTAL_INGRESOS, l.COMISION_PORCENTAJE, l.COMISION_MONTO,
    l.IVA_COMISION, l.IMPUESTO_4X1000, l.SEGURO_MONTO as "Seguro_Arrendamiento",
    l.GASTOS_ADMINISTRACION, l.GASTOS_SERVICIOS, l.GASTOS_REPARACIONES, l.PAGO_PREDIAL,
    l.OTROS_EGRESOS, l.TOTAL_EGRESOS, l.NETO_A_PAGAR,
    l.ESTADO_LIQUIDACION, l.FECHA_PAGO, l.METODO_PAGO,
    l.REFERENCIA_PAGO, l.OBSERVACIONES
-- ❌ FALTA: l.VALOR_INCIDENTES
```

**Consulta corregida**:
```sql
SELECT 
    l.ID_LIQUIDACION, l.ID_CONTRATO_M,
    p.DIRECCION_PROPIEDAD AS "Direccion_Predio",
    per_prop.NOMBRE_COMPLETO AS "Nombre_Propietario",
    per_ase.NOMBRE_COMPLETO AS "Nombre_Asesor",
    l.PERIODO, l.FECHA_GENERACION, l.CANON_BRUTO, l.OTROS_INGRESOS,
    l.TOTAL_INGRESOS, l.COMISION_PORCENTAJE, l.COMISION_MONTO,
    l.IVA_COMISION, l.IMPUESTO_4X1000, l.SEGURO_MONTO as "Seguro_Arrendamiento",
    l.GASTOS_ADMINISTRACION, l.GASTOS_SERVICIOS, l.GASTOS_REPARACIONES, l.PAGO_PREDIAL,
    l.OTROS_EGRESOS, l.TOTAL_EGRESOS, 
    COALESCE(l.VALOR_INCIDENTES, 0) AS "Valor_Incidentes",  -- ✅ AGREGADO
    l.NETO_A_PAGAR,
    l.ESTADO_LIQUIDACION, l.FECHA_PAGO, l.METODO_PAGO,
    l.REFERENCIA_PAGO, l.OBSERVACIONES
```

### Reporte Financiero Consolidado (`obtener_reporte_consolidado`)

**Consulta actual** (repositorio_reportes.py:601-682):
- ❌ No incluye `VALOR_INCIDENTES` en el SELECT
- ❌ Cálculo de `NETO_A_PAGAR` (línea 671-678) no descuenta `VALOR_INCIDENTES`

**Consulta corregida**:
```sql
-- Agregar después de TOTAL_EGRESOS (sección 8):
COALESCE(l.VALOR_INCIDENTES, 0) AS "VALOR_INCIDENTES",

-- Corregir cálculo de NETO_A_PAGAR (sección 9):
(COALESCE(l.TOTAL_INGRESOS, 0) - 
 (COALESCE(l.COMISION_MONTO, 0) + 
  COALESCE(l.IVA_COMISION, 0) + 
  COALESCE(l.GASTOS_ADMINISTRACION, 0) + 
  COALESCE(l.GASTOS_SERVICIOS, 0) + 
  COALESCE(l.GASTOS_REPARACIONES, 0) + 
  COALESCE(l.PAGO_PREDIAL, 0) + 
  COALESCE(l.OTROS_EGRESOS, 0) +
  COALESCE(l.VALOR_INCIDENTES, 0))) AS "NETO_A_PAGAR",  -- ✅ CORREGIDO
```

### Headers del Reporte Consolidado

**Constante actual** (servicio_reportes.py:6-62):
- 46 headers, no incluye `VALOR_INCIDENTES`

**Constante corregida**:
```python
HEADERS_REPORTE_CONSOLIDADO: List[str] = [
    # ... headers existentes ...
    # 8. Composición Financiera (Egresos y Retenciones)
    "COMISION_PORCENTAJE_ASESOR",
    "COMISION_MONTO_ASESOR",
    "IVA_COMISION",
    "GASTOS_ADMINISTRACION",
    "GASTOS_SERVICIOS",
    "GASTOS_REPARACIONES",
    "PAGO_PREDIAL",
    "OTROS_EGRESOS",
    "TOTAL_EGRESOS",
    "VALOR_INCIDENTES",  # ✅ AGREGADO
    # 9. Cierre Financiero (Liquidación)
    "NETO_A_PAGAR",
    # ... resto de headers ...
]
```

## Validation Rules

| Regla | Descripción |
|-------|-------------|
| VALOR_INCIDENTES >= 0 | Valor no puede ser negativo (por diseño) |
| VALOR_INCIDENTES <= TOTAL_INGRESOS | No puede exceder el total de ingresos |
| NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES | Fórmula de cierre financiero |
| NULL → 0 | Valores NULL se tratan como 0 en presentación |

## State Transitions

No aplica - el campo `valor_incidentes` es un valor calculado que no tiene transiciones de estado propias. Se actualiza automáticamente cuando:
1. Se crea una nueva liquidación (suma de cuotas pendientes de incidentes)
2. Se asocia un incidente a una liquidación
3. Se desasocia un incidente de una liquidación
