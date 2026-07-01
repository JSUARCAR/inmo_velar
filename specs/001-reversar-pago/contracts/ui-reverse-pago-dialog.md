# UI Contract: Reverse Pago Confirmation Dialog

**Component**: `reverse_pago_confirm_dialog`
**Trigger**: User clicks "Reversar Pago" button on a liquidation in "Pagada" state

## Dialog Structure

```
┌─────────────────────────────────────────────────┐
│  Confirmar Reversión de Pago                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  ¿Está seguro que desea reversar el pago de    │
│  esta liquidación?                              │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │ Propietario:  [nombre]                    │  │
│  │ Propiedad:    [dirección]                 │  │
│  │ Período:      [YYYY-MM]                   │  │
│  │ Neto a Pagar: [formatted currency]        │  │
│  │ Fecha Pago:   [YYYY-MM-DD]                │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  La liquidación volverá al estado 'Aprobada'.  │
│  Los datos de pago serán eliminados.            │
│                                                 │
│  Motivo de la reversión *:                      │
│  ┌───────────────────────────────────────────┐  │
│  │ [textarea - required, min 10 chars]       │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │   Cancelar   │  │  Confirmar Reversión   │  │
│  └──────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## State Variables (LiquidacionesState)

| Variable | Type | Purpose |
|----------|------|---------|
| `show_reverse_pago_confirm` | bool | Controls dialog visibility |
| `reverse_pago_liquidacion_id` | int | ID of liquidation to reverse |
| `reverse_pago_motivo` | str | User-provided justification |
| `reverse_pago_loading` | bool | Loading state during execution |

## Events

| Event | Trigger | Behavior |
|-------|---------|----------|
| `open_reverse_pago_confirm(id)` | Button click | Loads liquidation data, opens dialog |
| `close_reverse_pago_confirm()` | Cancel/close | Clears state, closes dialog |
| `set_reverse_pago_motivo(value)` | Text input | Updates motivo variable |
| `confirmar_reversar_pago()` | Confirm button | Validates motivo ≥ 10 chars, executes reversal, closes dialog, refreshes list |

## Validation Rules

- Motivo field is required
- Minimum 10 characters
- Confirm button disabled while loading or if motivo < 10 chars

## Button Visibility (in table and detail modal)

```python
# Table row actions
rx.cond(
    (liq["estado"] == "Pagada")
    & AuthState.check_action("Liquidaciones", "REVERSAR_PAGO"),
    rx.tooltip(
        rx.icon_button(rx.icon("rotate_ccw", size=18), ...),
        content="Reversar pago",
    ),
    rx.box(),
)

# Detail modal actions
rx.cond(
    LiquidacionesState.liquidacion_actual["estado"] == "Pagada",
    rx.button(
        rx.icon("rotate_ccw"),
        "Reversar Pago",
        on_click=lambda: LiquidacionesState.open_reverse_pago_confirm(
            LiquidacionesState.liquidacion_actual["id"]
        ),
        color_scheme="orange",
    ),
    rx.box(),
)
```
