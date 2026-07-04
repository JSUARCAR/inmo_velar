# Contract: IncidenteLiquidacion Operations

**Date**: 2026-06-30
**Feature**: 003-integracion-incidentes-liquidaciones

## Overview

This contract defines the API and validation rules for managing the relationship between incidents and liquidations.

## Operations

### AsociarIncidenteALiquidacion

**Description**: Associates an incident with a liquidation for discount

**Input Parameters**:
```python
{
    "id_incidente": int,           # Required: Incident ID
    "id_liquidacion": int,         # Required: Liquidation ID
    "numero_cuota": int,           # Required: Installment number
    "valor_descuento": int,        # Required: Discount value
    "asociado_por": str            # Required: User who associates
}
```

**Business Rules**:
1. Incident must exist and have `estado` in ['Aprobado', 'En Reparacion', 'Finalizado']
2. Incident must have `estado_pago` != 'Pagado'
3. Incident must have an active payment plan
4. Liquidation must exist and have `estado_liquidacion` in ['En Proceso', 'Aprobada']
5. Combination `(id_incidente, id_liquidacion, numero_cuota)` must be unique
6. `valor_descuento` must be > 0
7. Total discounts for this liquidation must not exceed liquidation's `neto_a_pagar`

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_relacion": int,
        "id_incidente": int,
        "id_liquidacion": int,
        "numero_cuota": int,
        "valor_descuento": int,
        "asociado_por": str,
        "fecha_asociacion": str
    },
    "error": str | None
}
```

**Error Codes**:
- `INCIDENTE_NO_ENCONTRADO`: Incident does not exist
- `INCIDENTE_NO_CALIFICADO`: Incident status does not allow association
- `INCIDENTE_PAGADO`: Incident is already fully paid
- `PLAN_NO_EXISTE`: No active payment plan for incident
- `LIQUIDACION_NO_ENCONTRADA`: Liquidation does not exist
- `LIQUIDACION_NO_CALIFICADA`: Liquidation status does not allow association
- `DUPLICADO`: Combination already exists
- `VALOR_INVALIDO`: valor_descuento <= 0
- `LIMITE_EXCEDIDO`: Total discounts exceed liquidation limit

---

### DesasociarIncidenteDeLiquidacion

**Description**: Removes association between incident and liquidation

**Input Parameters**:
```python
{
    "id_relacion": int,            # Required: Relationship ID
    "desasociado_por": str,        # Required: User who dissociates
    "justificacion": str           # Required: Justification
}
```

**Business Rules**:
1. Relationship must exist
2. Liquidation must NOT be in 'Pagada' state
3. Liquidation must NOT be in 'Anulada' state

**Output**:
```python
{
    "success": bool,
    "data": {...},                 # Removed relationship data
    "error": str | None
}
```

**Error Codes**:
- `RELACION_NO_ENCONTRADA`: Relationship does not exist
- `LIQUIDACION_PAGADA`: Cannot dissociate from paid liquidation
- `LIQUIDACION_ANULADA`: Cannot dissociate from annulled liquidation

---

### GetIncidentesByLiquidacion

**Description**: Gets all incidents associated with a liquidation

**Input Parameters**:
```python
{
    "id_liquidacion": int          # Required: Liquidation ID
}
```

**Output**:
```python
{
    "success": bool,
    "data": [
        {
            "id_relacion": int,
            "id_incidente": int,
            "numero_cuota": int,
            "valor_descuento": int,
            "asociado_por": str,
            "fecha_asociacion": str,
            "incidente_info": {
                "id_incidente": int,
                "id_propiedad": int,
                "costo_incidente": int,
                "estado": str,
                "estado_pago": str
            }
        }
    ],
    "error": str | None
}
```

---

### GetLiquidacionesByIncidente

**Description**: Gets all liquidations associated with an incident

**Input Parameters**:
```python
{
    "id_incidente": int            # Required: Incident ID
}
```

**Output**:
```python
{
    "success": bool,
    "data": [
        {
            "id_relacion": int,
            "id_liquidacion": int,
            "numero_cuota": int,
            "valor_descuento": int,
            "asociado_por": str,
            "fecha_asociacion": str,
            "liquidacion_info": {
                "id_liquidacion": int,
                "periodo": str,
                "estado_liquidacion": str,
                "neto_a_pagar": int,
                "valor_incidentes": int
            }
        }
    ],
    "error": str | None
}
```

---

### CalcularEstadoPagoIncidente

**Description**: Calculates and updates the payment status of an incident

**Input Parameters**:
```python
{
    "id_incidente": int            # Required: Incident ID
}
```

**Business Rules**:
1. Incident must exist
2. Status calculation:
   - If no liquidations associated → 'Pendiente'
   - If ALL associated liquidations have `estado_liquidacion = 'Pagada'` → 'Pagado'
   - If SOME but not ALL → 'Parcialmente Pagado'
   - If NONE are 'Pagada' → 'Pendiente'

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_incidente": int,
        "estado_pago_anterior": str,
        "estado_pago_nuevo": str,
        "num_liquidaciones": int,
        "num_pagadas": int
    },
    "error": str | None
}
```

