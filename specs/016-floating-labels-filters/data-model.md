# Data Model: Floating Labels en Filtros Avanzados

**Date**: 2026-07-05 | **Feature**: 016-floating-labels-filters

## Overview

Este feature es un componente UI puro. No modela entidades de persistencia, sino estructuras de datos para el estado del componente.

## Component State Model

### FloatingLabelState

Estado interno del componente floating label.

| Campo | Tipo | Descripción | Default |
|-------|------|-------------|---------|
| `is_focused` | `bool` | Si el campo tiene foco | `False` |
| `has_value` | `bool` | Si el campo contiene datos | `False` |
| `is_error` | `bool` | Si el campo tiene error de validación | `False` |

### Transiciones de Estado

```
                   ┌─────────────────┐
                   │  EMPTY (Idle)   │
                   │  label: center  │
                   │  label: normal  │
                   └────────┬────────┘
                            │
              on_focus()    │    on_blur() + no value
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  │                  │
┌─────────────────┐         │                  │
│  FOCUSED        │         │                  │
│  label: top     │◄────────┘                  │
│  label: small   │                            │
└────────┬────────┘                            │
         │                                     │
         │ on_blur()                           │
         │                                     │
         ▼                                     │
┌─────────────────┐                            │
│  FILLED         │                            │
│  label: top     │────────────────────────────┘
│  label: small   │   on_clear() → EMPTY
└─────────────────┘
         │
         │ on_error()
         ▼
┌─────────────────┐
│  ERROR          │
│  label: top     │
│  label: red     │
└─────────────────┘
```

## Props Interface

### FloatingInput Props

| Prop | Tipo | Requerido | Descripción |
|------|------|-----------|-------------|
| `label` | `str` | Sí | Texto de la etiqueta flotante |
| `value` | `str \| rx.Var` | Sí | Valor del campo |
| `on_change` | `Callable` | Sí | Handler de cambio de valor |
| `error` | `bool \| rx.Var` | No | Estado de error (default: `False`) |
| `placeholder` | `str` | No | Placeholder vacío `" "` para CSS |
| `disabled` | `bool` | No | Campo deshabilitado (default: `False`) |
| `**kwargs` | `dict` | No | Props adicionales para `rx.input` |

### FloatingSelect Props

| Prop | Tipo | Requerido | Descripción |
|------|------|-----------|-------------|
| `label` | `str` | Sí | Texto de la etiqueta flotante |
| `value` | `str \| rx.Var` | Sí | Valor seleccionado |
| `on_change` | `Callable` | Sí | Handler de cambio |
| `options` | `list[dict]` | Sí | Lista de opciones `[{label, value}]` |
| `error` | `bool \| rx.Var` | No | Estado de error |
| `placeholder` | `str` | No | Texto cuando no hay selección |
| `disabled` | `bool` | No | Campo deshabilitado |

## CSS Tokens

### Colores

| Token | Valor | Uso |
|-------|-------|-----|
| `--fl-label-color` | `var(--text-secondary)` | Color normal de etiqueta |
| `--fl-label-focus-color` | `var(--brand-primary)` | Color de etiqueta con foco |
| `--fl-label-error-color` | `var(--red-9)` | Color de etiqueta en error |
| `--fl-label-size` | `0.875rem` | Tamaño de fuente normal |
| `--fl-label-size-top` | `0.75rem` | Tamaño de fuente arriba |

### Dimensiones

| Token | Valor | Uso |
|-------|-------|-----|
| `--fl-translate-y` | `-24px` | Distancia de desplazamiento vertical |
| `--fl-transition` | `all 0.3s cubic-bezier(0.4, 0, 0.2, 1)` | Animación estándar |

## Validation Rules

### Input Validation

- `label`: No puede ser vacío
- `value`: Acepta `str` o `rx.Var`
- `on_change`: Requerido para campos controlados

### State Transitions Validation

- `EMPTY → FOCUSED`: Solo cuando `on_focus` se dispara
- `FOCUSED → FILLED`: Cuando `value` no está vacío y `on_blur`
- `FILLED → EMPTY`: Cuando `value` se limpia
- `任何 → ERROR`: Cuando `error=True`
