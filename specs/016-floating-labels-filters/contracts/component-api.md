# Contract: Floating Label Components

**Version**: 1.0.0 | **Date**: 2026-07-05

## Component API Contract

### `floating_input`

Componente de entrada de texto con etiqueta flotante.

```python
def floating_input(
    label: str,
    value: str | rx.Var,
    on_change: Callable[[str], None],
    error: bool | rx.Var = False,
    placeholder: str = " ",
    disabled: bool = False,
    **kwargs,
) -> rx.Component:
    """Input con etiqueta flotante.
    
    Args:
        label: Texto de la etiqueta que se desplaza al recibir foco
        value: Valor controlado del campo
        on_change: Callback cuando el valor cambia
        error: Si True, cambia color de etiqueta a rojo
        placeholder: Placeholder (usar " " para CSS selector)
        disabled: Si True, campo no interactuable
        **kwargs: Props adicionales para rx.input
    
    Returns:
        rx.Component: Input con etiqueta flotante
    """
```

**Comportamiento**:
- Estado vacío: Label en posición centrada, tamaño normal
- Estado foco: Label se desplaza hacia arriba, tamaño reduce
- Estado con valor: Label permanece arriba
- Estado error: Label cambia color a `var(--red-9)`
- Transición: `cubic-bezier(0.4, 0, 0.2, 1)` en 200ms

### `floating_select`

Componente select/dropdown con etiqueta flotante.

```python
def floating_select(
    label: str,
    value: str | rx.Var,
    on_change: Callable[[str], None],
    options: list[dict[str, str]],
    error: bool | rx.Var = False,
    placeholder: str = "Seleccionar...",
    disabled: bool = False,
    **kwargs,
) -> rx.Component:
    """Select con etiqueta flotante.
    
    Args:
        label: Texto de la etiqueta flotante
        value: Valor seleccionado
        on_change: Callback cuando cambia la selección
        options: Lista de opciones [{"label": "Texto", "value": "valor"}]
        error: Si True, cambia color de etiqueta a rojo
        placeholder: Texto cuando no hay selección
        disabled: Si True, select no interactuable
        **kwargs: Props adicionales para rx.select.root
    
    Returns:
        rx.Component: Select con etiqueta flotante
    """
```

**Comportamiento**:
- Similar a `floating_input` pero para selects
- Label siempre visible arriba cuando hay valor seleccionado
- Integrado con `neuro_select_root` existente

### `neuro_floating_input`

Wrapper neumórfico que combina `floating_input` con estilos del sistema.

```python
def neuro_floating_input(
    label: str,
    value: str | rx.Var,
    on_change: Callable[[str], None],
    error: bool | rx.Var = False,
    disabled: bool = False,
    **kwargs,
) -> rx.Component:
    """Input flotante con estilo neumórfico.
    
    Combina floating_input con NEU_INPUT_STYLE del sistema de diseño.
    
    Args:
        label: Texto de la etiqueta flotante
        value: Valor controlado del campo
        on_change: Callback cuando el valor cambia
        error: Si True, aplica estilo de error
        disabled: Si True, campo deshabilitado
        **kwargs: Props adicionales
    
    Returns:
        rx.Component: Input flotante neumórfico
    """
```

## Visual Contract

### Estados Visuales

```
┌─────────────────────────────────────────────────────────┐
│  ESTADO: EMPTY                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Nombre del Campo                                 │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│  Label: centro, tamaño normal, color secondary          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ESTADO: FOCUSED                                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Nombre del                                       │  │
│  │ ▌                                                 │  │
│  └───────────────────────────────────────────────────┘  │
│  Label: arriba, tamaño pequeño, color primary           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ESTADO: FILLED                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Nombre del                                       │  │
│  │ Juan Pérez                                       │  │
│  └───────────────────────────────────────────────────┘  │
│  Label: arriba, tamaño pequeño, color secondary         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ESTADO: ERROR                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Nombre del                                       │  │
│  │ ▌                                                 │  │
│  └───────────────────────────────────────────────────┘  │
│  Label: arriba, tamaño pequeño, color RED (error)       │
└─────────────────────────────────────────────────────────┘
```

## Integration Points

### Con ne_elements.py

```python
# Agregar a neuro_elements.py
from .shared.floating_label import floating_input, floating_select

def neuro_floating_input(label, value, on_change, **kwargs):
    return floating_input(
        label=label,
        value=value,
        on_change=on_change,
        style=NEU_INPUT_STYLE,
        **kwargs,
    )
```

### Con dashboard_filters.py

```python
# Reemplazar en dashboard_filters.py
# ANTES:
neuro_select_root(
    rx.select.group(...),
    placeholder="Seleccionar Mes",
    value=DashboardState.selected_month_name,
    on_change=DashboardState.set_month,
)

# DESPUÉS:
neuro_floating_select(
    label="Mes",
    value=DashboardState.selected_month_name,
    on_change=DashboardState.set_month,
    options=[{"label": m, "value": m} for m in meses],
)
```
