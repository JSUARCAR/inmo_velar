# UI Contract: Columna "Información Adicional" en Tabla de Contratos

**Component**: `render_table_view()` en `pages/contratos.py`
**Date**: 2026-07-21

## Column Definition

```python
{
    "key": "informacion_adicional",
    "header": "Información Adicional",
    "sortable": True,
    "width": "250px",  # Ancho fijo para consistencia
    "align": "left"
}
```

## Data Contract

### Input (ContratoDict)

```python
informacion_adicional: str | None
```

### Rendering Rules

| Condition | Render |
|-----------|--------|
| `informacion_adicional` is not None | Display text with pipe separators |
| `informacion_adicional` is None | Display "No registrado" in muted style |

### Visual Styling

```python
# Estilo para el contenido
content_style = {
    "fontSize": "13px",
    "color": "#5e5d59",  # Olive Gray del design system
    "lineHeight": "1.4"
}

# Estilo para "No registrado"
muted_style = {
    "fontSize": "13px",
    "color": "#87867f",  # Stone Gray del design system
    "fontStyle": "italic"
}
```

## Sorting Contract

```python
def sort_by_informacion_adicional(items: list[ContratoDict], ascending: bool) -> list[ContratoDict]:
    """Ordena por campo informacion_adicional."""
    return sorted(
        items,
        key=lambda x: x.informacion_adicional or "",
        reverse=not ascending
    )
```

## Filter Contract

La columna NO tiene filtro propio. Se filtra indirectamente al filtrar por `tipo_contrato`.

## Responsive Behavior

| Viewport | Behavior |
|----------|----------|
| Desktop (>1024px) | Columna visible, ancho fijo 250px |
| Tablet (768-1024px) | Columna visible, ancho reducido 200px |
| Mobile (<768px) | Columna accesible via horizontal scroll |
