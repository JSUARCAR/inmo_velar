# Implementation Plan: Restablecer Etiquetas Flotantes y Tooltips

**Branch**: `[025-fix-ui-labels-tooltips]` | **Date**: 2026-07-05 | **Spec**: [specs/025-fix-ui-labels-tooltips/spec.md](specs/025-fix-ui-labels-tooltips/spec.md)

**Input**: Feature specification from `specs/025-fix-ui-labels-tooltips/spec.md`

## Summary

Restaurar la funcionalidad de Floating Labels (Etiquetas Flotantes) en los formularios y los Tooltips en los botones en toda la aplicación. Se utilizará la configuración CSS centralizada en el sistema de diseño (`BASE_STYLE`) y los componentes base de Reflex (`rx.hover_card` o `rx.tooltip`) para asegurar consistencia UI/UX y evitar problemas de z-index y pointer-events.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex

**Storage**: N/A

**Testing**: Reflex dev server (`reflex run --env dev`), Visual Regression (Manual)

**Target Platform**: Web application (Frontend UI)

**Project Type**: Web application (Reflex)

**Performance Goals**: Sin impacto perceptible en renderizado de UI. Animaciones CSS optimizadas.

**Constraints**: "Claude/Anthropic Design System" para colores y sombras. Respetar jerarquía global de z-index (`Z_TOOLTIP=1100`, `Z_POPOVER=1050`, etc.).

**Scale/Scope**: Todos los formularios y botones principales y secundarios.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **16. GESTIÓN DE SUPERPOSICIONES Y PORTALS (RADIX UI):** Z-Index Global sin "magic numbers". Utilizar la escala en `styles.py`. (PASSED: Se integrará siguiendo este mandato estricto).
- **3. SISTEMA DE DISEÑO:** Respetar transiciones estándar (`all 0.3s cubic-bezier(...)`). (PASSED: Las animaciones de floating labels usarán estos tokens).
- **10. VERIFICACIÓN EN NAVEGADOR Y UI:** Evitar "Estética IA" y adherirse al sistema de diseño. (PASSED: Se usará el código base preexistente para diseño).

## Project Structure

### Documentation (this feature)

```text
specs/025-fix-ui-labels-tooltips/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    ├── styles.py           # Tokens de diseño, z-index y BASE_STYLE (para floating labels y tooltips)
    ├── componentes/
    │   ├── inputs.py       # Posibles wrappers para inputs con floating labels
    │   └── botones.py      # Posibles wrappers para botones con tooltips
    └── ...
```

**Structure Decision**: La corrección se centralizará en la capa de Presentación (`src/presentacion_reflex/`), específicamente revisando `styles.py` y los componentes reutilizables (inputs, botones) para aplicar los tooltips y las clases CSS necesarias para floating labels.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Ninguna | N/A | N/A |
