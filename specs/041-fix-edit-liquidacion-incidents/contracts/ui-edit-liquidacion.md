# UI Contract: Edit Liquidación Modal — Associated Incidents Display

**Feature**: 041-fix-edit-liquidacion-incidents
**Date**: 2026-07-10

## Overview

This contract defines the internal UI behavior for the Edit Liquidación modal's associated incidents display. No external API changes are involved.

## State Contract

### New State Variables on `LiquidacionesState`

```python
incidentes_asociados_liquidacion: List[Dict[str, Any]] = []
loading_incidentes_asociados: bool = False
```

### Event Handler Contract

```python
async def cargar_incidentes_asociados(self, id_liquidacion: int):
    """
    Fetches associated incidents for display in the edit modal.
    
    Input: id_liquidacion (int)
    Output: Populates incidentes_asociados_liquidacion
    
    SQL Query:
        SELECT il.*, i.DESCRIPCION_INCIDENTE, i.COSTO_INCIDENTE, 
               i.ESTADO, i.ESTADO_PAGO
        FROM INCIDENTE_LIQUIDACION il
        INNER JOIN INCIDENTES i ON il.ID_INCIDENTE = i.ID_INCIDENTE
        WHERE il.ID_LIQUIDACION = ?
        ORDER BY il.FECHA_ASOCIACION
    
    Returns: List of dicts with keys:
        - id_relacion (int)
        - id_incidente (int)
        - descripcion (str)
        - costo (int)
        - estado (str)
        - estado_pago (str)
        - valor_descuento (int)
        - numero_cuota (int)
        - fecha_asociacion (str)
    """
```

## UI Contract

### Edit Modal Sections

The edit modal (`liquidacion_edit_form`) will display:

1. **Existing fields** (unchanged):
   - Read-only: Propietario, Dirección, Canon, Contrato, Período
   - Editable: Otros Ingresos, Gastos Admin, Gastos Servicios, Incidentes (total), Pago Predial, Otros Egresos
   - Textarea: Observaciones

2. **New section**: "Incidentes Asociados" (between "Egresos Variables" and "Seleccionar Incidentes" button)
   - Show loading spinner while `loading_incidentes_asociados` is True
   - Show table with columns: ID, Descripción, Estado, Estado Pago, Valor Descuento
   - Show "No hay incidentes asociados" when list is empty
   - Table is READ-ONLY (no edit/delete actions)

3. **Existing button**: "Seleccionar Incidentes" (unchanged — opens modal to ADD new incidents)

### Display Rules

- Table rows sorted by `fecha_asociacion` ascending
- Estado displayed as badge with color coding:
  - Aprobado → blue
  - En Reparacion → orange
  - Finalizado → green
- Estado Pago displayed as badge:
  - Pendiente → red
  - Parcialmente Pagado → yellow
  - Pagado → green
- Valor Descuento formatted as currency ($X,XXX)
- After successfully associating new incidents, the table refreshes automatically
