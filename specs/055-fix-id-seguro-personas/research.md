# Research: Fix ID Seguro - Personas

**Date**: 2026-07-15

## Research Tasks

### T1: Análisis del error `PopoverPortal must be used within Popover`

**Hallazgo**: El error ocurre porque `selector_busqueda()` en `modal_form.py` (línea 44) usa `rx.popover.content` directamente sin envolverlo en `rx.popover.root`.

**Código problemático** (modal_form.py:42-81):
```python
rx.cond(
    menu_abierto,
    rx.popover.content(  # ← Error: no hay rx.popover.root padre
        rx.vstack(...)
    ),
),
```

**Causa raíz**: Radix UI requiere que `PopoverPortal` (que `rx.popover.content` usa internamente) se renderice dentro de un `Popover` context (`rx.popover.root`). Cuando el formulario está dentro de un `rx.dialog.content`, el portal se renderiza fuera del contexto esperado.

### T2: Análisis del patrón alternativo en `searchable_select.py`

**Hallazgo**: El componente `searchable_select.py` (líneas 75-126) implementa un dropdown usando CSS positioning en lugar de Radix UI Popover:

```python
dropdown_menu = rx.cond(
    menu_open,
    rx.box(
        rx.scroll_area(...),
        position="absolute",
        top="100%",
        z_index=styles.Z_POPOVER,
    ),
)
```

**Ventajas**:
- No depende de Radix UI Popover context
- Funciona correctamente dentro de Dialog/Modal
- Ya está probado en la aplicación
- Comportamiento visual idéntico al original

### T3: Validación de CSS positioning dentro de Dialog

**Hallazgo**: El patrón `position="absolute"` funciona correctamente dentro de `rx.dialog.content` porque:
1. El Dialog ya tiene `overflow: hidden` por defecto
2. El dropdown se posiciona relativo al contenedor padre con `position: relative`
3. El `z_index=styles.Z_POPOVER` (1050) garantiza que aparezca sobre otros elementos

**Referencia**: Constitución §16 - "La configuración de `pointer-events` y `z-index` se gestiona de forma centralizada en el `BASE_STYLE`"

## Decisiones

| Decisión | Decidido | Rationale |
|----------|----------|-----------|
| Reemplazar `rx.popover.content` por `rx.box` con CSS | 2026-07-15 | Patrón probado en `searchable_select.py`, evita dependencia de Radix UI context |
| Mantener la misma interfaz de la función | 2026-07-15 | No requiere cambios en `personas_state.py` ni en los llamadores |
| Usar `on_mouse_down` en lugar de `on_click` para opciones | 2026-07-15 | Evita `on_blur` prematuro del input (patrón de `searchable_select.py`) |

## Dependencias

- `styles.Z_POPOVER` ya definido en `src/presentacion_reflex/styles.py`
- `styles.GLOBAL_TRANSITION` ya definido
- `styles.BG_HOVER`, `styles.TEXT_PRIMARY` ya definidos
- `styles.NEU_PANEL_STYLE` ya definido

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Dropdown se corta por overflow del Dialog | Baja | Medio | Verificar con `max_height` en scroll_area |
| Estilo visual diferente al original | Baja | Bajo | Reutilizar los mismos estilos CSS |
| Regresión en otros usos de `selector_busqueda` | N/A | N/A | Función solo se usa en `campos_arrendatario()` |
