# Implementation Plan: Corrección de Floating Labels y Tooltips

**Branch**: `027-fix-floating-labels-tooltips` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/027-fix-floating-labels-tooltips/spec.md`

## Summary

Corregir el comportamiento de Floating Labels y Toolticks en Filtros Avanzados y Modales de los 14 módulos del sistema. La implementación actual tiene componentes base (`floating_label.py`, `neuro_elements.py`) que requieren ajustes de consistencia, z-index para tooltips en modales, y centralización de textos de tooltips.

## Technical Context

**Language/Version**: Python 3.11+ / Reflex 0.8.x

**Primary Dependencies**: Reflex (rx), Radix UI (subyacente)

**Storage**: N/A (componentes UI puros)

**Testing**: Visual validation + Playwright (si disponible)

**Target Platform**: Web (desktop + responsive)

**Project Type**: Web application (frontend Reflex)

**Performance Goals**: Transiciones UI a 60fps, sin re-renders innecesarios

**Constraints**: 
- Mantener compatibilidad con `styles.py` existente
- Usar tokens de diseño definidos (FL_*, Z_*, NEU_*)
- No romper componentes existentes que usen `floating_input`/`floating_select`

**Scale/Scope**: 14 módulos, ~100+ campos de formulario, ~50+ tooltips

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| Clean Architecture | ✅ | Cambios solo en capa Presentación |
| Claude/Anthropic Design System | ✅ | Usar tokens existentes en styles.py |
| Zero Leak | ✅ | Sin credenciales ni datos sensibles |
| Nomenclatura snake_case | ✅ | Funciones y archivos en snake_case |
| Type Hints | ✅ | Mantener type hints existentes |
| Docstrings Google Style | ✅ | Mantener en funciones modificadas |

## Project Structure

### Documentation (this feature)

```text
specs/027-fix-floating-labels-tooltips/
├── plan.md              # Este archivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── styles.py                    # Tokens de diseño (FL_*, Z_*, NEU_*)
├── components/
│   ├── shared/
│   │   └── floating_label.py    # Componentes base (MODIFICAR)
│   ├── neuro_elements.py        # Wrappers neumórficos (MODIFICAR)
│   ├── personas/                # Filtros/Modales (VALIDAR)
│   ├── propiedades/             # Filtros/Modales (VALIDAR)
│   ├── contratos/               # Filtros/Modales (VALIDAR)
│   ├── liquidaciones/           # Filtros/Modales (VALIDAR)
│   ├── liquidacion_asesores/    # Filtros/Modales (VALIDAR)
│   ├── recaudos/                # Filtros/Modales (VALIDAR)
│   ├── desocupaciones/          # Filtros/Modales (VALIDAR)
│   ├── incidentes/              # Filtros/Modales (VALIDAR)
│   ├── seguros/                 # Filtros/Modales (VALIDAR)
│   ├── recibos/                 # Filtros/Modales (VALIDAR)
│   └── usuarios/                # Filtros/Modales (VALIDAR)
```

**Structure Decision**: No se requieren nuevos directorios. Los cambios se concentran en:
1. `components/shared/floating_label.py` — Correcciones base
2. `components/neuro_elements.py` — Wrappers actualizados
3. `styles.py` — Nuevos tokens si es necesario
4. Módulos individuales — Validación y corrección de uso

## Complexity Tracking

No se requiere justificación de violaciones. El cambio es una corrección de UI dentro de la arquitectura existente.

---

## Phase 0: Research

### Research Tasks

1. **Estado actual de Floating Labels**: Verificar qué módulos usan `floating_input`/`floating_select` vs componentes nativos
2. **Tooltips existentes**: Identificar qué módulos tienen tooltips y cuáles les faltan
3. **Z-index conflicts**: Verificar si hay conflictos de z-index entre modales y tooltips
4. **Contenido de tooltips**: Identificar si el texto de tooltips está hardcodeado o centralizado

### Research Output → research.md

(Generado después de la investigación)

## Phase 1: Design & Contracts

### Data Model → data-model.md

No aplica — este feature es puramente de UI sin nuevos entities.

### Contracts

No aplica — no hay interfaces externas nuevas.

### Quickstart → quickstart.md

(Generado después del diseño)

---

## Implementation Strategy

### Fase 1: Corrección de Componentes Base

**Archivos**: `floating_label.py`, `styles.py`

1. Verificar que `FL_TRANSITION` use el timing correcto (`0.2s` actual → mantener o ajustar a `0.3s` según clarificación)
2. Asegurar que `FL_LABEL_ERROR_COLOR` esté definido correctamente
3. Verificar que `BASE_STYLE` tenga los selectores CSS correctos para floating labels

### Fase 2: Tooltips Centralizados

**Archivos**: Nuevo `tooltips_text.py` (si no existe), `neuro_elements.py`

1. Crear archivo de constantes para textos de tooltips
2. Actualizar `neuro_tooltip` para usar constantes centralizadas
3. Agregar atributos ARIA (`role="tooltip"`, `aria-describedby`)

### Fase 3: Z-Index para Tooltips en Modales

**Archivos**: `styles.py`, `neuro_elements.py`

1. Definir `Z_TOOLTIP_IN_MODAL = int(Z_MODAL) + 50` en styles.py
2. Actualizar `NEU_TOOLTIP_STYLE` para soportar z-index contextual
3. Crear variante de tooltip para modales

### Fase 4: Validación por Módulo

**Archivos**: Cada módulo en `components/`

Para cada módulo:
1. Verificar uso de `floating_input`/`floating_select` en Filtros Avanzados
2. Verificar uso en Modales
3. Verificar presencia de tooltips en iconos ℹ️
4. Corregir inconsistencias

### Fase 5: Testing Visual

1. Abrir cada módulo y verificar Filtros Avanzados
2. Abrir modales principales y verificar formularios
3. Verificar tooltips con hover
4. Verificar comportamiento en error states
5. Verificar consistencia entre módulos
