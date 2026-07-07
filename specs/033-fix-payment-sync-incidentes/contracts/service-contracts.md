# Service Contracts: Fix Payment Status Synchronization

**Date**: 2026-07-07
**Feature**: 033-fix-payment-sync-incidentes

## Overview

This document defines the service interfaces for the payment status synchronization feature. Since this is an internal web application, contracts define the internal service layer interfaces rather than external APIs.

## ServicioFinanciero

### marcar_liquidacion_pagada()

**Purpose**: Mark a liquidación as paid and update associated incident cuotas

**Input**:
```python
{
    "id_liquidacion": int,       # Required: Liquidación ID
    "fecha_pago": str,           # Required: Payment date (YYYY-MM-DD)
    "metodo_pago": str,          # Required: Payment method
    "referencia_pago": str,      # Required: Payment reference
    "usuario_sistema": str       # Required: System user
}
```

**Output**:
```python
None  # Raises exception on error
```

**Side Effects**:
1. Updates `LIQUIDACIONES.ESTADO_LIQUIDACION` to 'Pagada'
2. Updates `CUOTA_INCIDENTE.ESTADO_PAGO` to 'Pagada' for all associated cuotas
3. **NEW**: Triggers `ServicioEstadoPagoAutomatico.actualizar_estado_pago_por_liquidacion()`

**Error Handling**:
- Raises `ValueError` if liquidación not found
- Raises `Exception` on database errors

### marcar_liquidacion_propietario_pagada()

**Purpose**: Mark all approved liquidaciones for a property/period as paid

**Input**:
```python
{
    "id_propietario": int,       # Required: Property owner ID
    "periodo": str,              # Required: Period (YYYY-MM)
    "fecha_pago": str,           # Required: Payment date
    "metodo_pago": str,          # Required: Payment method
    "referencia_pago": str,      # Required: Payment reference
    "usuario_sistema": str       # Required: System user
}
```

**Output**:
```python
int  # Number of liquidaciones affected
```

**Side Effects**:
1. For each liquidación with ESTADO_LIQUIDACION = 'Aprobada':
   - Calls `marcar_liquidacion_pagada()`
2. **NEW**: Each call triggers incident status sync

### reversar_liquidacion()

**Purpose**: Reverse a liquidación payment (Pagada → En Proceso)

**Input**:
```python
{
    "id_liquidacion": int,       # Required: Liquidación ID
    "usuario_sistema": str       # Required: System user
}
```

**Output**:
```python
None  # Raises exception on error
```

**Side Effects**:
1. Updates `LIQUIDACIONES.ESTADO_LIQUIDACION` to 'En Proceso'
2. **NEW**: Triggers `ServicioEstadoPagoAutomatico.revertir_estado_pago_por_liquidacion()`

## ServicioEstadoPagoAutomatico

### actualizar_estado_pago_por_liquidacion()

**Purpose**: Update incident payment status when a liquidación changes state

**Input**:
```python
{
    "id_liquidacion": int,       # Required: Liquidación ID
    "usuario": str               # Required: User performing action
}
```

**Output**:
```python
{
    "success": bool,
    "data": {
        "incidentes_actualizados": int
    },
    "message": str
}
```

**Side Effects**:
1. For each incident associated with the liquidación:
   - Calls `recalcular_estado_pago_incidente()`

**Error Handling**:
- Returns `{"success": False, "error": "ERROR_INESPERADO"}` on failure

### recalcular_estado_pago_incidente()

**Purpose**: Recalculate a single incident's payment status

**Input**:
```python
{
    "id_incidente": int,         # Required: Incident ID
    "usuario": str               # Required: User performing action
}
```

**Output**:
```python
{
    "success": bool,
    "data": {
        "estado_pago": str  # "Pendiente" | "Parcialmente Pagado" | "Pagado"
    }
}
```

