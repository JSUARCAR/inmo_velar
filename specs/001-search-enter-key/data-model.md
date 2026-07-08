# Data Model: Búsqueda con Tecla ENTER

**Date**: 2026-07-08
**Feature**: 001-search-enter-key

## Overview

Este feature NO introduce nuevas entidades de datos. Modifica exclusivamente el flujo de eventos UI (teclado → handler → búsqueda existente). Las entidades existentes permanecen intactas.

## State Variables Existentes (no modificadas)

Cada módulo ya tiene una variable de estado para el texto de búsqueda:

| Módulo | State Class | Variable | Tipo |
|--------|-------------|----------|------|
| Personas | `PersonasState` | `search_query` | `str` |
| Propiedades | `PropiedadesState` | `search_text` | `str` |
| Contratos | `ContratosState` | `search_text` | `str` |
| Liquidaciones | `LiquidacionesState` | `search_text` | `str` |
| Liquidación Asesores | `LiquidacionFiltrosState` | `search_text` | `str` |
| Recaudos | `RecaudosState` | `search_text` | `str` |
| Incidentes | `IncidentesState` | `search_text` | `str` |

## Event Flow (nuevo patrón)

```
Usuario presiona ENTER en rx.input
        │
        ▼
on_key_down → State.handle_search_key_down(key)
        │
        ▼
   ¿key == "Enter"?
    │           │
   SÍ          NO → no-op
    │
    ▼
State.search_<modulo>()
    │
    ▼
self.page = 1  (reset paginación)
    │
    ▼
return State.load_<modulo>()  (reutiliza lógica existente)
```

## State Methods (nuevos para módulos que no los tienen)

### PropiedadesState — Nuevos métodos

```python
def search_propiedades(self):
    """Ejecuta la búsqueda contra BD (llamar desde botón o Enter)."""
    self.current_page = 1
    return PropiedadesState.load_propiedades

def handle_search_key_down(self, key: str):
    """Lanza la búsqueda al presionar Enter en el campo de texto."""
    if key == "Enter":
        return self.search_propiedades()
```

### ContratosState — Nuevos métodos

```python
def search_contratos(self):
    """Ejecuta la búsqueda contra BD (llamar desde botón o Enter)."""
    self.current_page = 1
    return ContratosState.load_contratos

def handle_search_key_down(self, key: str):
    """Lanza la búsqueda al presionar Enter en el campo de texto."""
    if key == "Enter":
        return self.search_contratos()
```

### LiquidacionFiltrosState — Nuevos métodos

```python
def handle_search_key_down(self, key: str):
    """Lanza la búsqueda al presionar Enter en el campo de texto."""
    if key == "Enter":
        return self._trigger_reload()
```

### IncidentesState — Nuevos métodos

```python
def search_incidentes(self):
    """Ejecuta la búsqueda contra BD (llamar desde botón o Enter)."""
    self.page = 1
    return IncidentesState.load_incidentes

def handle_search_key_down(self, key: str):
    """Lanza la búsqueda al presionar Enter en el campo de texto."""
    if key == "Enter":
        return self.search_incidentes()
```

## Data Flow Completo (con filtros avanzados)

```
Filtros avanzados (dropdowns, fechas, etc.)
        │
        ▼
State.filter_* variables (ya existentes, no se modifican)
        │
        ▼
search_text (set por on_change del input)
        │
        ▼
handle_search_key_down("Enter")
        │
        ▼
search_<modulo>() → page = 1
        │
        ▼
load_<modulo>() → aplica search_text + filtros + paginación
        │
        ▼
Respuesta filtrada → UI se actualiza
```

## Nota sobre Liquidación de Asesores

Este módulo usa un patrón diferente: `LiquidacionFiltrosState` (state de filtros) + `LiquidacionGridState` (state de grilla). El handler se agrega a `LiquidacionFiltrosState` que ya tiene `_trigger_reload()` para invocar `LiquidacionGridState.load_liquidaciones()`.
