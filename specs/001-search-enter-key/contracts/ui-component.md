# UI Contract: advanced_filter_bar — on_key_down

**Component**: `advanced_filter_bar`
**File**: `src/presentacion_reflex/components/shared/advanced_filter_bar.py`

## Contract

```python
def advanced_filter_bar(
    *children,
    search_placeholder: str = "Buscar...",
    on_search: Callable = None,          # Existente: on_change del input
    on_key_down: Callable = None,         # NUEVO: on_key_down del input
    search_value: str = "",
    on_clear: Callable = None,
    action_buttons: List[rx.Component] = None,
    **props
) -> rx.Component:
```

## Comportamiento

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `on_key_down` | `Callable` o `None` | `None` | Handler para el evento `on_key_down` del `rx.input` de búsqueda. Si es `None`, no se asigna (backward-compatible). |

## Backward Compatibility

- Si `on_key_down` no se pasa o es `None`, el componente funciona exactamente igual que antes.
- No se rompe ninguna llamada existente al componente.

## Ejemplo de Uso (nuevo)

```python
advanced_filter_bar(
    search_placeholder="Buscar por nombre o documento...",
    on_search=PersonasState.set_search,
    on_key_down=PersonasState.handle_search_key_down,  # NUEVO
    search_value=PersonasState.search_query,
    on_clear=PersonasState.clear_filters,
)
```