**Business Logic**:
```python
if not plan:
    estado_pago = "Pendiente"
elif total_con_liq == 0:
    estado_pago = "Pendiente"
elif cuotas_pagadas == total_con_liq:
    estado_pago = "Pagado"
elif cuotas_pagadas > 0:
    estado_pago = "Parcialmente Pagado"
else:
    estado_pago = "Pendiente"
```

**Side Effects**:
1. Updates `INCIDENTE.ESTADO_PAGO` if changed

### revertir_estado_pago_por_liquidacion()

**Purpose**: Update incident payment status when a liquidación payment is reversed

**Input**:
```python
{
    "id_liquidacion": int,       # Required: Liquidación ID
    "usuario": str               # Required: User performing action
}
```

**Output**:
```python
{
    "success": bool,
    "data": {
        "incidentes_actualizados": int
    },
    "message": str
}
```

**Side Effects**:
1. For each incident associated with the liquidación:
   - Calls `recalcular_estado_pago_incidente()`

## RepositorioCuotaPostgres

### obtener_por_liquidacion()

**Purpose**: Get all cuotas associated with a liquidación

**Input**:
```python
{
    "id_liquidacion": int       # Required: Liquidación ID
}
```

**Output**:
```python
List[CuotaIncidente]  # List of cuota entities
```

**SQL**:
```sql
SELECT * FROM CUOTA_INCIDENTE 
WHERE ID_LIQUIDACION = %s 
ORDER BY NUMERO_CUOTA
```

### contar_estado_liquidaciones_por_plan()

**Purpose**: Count cuotas with liquidations and paid cuotas for a plan

**Input**:
```python
{
    "id_plan_pago": int         # Required: Payment plan ID
}
```

**Output**:
```python
tuple[int, int]  # (total_cuotas_con_liq, total_cuotas_pagadas)
```

**SQL**:
```sql
SELECT 
    COUNT(c.ID_CUOTA) as total_con_liq,
    SUM(CASE WHEN l.ESTADO_LIQUIDACION = 'Pagada' THEN 1 ELSE 0 END) as total_pagadas
FROM CUOTA_INCIDENTE c
JOIN LIQUIDACIONES l ON c.ID_LIQUIDACION = l.ID_LIQUIDACION
WHERE c.ID_PLAN_PAGO = %s
```

## UI State Contracts

### LiquidacionesState

#### marcar_como_pagada()

**Purpose**: Handle single payment registration from UI

**Input**:
```python
{
    "form_data": {
        "id_liquidacion": int,
        "fecha_pago": str,
        "metodo_pago": str,
        "referencia_pago": str
    }
}
```

**Side Effects**:
1. Calls `ServicioFinanciero.marcar_liquidacion_pagada()`
2. **NEW**: Calls `ServicioEstadoPagoAutomatico.actualizar_estado_pago_por_liquidacion()`
3. Updates UI state: `show_payment_modal = False`
4. Reloads liquidaciones list

#### marcar_como_pagada_masiva()

**Purpose**: Handle bulk payment registration from UI

**Input**:
```python
{
    "form_data": {
        "id_propietario": int,
        "periodo": str,
        "fecha_pago": str,
        "metodo_pago": str,
        "referencia_pago": str
    }
}
```

**Side Effects**:
1. Calls `ServicioFinanciero.marcar_liquidacion_propietario_pagada()`
2. **NEW**: Each liquidación triggers incident status sync
3. Updates UI state: `show_payment_modal = False`
4. Reloads liquidaciones list

#### confirmar_reversar()

**Purpose**: Handle payment reversal from UI

**Input**:
```python
{
    "id_liquidacion": int
}
```

**Side Effects**:
1. Calls `ServicioFinanciero.reversar_liquidacion()`
2. **NEW**: Calls `ServicioEstadoPagoAutomatico.revertir_estado_pago_por_liquidacion()`
3. Updates UI state: `show_reverse_confirm = False`
4. Reloads liquidaciones list
