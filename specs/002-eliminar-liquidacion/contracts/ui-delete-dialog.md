# UI Contract: Delete Confirmation Dialog

**Component**: `delete_confirm_dialog.py`
**Feature**: 002-eliminar-liquidacion

## State Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `show_delete_modal` | `bool` | `False` | Controls dialog open/close |
| `liquidacion_id_for_delete` | `int` | `0` | ID of liquidation to delete |
| `delete_confirmed` | `bool` | `False` | Checkbox state |

## Event Handlers

### `open_delete_modal(id_liquidacion: int)`
- Sets `liquidacion_id_for_delete = id_liquidacion`
- Sets `delete_confirmed = False`
- Sets `show_delete_modal = True`
- Sets `error_message = ""`

### `close_delete_modal()`
- Sets `show_delete_modal = False`
- Sets `liquidacion_id_for_delete = 0`
- Sets `delete_confirmed = False`
- Sets `error_message = ""`

### `set_delete_confirmed(value: bool)`
- Sets `delete_confirmed = value`

### `confirmar_eliminar()`
- **Preconditions**: `delete_confirmed == True`
- **Validates**: Liquidation exists, state != "Pagada", not already deleted
- **On success**: Calls service, closes modal, reloads data, shows toast
- **On error**: Sets `error_message`, keeps modal open

## Dialog Structure

```
rx.dialog.root(
  rx.dialog.content(
    rx.dialog.title("Eliminar Liquidación"),
    rx.dialog.description("Esta acción es irreversible"),
    rx.vstack(
      # Summary section
      info_row("Propietario:", ...),
      info_row("Propiedad:", ...),
      info_row("Período:", ...),
      info_row("Neto a Pagar:", ...),
      info_row("Estado:", ...),
      
      # Financial breakdown
      section_header("Desglose Financiero"),
      info_row("Total Ingresos:", ...),
      info_row("Comisión:", ...),
      info_row("IVA:", ...),
      info_row("Gastos Admin:", ...),
      info_row("Gastos Servicios:", ...),
      info_row("Gastos Reparaciones:", ...),
      info_row("Pago Predial:", ...),
      info_row("Otros Egresos:", ...),
      
      # Warning
      rx.callout(
        "Esta liquidación será eliminada permanentemente del sistema.",
        icon="triangle-alert",
        color_scheme="red",
      ),
      
      # Confirmation checkbox
      rx.checkbox(
        "Confirmo que deseo eliminar esta liquidación",
        checked=LiquidacionesState.delete_confirmed,
        on_change=LiquidacionesState.set_delete_confirmed,
      ),
      
      # Error display
      rx.cond(error != "", rx.callout(...)),
      
      # Action buttons
      rx.hstack(
        rx.dialog.close(rx.button("Cancelar", variant="soft")),
        rx.button(
          "Eliminar",
          on_click=LiquidacionesState.confirmar_eliminar,
          disabled=~LiquidacionesState.delete_confirmed,
          color_scheme="red",
        ),
      ),
    ),
  ),
  open=LiquidacionesState.show_delete_modal,
  on_open_change=LiquidacionesState.close_delete_modal,
)
```

## Button Visibility Rules

### Individual View (Table)
```python
rx.cond(
    (liq["estado"] != "Pagada") 
    & (liq["eliminada"] != True)
    & AuthState.check_action("Liquidaciones", "ELIMINAR"),
    rx.tooltip(
        rx.icon_button(rx.icon("trash-2"), ...),
        content="Eliminar liquidación",
    ),
    rx.box(),
)
```

### Detail Modal
```python
rx.cond(
    (LiquidacionesState.liquidacion_actual["estado"] != "Pagada")
    & (LiquidacionesState.liquidacion_actual.get("eliminada", False) != True)
    & AuthState.check_action("Liquidaciones", "ELIMINAR"),
    rx.button("Eliminar", on_click=..., color_scheme="red", variant="soft"),
    rx.box(),
)
```

## UX Specifications

- **Dialog width**: max_width="700px"
- **Dialog height**: max_height="80vh" with overflow_y="auto"
- **Checkbox default**: Unchecked (must explicitly confirm)
- **Button disabled**: Until checkbox is checked
- **Error display**: Inline callout within dialog
- **Success feedback**: Toast bottom-right + table reload
- **Loading state**: Show spinner on confirm button during execution
