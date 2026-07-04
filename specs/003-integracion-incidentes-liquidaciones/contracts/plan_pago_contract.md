# Contract: PlanPagoIncidente Operations

**Date**: 2026-06-30
**Feature**: 003-integracion-incidentes-liquidaciones

## Overview

This contract defines the API and validation rules for creating, reading, updating, and deleting payment plans for incidents.

## Operations

### CreatePlanPago

**Description**: Creates a new payment plan for an incident

**Input Parameters**:
```python
{
    "id_incidente": int,           # Required: Incident ID
    "num_cuotas": int,             # Required: Number of installments (>= 1)
    "valor_cuota": int,            # Required: Value per installment (> 0)
    "creado_por": str              # Required: User who creates the plan
}
```

**Business Rules**:
1. Incident must exist and have `estado` in ['Aprobado', 'En Reparacion', 'Finalizado']
2. Incident must NOT have an existing active plan (`estado = 'Activo'`)
3. `num_cuotas` must be >= 1
4. `valor_cuota` must be > 0
5. `total_plan` = `num_cuotas * valor_cuota` (auto-calculated)

**Output**:
```python
{
    "success": bool,
    "data": {
        "id_plan_pago": int,
        "id_incidente": int,
        "num_cuotas": int,
        "valor_cuota": int,
        "total_plan": int,
        "estado": "Activo",
        "creado_por": str,
        "created_at": str
    },
    "error": str | None
}
```

**Error Codes**:
- `INCIDENTE_NO_ENCONTRADO`: Incident does not exist
- `INCIDENTE_NO_CALIFICADO`: Incident status does not allow payment plans
- `PLAN_YA_EXISTE`: Active plan already exists for this incident
- `CUOTAS_INVALIDAS`: num_cuotas < 1
- `VALOR_INVALIDO`: valor_cuota <= 0

---

### GetPlanPago

**Description**: Retrieves a payment plan by ID

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
    "data": {
        "id_plan_pago": int,
        "id_incidente": int,
        "num_cuotas": int,
        "valor_cuota": int,
        "total_plan": int,
        "estado": str,
        "creado_por": str,
        "created_at": str,
        "updated_at": str | None,
        "cuotas": [                 # Associated installments
            {
                "id_cuota": int,
                "numero_cuota": int,
                "valor_cuota": int,
                "id_liquidacion": int | None,
                "estado_pago": str
            }
        ]
    },
    "error": str | None
}
```

---

### GetPlanPagoByIncidente

**Description**: Retrieves the active payment plan for a specific incident

**Input Parameters**:
```python
{
    "id_incidente": int            # Required: Incident ID
}
```

**Output**: Same as GetPlanPago

**Error Codes**:
- `INCIDENTE_NO_ENCONTRADO`: Incident does not exist
- `PLAN_NO_ENCONTRADO`: No active plan found for this incident

---

### UpdatePlanPago

**Description**: Updates an existing payment plan (only if no installments are associated)

**Input Parameters**:
```python
{
    "id_plan_pago": int,           # Required: Payment plan ID
    "num_cuotas": int | None,      # Optional: New number of installments
    "valor_cuota": int | None,     # Optional: New value per installment
    "modificado_por": str          # Required: User who modifies
}
```

**Business Rules**:
1. Plan must exist and have `estado = 'Activo'`
2. No installments can have `id_liquidacion` not NULL
3. If updating `num_cuotas`, must recalculate `total_plan`
4. If updating `valor_cuota`, must recalculate `total_plan`
5. All installments must be updated to match new plan

**Output**:
```python
{
    "success": bool,
    "data": {...},                 # Updated plan data
    "error": str | None
}
```

**Error Codes**:
- `PLAN_NO_ENCONTRADO`: Plan does not exist
- `PLAN_NO_MODIFICABLE`: Plan has associated installments
- `CUOTAS_INVALIDAS`: num_cuotas < 1
- `VALOR_INVALIDO`: valor_cuota <= 0

---

### CancelPlanPago

**Description**: Cancels a payment plan (only if no installments are associated)

**Input Parameters**:
```python
{
    "id_plan_pago": int,           # Required: Payment plan ID
    "cancelado_por": str,          # Required: User who cancels
    "justificacion": str           # Required: Justification for cancellation
}
```

**Business Rules**:
1. Plan must exist and have `estado = 'Activo'`
2. No installments can have `id_liquidacion` not NULL

**Output**:
```python
{
    "success": bool,
    "data": {...},                 # Cancelled plan data
    "error": str | None
}
```

**Error Codes**:
- `PLAN_NO_ENCONTRADO`: Plan does not exist
- `PLAN_NO_CANCELABLE`: Plan has associated installments

---

### DeletePlanPago

**Description**: Soft-deletes a payment plan (sets estado = 'Cancelado')

**Input Parameters**: Same as CancelPlanPago

**Note**: This is equivalent to CancelPlanPago for audit purposes.

## Validation Rules Summary

| Rule | Validation | Error Code |
|------|------------|------------|
| Incident exists | SELECT COUNT(*) > 0 | INCIDENTE_NO_ENCONTRADO |
| Incident qualified | estado IN ('Aprobado', 'En Reparacion', 'Finalizado') | INCIDENTE_NO_CALIFICADO |
| No active plan | SELECT COUNT(*) = 0 WHERE estado = 'Activo' | PLAN_YA_EXISTE |
| Valid installments | num_cuotas >= 1 | CUOTAS_INVALIDAS |
| Valid value | valor_cuota > 0 | VALOR_INVALIDO |
| No associated installments | All cuotas have id_liquidacion = NULL | PLAN_NO_MODIFICABLE |

## Audit Fields

All operations must log:
- `usuario`: User performing the action
- `fecha`: Timestamp of the action
- `accion`: CREATE/UPDATE/CANCEL
- `valores_anteriores`: Previous state (for updates)
- `valores_nuevos`: New state (for creates/updates)
- `direccion_ip`: IP address of the user
- `id_sesion`: Session ID