---

### ActualizarValorIncidentesLiquidacion

**Description**: Updates the total incident value for a liquidation

**Input Parameters**:
```python
{
    "id_liquidacion": int,         # Required: Liquidation ID
    "modificado_por": str          # Required: User who updates
}
```

**Business Rules**:
1. Liquidation must exist
2. Calculate total: SUM(valor_descuento) from all associated incidents
3. Update `valor_incidentes` field
4. Recalculate `neto_a_pagar` = `total_ingresos` - `total_egresos` - `valor_incidentes`

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_liquidacion": int,
        "valor_incidentes_anterior": int,
        "valor_incidentes_nuevo": int,
        "neto_a_pagar_anterior": int,
        "neto_a_pagar_nuevo": int
    },
    "error": str | None
}
```

---

### GetResumenDescuentosIncidente

**Description**: Gets summary of all discounts applied to an incident

**Input Parameters**:
```python
{
    "id_incidente": int            # Required: Incident ID
}
```

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_incidente": int,
        "costo_incidente": int,
        "total_descuentos": int,
        "saldo_pendiente": int,
        "num_liquidaciones": int,
        "detalles": [
            {
                "id_liquidacion": int,
                "periodo": str,
                "valor_descuento": int,
                "estado_liquidacion": str
            }
        ]
    },
    "error": str | None
}
```

## Validation Rules Summary

| Rule | Validation | Error Code |
|------|------------|------------|
| Incident exists | SELECT COUNT(*) > 0 | INCIDENTE_NO_ENCONTRADO |
| Incident qualified | estado IN ('Aprobado', 'En Reparacion', 'Finalizado') | INCIDENTE_NO_CALIFICADO |
| Incident not paid | estado_pago != 'Pagado' | INCIDENTE_PAGADO |
| Plan exists | SELECT COUNT(*) > 0 WHERE estado = 'Activo' | PLAN_NO_EXISTE |
| Liquidation exists | SELECT COUNT(*) > 0 | LIQUIDACION_NO_ENCONTRADA |
| Liquidation qualified | estado_liquidacion IN ('En Proceso', 'Aprobada') | LIQUIDACION_NO_CALIFICADA |
| No duplicate | UNIQUE(id_incidente, id_liquidacion, numero_cuota) | DUPLICADO |
| Valid discount | valor_descuento > 0 | VALOR_INVALIDO |
| No limit exceeded | SUM(valor_descuento) <= liquidation.neto_a_pagar | LIMITE_EXCEDIDO |

## Status Values for Incident Payment Status

- `Pendiente`: No liquidations associated or none paid
- `Parcialmente Pagado`: Some but not all liquidations paid
- `Pagado`: All associated liquidations are paid

## Audit Fields

All operations must log:
- `usuario`: User performing the action
- `fecha`: Timestamp of the action
- `accion`: ASSOCIATE/DISSOCIATE/CALCULATE_STATUS/UPDATE_VALUE
- `valores_anteriores`: Previous state (for updates)
- `valores_nuevos`: New state (for creates/updates)
- `direccion_ip`: IP address of the user
- `id_sesion`: Session ID
