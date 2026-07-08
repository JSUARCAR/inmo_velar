# Component API Contract: AdvancedFilterBar

**Date**: 2026-07-07

## Overview

`AdvancedFilterBar` is a reusable Reflex component that provides a standardized container and layout for filter controls across all 7 modules.

## Component Signature

```python
def advanced_filter_bar(
    *children,           # Filter components (inputs, selects, toggles, etc.)
    search_placeholder: str = "Buscar...",  # Placeholder for search input
    on_search: Callable = None,            # Search change handler
    search_value: str = "",                # Current search value
    on_clear: Callable = None,             # Clear all filters handler
    action_buttons: list = None,           # Right-aligned action buttons (icon-only)
    **props             # Additional props passed to container
) -> rx.Component
```

## Props

| Prop | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `*children` | `rx.Component` | — | Yes | Filter components (Select, DatePicker, Toggle, Checkbox) arranged in a flex row |
| `search_placeholder` | `str` | `"Buscar..."` | No | Placeholder text for the search input |
| `on_search` | `Callable` | `None` | Yes | Event handler called when search text changes |
| `search_value` | `str` | `""` | No | Current search input value |
| `on_clear` | `Callable` | `None` | Yes | Event handler called when "Limpiar" button is pressed |
| `action_buttons` | `list[rx.Component]` | `None` | No | List of icon-only action buttons displayed right-aligned |
| `**props` | — | — | No | Additional props forwarded to the container `rx.box` |

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│ AdvancedFilterBar (rx.box with NEU_FILTER_BAR_STYLE)               │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ rx.flex (direction=breakpoints, wrap=wrap, gap=4)              │ │
│ │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐ │ │
│ │ │ Search   │ │ Filter 1 │ │ Filter 2 │ │ Filter 3 │ │Actions│ │ │
│ │ │ Input    │ │ (Select) │ │ (Select) │ │ (Toggle) │ │  📋  │ │ │
│ │ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────┘ │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                         ┌──────────┐                                │
│                         │ Limpiar  │ ← Badge with count            │
│                         │    🗑️    │                                │
│                         └──────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Styling

| Property | Value | Source |
|----------|-------|--------|
| Container background | `#FFFFFF` | Per clarification Q2 |
| Container border | `1px solid #E5E7EB` | Per clarification Q2 |
| Container shadow | None | Per clarification Q2 |
| Container border-radius | `16px` | From `NEU_PANEL_STYLE` |
| Container padding | `1.5rem` (24px) | From `NEU_PANEL_STYLE` |
| Flex gap (horizontal) | `16px` (gap="4") | Per spec FR-002 |
| Flex gap (vertical) | `12px` (gap="3") | Per spec FR-003 |
| Flex wrap | `wrap` | Per spec FR-008 |
| Flex direction | `breakpoints(initial="column", md="row")` | Responsive |

## Component Dimensions (Applied to Children)

| Component | Height | Border-Radius | Source |
|-----------|--------|---------------|--------|
| Text Input | 40px | 8px | Per spec FR-001 |
| Select/ComboBox | 40px | 8px | Per spec FR-001 |
| DatePicker | 40px | 8px | Per spec FR-001 |
| Toggle/Switch | 40px | — | Aligned vertically |
| Checkbox | — | — | Aligned vertically |
| Action Button | 40px | 10px | Per spec FR-006 |

## Label Pattern

| Component Type | Label Position |
|----------------|----------------|
| Text Search Input | Placeholder only (no label above) |
| Select/ComboBox | Label ABOVE the component |
| DatePicker | Label ABOVE the component |
| Toggle/Switch | Label to the RIGHT of the component |
| Checkbox | Label to the RIGHT of the component |

## Badge Behavior

- The "Limpiar" button displays a numeric badge when `_active_filter_count > 0`
- Badge shows the exact count of filters with non-default values
- Badge disappears when count is 0

## Usage Example (Personas Module)

```python
advanced_filter_bar(
    rx.input(
        placeholder="Buscar por nombre o documento...",
        on_change=PersonasState.set_search_query,
        value=PersonasState.search_query,
        style=NEU_FILTER_INPUT_STYLE,
    ),
    rx.select(
        ["Todos", "Propietario", "Arrendatario", ...],
        value=PersonasState.filtro_rol,
        on_change=PersonasState.set_filtro_rol,
        style=NEU_FILTER_SELECT_STYLE,
    ),
    # ... more filters ...
    search_placeholder="Buscar por nombre o documento...",
    on_search=PersonasState.set_search_query,
    search_value=PersonasState.search_query,
    on_clear=PersonasState.clear_filters,
    action_buttons=[
        rx.icon_button("grid", on_click=PersonasState.set_view("grid")),
        rx.icon_button("list", on_click=PersonasState.set_view("list")),
        rx.icon_button("refresh-cw", on_click=PersonasState.refresh),
    ],
)
```

## State Methods Expected

Each module must implement these methods in its State class:

| Method | Signature | Description |
|--------|-----------|-------------|
| `set_search_query` | `(value: str) -> None` | Update search text |
| `clear_filters` | `() -> None` | Reset all filters to defaults |
| `get_active_filter_count` | `() -> int` | Return count of non-default filters |
