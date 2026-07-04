# Contract: CuotaIncidente Operations

**Date**: 2026-06-30
**Feature**: 003-integracion-incidentes-liquidaciones

## Overview

This contract defines the API and validation rules for managing installments (cuotas) within a payment plan.

## Operations

### CreateCuotasFromPlan

**Description**: Creates all installments for a payment plan

**Input Parameters**:
```python
{
    "id_plan_pago": int,           # Required: Payment plan ID
    "creado_por": str              # Required: User who creates
}
```

**Business Rules**:
1. Plan must exist and have `estado = 'Activo'`
2. Installments must be created sequentially (1, 2, 3...)
3. Each installment's `valor_cuota` = plan's `valor_cuota`
4. Total of all installments must equal plan's `total_plan`

**Output**:
```python
{
    "success": bool,
    "data": [                      # List of created installments
        {
            "id_cuota": int,
            "numero_cuota": int,
            "valor_cuota": int,
            "id_liquidacion": None,
            "estado_pago": "Pendiente"
        }
    ],
    "error": str | None
}
```

**Error Codes**:
- `PLAN_NO_ENCONTRADO`: Plan does not exist
- `PLAN_NO_ACTIVO`: Plan is not in 'Activo' state
- `CUOTAS_YA_EXISTEN`: Installments already exist for this plan

---

### GetCuotasByPlan

**Description**: Retrieves all installments for a payment plan

**Input Parameters**:
```python
{
    "id_plan_pago": int            # Required: Payment plan ID
}
```

**Output**:
```python
{
    "success": bool,
    "data": [
        {
            "id_cuota": int,
            "numero_cuota": int,
            "valor_cuota": int,
            "id_liquidacion": int | None,
            "estado_pago": str,
            "liquidacion_info": {   # Optional: If liquidation exists
                "id_liquidacion": int,
                "periodo": str,
                "estado_liquidacion": str,
                "neto_a_pagar": int
            } | None
        }
    ],
    "error": str | None
}
```

---

### AsociarCuotaALiquidacion

**Description**: Associates an installment with a liquidation

**Input Parameters**:
```python
{
    "id_cuota": int,               # Required: Installment ID
    "id_liquidacion": int,         # Required: Liquidation ID
    "asociado_por": str            # Required: User who associates
}
```

**Business Rules**:
1. Installment must exist and have `estado_pago = 'Pendiente'`
2. Liquidation must exist and have `estado_liquidacion` in ['En Proceso', 'Aprobada']
3. Liquidation must NOT be in 'Anulada' or 'Pagada' state
4. Total installments for this liquidation must not exceed liquidation's `valor_incidentes`

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_cuota": int,
        "numero_cuota": int,
        "valor_cuota": int,
        "id_liquidacion": int,
        "estado_pago": "Asociada"
    },
    "error": str | None
}
```

**Error Codes**:
- `CUOTA_NO_ENCONTRADA`: Installment does not exist
- `CUOTA_YA_ASOCIADA`: Installment already has a liquidation
- `LIQUIDACION_NO_ENCONTRADA`: Liquidation does not exist
- `LIQUIDACION_NO_CALIFICADA`: Liquidation status does not allow association
- `LIMITE_EXCEDIDO`: Total installments exceed liquidation limit

---

### DesasociarCuotaDeLiquidacion

**Description**: Removes association between installment and liquidation

**Input Parameters**:
```python
{
    "id_cuota": int,               # Required: Installment ID
    "desasociado_por": str,        # Required: User who dissociates
    "justificacion": str           # Required: Justification
}
```

**Business Rules**:
1. Installment must exist and have `estado_pago = 'Asociada'`
2. Liquidation must NOT be in 'Pagada' state

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_cuota": int,
        "numero_cuota": int,
        "valor_cuota": int,
        "id_liquidacion": None,
        "estado_pago": "Pendiente"
    },
    "error": str | None
}
```

**Error Codes**:
- `CUOTA_NO_ENCONTRADA`: Installment does not exist
- `CUOTA_NO_ASOCIADA`: Installment is not associated
- `LIQUIDACION_PAGADA`: Cannot dissociate from paid liquidation

---

### ActualizarEstadoCuota

**Description**: Updates installment status based on liquidation status

**Input Parameters**:
```python
{
    "id_cuota": int,               # Required: Installment ID
    "nuevo_estado": str,           # Required: New status
    "modificado_por": str          # Required: User who updates
}
```

**Business Rules**:
1. Installment must exist
2. Status transition must be valid:
   - Pendiente → Asociada (when liquidation is associated)
   - Asociada → Pagada (when liquidation is paid)
   - Pagada → Asociada (when liquidation payment is reversed)
   - Asociada → Pendiente (when liquidation is dissociated)

**Output**:
```python
{
    "success": bool,
    "data": {...},                 # Updated installment data
    "error": str | None
}
```

**Error Codes**:
- `CUOTA_NO_ENCONTRADA`: Installment does not exist
- `TRANSICION_INVALIDA`: Invalid status transition

---

### GetCuotasPendientes

**Description**: Gets all installments without liquidation association

**Input Parameters**:
```python
{
    "id_plan_pago": int            # Required: Payment plan ID
}
```

**Output**: Same as GetCuotasByPlan (filtered to only Pendiente status)

---

### GetCuotasByLiquidacion

**Description**: Gets all installments associated with a specific liquidation

**Input Parameters**:
```python
{
    "id_liquidacion": int          # Required: Liquidation ID
}
```

**Output**: Same as GetCuotasByPlan (filtered by liquidation)

## Validation Rules Summary

| Rule | Validation | Error Code |
|------|------------|------------|
| Installment exists | SELECT COUNT(*) > 0 | CUOTA_NO_ENCONTRADA |
| Installment pending | estado_pago = 'Pendiente' | CUOTA_YA_ASOCIADA |
| Liquidation exists | SELECT COUNT(*) > 0 | LIQUIDACION_NO_ENCONTRADA |
| Liquidation qualified | estado_liquidacion IN ('En Proceso', 'Aprobada') | LIQUIDACION_NO_CALIFICADA |
| No limit exceeded | SUM(valor_cuota) <= liquidation.valor_incidentes | LIMITE_EXCEDIDO |
| Valid transition | From estado → To estado is allowed | TRANSICION_INVALIDA |

## Status Values

- `Pendiente`: Installment created, no liquidation associated
- `Asociada`: Installment associated with a liquidation
- `Pagada`: Associated liquidation is in 'Pagada' state

## Audit Fields

All operations must log:
- `usuario`: User performing the action
- `fecha`: Timestamp of the action
- `accion`: CREATE/ASSOCIATE/DISSOCIATE/UPDATE_STATUS
- `valores_anteriores`: Previous state (for updates)
- `valores_nuevos`: New state (for creates/updates)
- `direccion_ip`: IP address of the user
- `id_sesion`: Session ID
