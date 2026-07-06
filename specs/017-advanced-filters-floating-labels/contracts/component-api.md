# Component API Contract: Floating Label Filters

**Date**: 2026-07-05
**Feature**: 017-advanced-filters-floating-labels

## Component Interface: neuro_floating_input

```python
def neuro_floating_input(
    label: str,                    # REQUIRED: Visible label text (replaces placeholder)
    value: str | rx.Var,           # REQUIRED: Controlled value binding
    on_change: Callable[[str], None],  # REQUIRED: Change callback
    error: bool | rx.Var = False,  # Optional: Error state (red label)
    disabled: bool = False,        # Optional: Disabled state
    type: str = "text",            # Optional: Input type ("text", "date", etc.)
    **kwargs,                      # Pass-through to rx.input
) -> rx.Component:
```

**Usage Pattern**:
```python
neuro_floating_input(
    label="Buscar por nombre",
    value=State.search_query,
    on_change=State.set_search_query,
)
```

**Date Input Pattern**:
```python
neuro_floating_input(
    label="Fecha Desde",
    value=State.filtro_fecha_desde,
    on_change=State.set_filtro_fecha_desde,
    type="date",
)
```

## Component Interface: neuro_floating_select

```python
def neuro_floating_select(
    label: str,                    # REQUIRED: Visible label text
    value: str | rx.Var,           # REQUIRED: Selected value
    on_change: Callable[[str], None],  # REQUIRED: Change callback
    options: list[dict[str, str]], # REQUIRED: [{"label": "Text", "value": "val"}]
    error: bool | rx.Var = False,  # Optional: Error state
    placeholder: str = "Seleccionar...",  # Optional: Dropdown placeholder
    disabled: bool = False,        # Optional: Disabled state
    **kwargs,                      # Pass-through to rx.select.root
) -> rx.Component:
```

**Usage Pattern**:
```python
neuro_floating_select(
    label="Estado",
    value=State.filtro_estado,
    on_change=State.set_filtro_estado,
    options=[
        {"label": "Activo", "value": "activo"},
        {"label": "Inactivo", "value": "inactivo"},
    ],
)
```

## Migration Mapping

### neuro_input → neuro_floating_input

| Before | After |
|--------|-------|
| `neuro_input(placeholder="Buscar...", value=S.q, on_change=S.set_q)` | `neuro_floating_input(label="Buscar", value=S.q, on_change=S.set_q)` |
| `neuro_input(placeholder="Desde", type="date", value=S.fd, on_change=S.set_fd)` | `neuro_floating_input(label="Fecha Desde", type="date", value=S.fd, on_change=S.set_fd)` |

### neuro_select_root → neuro_floating_select

| Before | After |
|--------|-------|
| `neuro_select_root(placeholder="Estado", value=S.f, on_change=S.set_f, options=opts)` | `neuro_floating_select(label="Estado", value=S.f, on_change=S.set_f, options=opts)` |

### rx.input → neuro_floating_input (raw migration)

| Before | After |
|--------|-------|
| `rx.input(placeholder="Buscar...", value=S.q, on_change=S.set_q)` | `neuro_floating_input(label="Buscar", value=S.q, on_change=S.set_q)` |

### rx.select → neuro_floating_select (raw migration)

| Before | After |
|--------|-------|
| `rx.select(placeholder="Estado", value=S.f, on_change=S.set_f, ...)` | `neuro_floating_select(label="Estado", value=S.f, on_change=S.set_f, options=opts)` |

## Import Paths

```python
# For modules already using neuro_elements:
from src.presentacion_reflex.components.neuro_elements import neuro_floating_input, neuro_floating_select

# For modules using raw rx.input/rx.select (add to existing imports):
from src.presentacion_reflex.components.neuro_elements import neuro_floating_input, neuro_floating_select
```

## Accessibility Contract

- Each `neuro_floating_input` renders a `<label>` with `html_for` pointing to the input's `id`
- Each `neuro_floating_select` renders a `<label>` with `html_for` pointing to the select trigger's `id`
- Screen readers announce the label text when focus reaches the field
- Keyboard navigation (Tab, Shift+Tab, Enter, arrows) works unchanged
