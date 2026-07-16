# Implementation Plan: Fix ID Seguro - Personas

**Branch**: `bugfix/055-fix-id-seguro-personas` | **Date**: 2026-07-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/055-fix-id-seguro-personas/spec.md`

## Summary

Corregir el error `PopoverPortal must be used within Popover` que ocurre al intentar seleccionar un valor en el campo ID Seguro del formulario de creación de personas con rol Arrendatario. La causa raíz es que la función `selector_busqueda()` en `modal_form.py` usa `rx.popover.content` directamente sin envolverlo en `rx.popover.root`, causando que el Portal se renderice fuera del contexto de Popover requerido por Radix UI.

## Technical Context

**Language/Version**: Python 3.11+, Reflex 0.6.x

**Primary Dependencies**: Reflex (Radix UI primitives), PostgreSQL

**Storage**: PostgreSQL (lectura de catálogo de seguros)

**Testing**: Manual verification en navegador (consola limpia), tests de renderizado Reflex

**Target Platform**: Web application (localhost:3000)

**Project Type**: Web application (Full-stack Python/Reflex)

**Performance Goals**: Carga síncrona del combobox (< 2 segundos)

**Constraints**: Sin modificaciones a la base de datos, fix limitado a componente UI

**Scale/Scope**: Solo afecta el campo ID Seguro del rol Arrendatario

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| §2.1 Clean Architecture | ✅ PASS | Fix en capa de Presentación, no afecta otras capas |
| §2.2 Naming conventions | ✅ PASS | Función `selector_busqueda` mantiene snake_case |
| §16 Gestión de Portals | ⚠️ REVISAR | Fix específicamente aborda这个问题 de Portals |
| §10 Runtime Verification | ✅ PASS | Requiere verificación en consola del navegador |
| §13 Stop-the-Line | ✅ PASS | Error impide funcionalidad core |

## Project Structure

### Documentation (this feature)

```text
specs/055-fix-id-seguro-personas/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A - no schema changes)
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── components/
│   ├── personas/
│   │   └── modal_form.py        # ← ARCHIVO A MODIFICAR (selector_busqueda)
│   └── shared/
│       └── searchable_select.py  # Patrón de referencia (no usar Popover)
└── state/
    └── personas_state.py         # Estado del combobox (sin cambios)
```

**Structure Decision**: Fix puntual en `modal_form.py`, reutilizando el patrón de `searchable_select.py` que usa CSS positioning en lugar de Radix UI Popover.

## Complexity Tracking

No aplica - fix de bajo complejidad, cambio en un solo archivo.

## Phase 0: Research

### Research Tasks

1. **Verificar patrón `searchable_select`**: Confirmar que el componente `searchable_select` funciona correctamente dentro de Dialog/Modal sin errores de Popover.

2. **Revisar documentación Radix UI**: Confirmar que `rx.popover.content` requiere `rx.popover.root` como padre directo.

3. **Validar que `rx.box` con `position="absolute"` funciona dentro de `rx.dialog.content`**: El patrón alternativo usa CSS positioning, verificar que no hay overflow issues.

### Findings

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Reemplazar `rx.popover.content` por `rx.box` con CSS positioning | `searchable_select.py` ya usa este patrón exitosamente dentro de la aplicación. Evita la dependencia de Radix UI Popover context. | 1) Envolver con `rx.popover.root` - más complejo, requiere manejar estado de apertura. 2) Usar `rx.select` nativo - no soporta búsqueda. |

## Phase 1: Design

### Data Model

No aplica - no hay cambios en esquema de base de datos.

### Interface Contracts

No aplica - es un fix de UI interno.

### Component Contract (selector_busqueda)

**Entrada**:
- `etiqueta`: str - Label del campo
- `marcador`: str - Placeholder
- `etiqueta_valor`: Var[str] - Valor seleccionado (label)
- `valor_busqueda`: Var[str] - Texto de búsqueda
- `menu_abierto`: Var[bool] - Estado del menú
- `opciones_filtradas`: Var[list] - Opciones disponibles
- `al_cambiar_busqueda`: callable - Handler de búsqueda
- `al_alternar_menu`: callable - Handler de toggle
- `al_seleccionar`: callable - Handler de selección

**Salida**: rx.Component (vstack con input + dropdown)

**Comportamiento**:
1. Input con floating label que actúa como trigger
2. Dropdown flotante con `position="absolute"` cuando `menu_abierto` es True
3. Opciones clickeables que llaman `al_seleccionar`
4. Cierre automático al perder foco

### Quickstart Validation

1. Abrir `http://localhost:3000/personas`
2. Click en "Nueva Persona"
3. Completar Paso 1 (info básica) → Click "Siguiente"
4. Seleccionar rol "Arrendatario" en Paso 2 → Click "Siguiente"
5. En Paso 3, verificar que el campo "ID Seguro" renderiza sin errores
6. Abrir consola del navegador (F12) → Verificar que no hay errores `PopoverPortal`
7. Click en el campo "ID Seguro" → Verificar que el dropdown se abre correctamente
8. Seleccionar una opción → Verificar que se registra correctamente
9. Completar formulario y guardar → Verificar que la persona se crea con el seguro asignado
