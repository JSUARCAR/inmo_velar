# Interface Contract: Advanced Filter Bar Search Input

## Component Interface

### Props (Unchanged)

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `*children` | `rx.Component` | - | Filter controls (dropdowns, toggles) |
| `search_placeholder` | `str` | `"Buscar..."` | Placeholder text for search input |
| `on_search` | `Callable` | `None` | Handler for search text changes |
| `search_value` | `str` | `""` | Current search text value |
| `on_clear` | `Callable` | `None` | Handler for "Limpiar" button |
| `action_buttons` | `List[rx.Component]` | `None` | Right-aligned action buttons |
| `active_filter_count` | `int` | `0` | Badge count for active filters |

### Rendered Output

The component will render:

**Desktop View** (md breakpoint and above):
```
┌─────────────────────────────────────────────────────────┐
│ [Buscar input] [Filter 1] [Filter 2] ... [Filter N]    │
│                                                         │
│ [Limpiar button]                    [Action buttons]    │
└─────────────────────────────────────────────────────────┘
```

**Mobile View** (below md breakpoint):
```
┌─────────────────────────────────────┐
│ [Filtros button with badge]         │
│                                     │
│ [Action buttons]                    │
└─────────────────────────────────────┘

Drawer (on Filtros click):
┌─────────────────────────────────────┐
│ Filtros Avanzados              [X]  │
│                                     │
│ [Buscar input]                      │
│ [Filter 1]                          │
│ [Filter 2]                          │
│ ...                                 │
│ [Filter N]                          │
│                                     │
│ [Limpiar button]                    │
└─────────────────────────────────────┘
```

### Search Input Behavior

1. **Input**: Accepts text input from user
2. **State Update**: Calls `on_search` handler on each keystroke
3. **Filtering**: Search is applied on next data fetch (not real-time)
4. **Reset**: Clear button resets search value to empty string

### Styling Contract

| Element | Style Token | Properties |
|---------|-------------|------------|
| Search input | `NEU_FILTER_INPUT_STYLE` | height: 40px, border-radius: 8px |
| Search label | `NEU_FILTER_LABEL_STYLE` | font-size: small, font-weight: 600 |
| Search container | - | width: ["100%", "100%", "250px"] |

### Integration Points

- **State Classes**: Each module's `set_search()` method handles search value updates
- **Clear Functionality**: `clear_filters()` resets search along with other filters
- **Active Count**: `active_filter_count` computed var includes search in count
- **Data Loading**: Search term is applied during `load_*()` data fetch calls
