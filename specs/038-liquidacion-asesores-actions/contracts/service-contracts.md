# Service Contracts: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Feature**: 038-liquidacion-asesores-actions
**Date**: 2026-07-08

## Service Layer Contracts

### 1. eliminar_liquidacion

```python
def eliminar_liquidacion(
    self, 
    id_liquidacion: int, 
    usuario_sistema: str
) -> dict:
    """
    Elimina lógicamente una liquidación de asesor (soft delete).
    
    Preconditions:
        - La liquidación debe existir
        - La liquidación debe estar en estado "Pendiente"
        - La liquidación no debe estar previamente eliminada
    
    Postconditions:
        - ELIMINADA se establece en TRUE
        - UPDATED_AT y UPDATED_BY se actualizan
        - Se registra en auditoría
    
    Args:
        id_liquidacion: ID de la liquidación a eliminar
        usuario_sistema: Usuario que ejecuta la acción
    
    Returns:
        dict: {"exitosa": bool, "mensaje": str}
    
    Raises:
        ValueError: Si la liquidación no está en estado Pendiente
        ValueError: Si la liquidación no existe
    """
```

### 2. reversar_liquidacion

```python
def reversar_liquidacion(
    self, 
    id_liquidacion: int, 
    motivo: str,
    usuario_sistema: str
) -> dict:
    """
    Revierte el estado de una liquidación de asesor.
    
    Transitions:
        - Aprobada → Pendiente
        - Pagada → Aprobada (requiere motivo ≥ 10 chars)
        - Anulada → Pendiente (requiere motivo ≥ 10 chars)
    
    Preconditions:
        - La liquidación debe existir
        - La liquidación NO debe estar en estado "Pendiente"
        - Si estado es Pagada o Anulada, motivo debe tener ≥ 10 caracteres
    
    Postconditions:
        - Estado cambia según transición definida
        - Campos de auditoría se actualizan
        - Se registra en historial
    
    Args:
        id_liquidacion: ID de la liquidación a reversar
        motivo: Razón de la reversión (requerido para Pagada/Anulada)
        usuario_sistema: Usuario que ejecuta la acción
    
    Returns:
        dict: {"exitosa": bool, "mensaje": str, "nuevo_estado": str}
    
    Raises:
        ValueError: Si la liquidación está en estado Pendiente
        ValueError: Si motivo es requerido y no cumple longitud mínima
        ValueError: Si la liquidación no existe
    """
```

### 3. obtener_acciones_disponibles

```python
def obtener_acciones_disponibles(
    self, 
    id_liquidacion: int
) -> dict:
    """
    Retorna las acciones disponibles para una liquidación según su estado.
    
    Args:
        id_liquidacion: ID de la liquidación
    
    Returns:
        dict: {
            "eliminar": bool,      # True si estado == "Pendiente"
            "reversar": bool,      # True si estado != "Pendiente"
            "aprobar": bool,       # True si estado == "Pendiente"
            "anular": bool,        # True si estado not in ["Pagada", "Anulada"]
            "editar": bool,        # True si estado == "Pendiente"
            "motivo_requerido": bool  # True si reversar requiere motivo
        }
    """
```

## Frontend State Contracts

### 1. eliminar_liquidacion (EventHandler)

```python
@rx.event(background=True)
async def eliminar_liquidacion(self, id_liquidacion: int):
    """
    Handler para eliminar una liquidación.
    
    Flow:
        1. Muestra modal de confirmación
        2. Usuario confirma
        3. Llama a servicio.eliminar_liquidacion()
        4. Muestra toast de éxito/error
        5. Recarga grid
    
    State Updates:
        - show_delete_confirm_modal: True → False
        - Grid data: recargado
    """
```

### 2. reversar_liquidacion (EventHandler)

