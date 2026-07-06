# Implementation Plan: Estandarización de Tooltips en Filtros Avanzados

**Branch**: `[022-tooltips-filtros-avanzados]` | **Date**: 2026-07-05 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/022-tooltips-filtros-avanzados/spec.md)

**Input**: Feature specification from `/specs/022-tooltips-filtros-avanzados/spec.md`

## Summary

Estandarizar el uso de tooltips (`rx.tooltip`) en todos los botones de la sección de "Filtros Avanzados" en 15 módulos del sistema, garantizando accesibilidad (foco), UX (ocultamiento en móviles) y homogeneidad gramatical (verbos en infinitivo).

## Technical Context

**Language/Version**: Python 3.11+ / Reflex

**Primary Dependencies**: Reflex, Radix UI (interno en Reflex)

**Storage**: N/A (Feature de presentación UI)

**Testing**: Pruebas de renderizado visual / QA Manual

**Target Platform**: Web (Desktop & Mobile)

**Project Type**: Web Application

**Performance Goals**: N/A

**Constraints**: Usar componentes de Reflex, evitar soluciones ad-hoc, seguir diseño global.

**Scale/Scope**: 15 módulos de UI afectados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Estructura de Capas**: Se limitará estrictamente a la capa de `src/presentacion_reflex/`. Cumple.
- **Nomenclatura**: Se usarán las constantes de UI correctas (ej. `Z_TOOLTIP`). Cumple.
- **Accesibilidad y Portals**: Se cumplirá la directiva de Z-Index (`1100` o superior definido) y `pointer-events`. Cumple.
- **UI Engineering**: Se descarta Flet, se usa exclusivamente Reflex.

## Project Structure

### Documentation (this feature)

```text
specs/022-tooltips-filtros-avanzados/
├── plan.md              # This file
├── research.md          # Investigación de implementación en Reflex
├── data-model.md        # N/A (Feature UI)
└── quickstart.md        # Guía de validación
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    ├── pages/
    │   ├── dashboard.py
    │   ├── gestion_personas.py
    │   ├── gestion_propiedades.py
    │   ├── gestion_contratos.py
    │   ├── gestion_liquidaciones.py
    │   ├── liquidacion_asesores.py
    │   ├── gestion_recaudos.py
    │   ├── gestion_desocupaciones.py
    │   ├── gestion_incidentes.py
    │   ├── gestion_seguros.py
    │   ├── recibos_publicos.py
    │   ├── saldos_a_favor.py
    │   ├── usuarios.py
    │   ├── gestion_ipc.py
    │   └── reportes.py
    ├── components/
    │   └── (potenciales componentes de UI reutilizables como botones de acción o filtros)
    └── styles.py (Para validación de z-index y pointer-events)
```

**Structure Decision**: El trabajo se centrará enteramente en refactorizar los componentes de UI (principalmente páginas bajo `src/presentacion_reflex/pages/` o componentes genéricos de filtros) para inyectar `rx.tooltip`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