```python
@rx.event(background=True)
async def reversar_liquidacion(self, id_liquidacion: int, motivo: str):
    """
    Handler para reversar una liquidación.
    
    Flow:
        1. Muestra modal con campo motivo (si aplica)
        2. Usuario completa motivo y confirma
        3. Llama a servicio.reversar_liquidacion()
        4. Muestra toast de éxito/error
        5. Recarga grid
    
    State Updates:
        - show_reverse_modal: True → False
        - reverse_motivo: "" → ""
        - Grid data: recargado
    """
```

### 3. open_delete_confirm_modal

```python
def open_delete_confirm_modal(self, id_liquidacion: int):
    """
    Abre modal de confirmación para eliminar.
    
    Args:
        id_liquidacion: ID de la liquidación a eliminar
    
    State Updates:
        - liquidacion_id_for_action: id_liquidacion
        - show_delete_confirm_modal: True
    """
```

### 4. open_reverse_modal

```python
def open_reverse_modal(self, id_liquidacion: int, estado: str):
    """
    Abre modal de reversión con campo motivo si es necesario.
    
    Args:
        id_liquidacion: ID de la liquidación a reversar
        estado: Estado actual (determina si motivo es requerido)
    
    State Updates:
        - liquidacion_id_for_action: id_liquidacion
        - reverse_motivo_requerido: estado in ["Pagada", "Anulada"]
        - show_reverse_modal: True
    """
```

## UI Component Contracts

### Action Buttons (Grid Row)

```python
# Columna de acciones en tabla
rx.cond(
    LiquidacionAsesoresState.liquidaciones[liq_idx]["estado"] == "Pendiente",
    rx.button("Eliminar", on_click=lambda: LiquidacionFormState.open_delete_confirm_modal(liq["id_liquidacion"])),
    rx.button("Reversar", on_click=lambda: LiquidacionFormState.open_reverse_modal(liq["id_liquidacion"], liq["estado"]))
)
```

### Delete Confirmation Modal

```python
rx.dialog(
    rx.dialog.title("Confirmar Eliminación"),
    rx.dialog.description("¿Está seguro de eliminar esta liquidación?"),
    rx.dialog.close(
        rx.button("Cancelar", on_click=LiquidacionFormState.close_delete_modal),
        rx.button("Eliminar", on_click=lambda: LiquidacionFormState.eliminar_liquidacion(LiquidacionFormState.liquidacion_id_for_action)),
    ),
)
```

### Reverse Modal (with optional motivo)

```python
rx.dialog(
    rx.dialog.title("Confirmar Reversión"),
    rx.dialog.description("¿Está seguro de reversar esta liquidación?"),
    rx.cond(
        LiquidacionFormState.reverse_motivo_requerido,
        rx.input(placeholder="Motivo (mínimo 10 caracteres)", on_change=LiquidacionFormState.set_reverse_motivo),
    ),
    rx.dialog.close(
        rx.button("Cancelar", on_click=LiquidacionFormState.close_reverse_modal),
        rx.button(
            "Reversar", 
            on_click=lambda: LiquidacionFormState.reversar_liquidacion(
                LiquidacionFormState.liquidacion_id_for_action,
                LiquidacionFormState.reverse_motivo
            ),
            is_disabled=LiquidacionFormState.reverse_motivo_requerido & (len(LiquidacionFormState.reverse_motivo) < 10)
        ),
    ),
)
```

## Error Responses

### Standard Error Format

```python
{
    "exitosa": False,
    "mensaje": "Descripción del error para el usuario",
    "codigo": "ESTADO_NO_PERMITIDO"  # Opcional, para debugging
}
```

### Error Codes

| Code | Description |
|------|-------------|
| ESTADO_NO_PERMITIDO | Acción no permitida para el estado actual |
| MOTIVO_REQUIRIDO | Motivo obligatorio no proporcionado |
| MOTIVO_CORTO | Motivo menor a 10 caracteres |
| ENTIDADES_RELACIONADAS | Tiene descuentos/pagos que impiden la operación |
| LIQUIDACION_NO_ENCONTRADA | ID no existe |
| YA_ELIMINADA | Liquidación ya fue eliminada (idempotente) |
