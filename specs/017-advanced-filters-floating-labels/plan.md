# Implementation Plan: Estandarización de Filtros Avanzados con Floating Labels

**Branch**: `017-advanced-filters-floating-labels` | **Date**: 2026-07-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-advanced-filters-floating-labels/spec.md`

## Summary

Reemplazar placeholders por etiquetas flotantes (Floating Labels) en todos los campos de filtro avanzado de 13 módulos del sistema inmobiliario. El sistema ya cuenta con componentes reutilizables (`floating_input`, `floating_select`, `neuro_floating_input`, `neuro_floating_select`) que implementan el patrón CSS-only. La implementación consiste en migrar cada módulo para usar estos componentes existentes, eliminando `neuro_input`/`neuro_select_root` con placeholders y migrando módulos raw (Seguros, Saldos a Favor, Reportes) a componentes neumórficos con floating labels.

## Technical Context

**Language/Version**: Python 3.11+, Reflex 0.6.x

**Primary Dependencies**: Reflex (rx), existing neumorphic design system (`neuro_elements.py`), existing floating label components (`shared/floating_label.py`)

**Storage**: N/A (UI-only change, no database modifications)

**Testing**: Manual visual verification + Playwright browser tests (existing `playwright_test.py`)

**Target Platform**: Web application (desktop, tablet, mobile responsive)

**Project Type**: Web application (Reflex/Python full-stack)

**Performance Goals**: Transitions 150-300ms, no render regression

**Constraints**: Must use existing `neuro_floating_input`/`neuro_floating_select` components, preserve all existing filter behavior, maintain neumorphic design consistency

**Scale/Scope**: 13 modules, ~45 filter fields across the system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| 100% Español | PASS | All code, UI, comments in Spanish |
| Clean Architecture | PASS | Changes confined to Presentación layer only |
| Design System | PASS | Using existing neumorphic tokens (NEU_*, FL_*) |
| Zero Guessing | PASS | All requirements from spec, no speculation |
| Atomic Changes | PASS | Changes are small per-module (~10-30 lines each) |
| No Deferred Cleanup | PASS | Migrating raw components to standard during this change |

**Gate Result**: PASS - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/017-advanced-filters-floating-labels/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── components/
│   ├── neuro_elements.py          # MODIFY: neuro_floating_input, neuro_floating_select (already exist)
│   └── shared/
│       └── floating_label.py      # REFERENCE: floating_input, floating_select (already exist)
├── pages/
│   ├── personas.py                # MODIFY: Replace placeholders with floating labels
│   ├── propiedades.py             # MODIFY: Replace placeholders with floating labels
│   ├── contratos.py               # MODIFY: Replace placeholders with floating labels
│   ├── liquidaciones.py           # MODIFY: Replace placeholders with floating labels
│   ├── liquidacion_asesores.py    # MODIFY: Replace placeholders with floating labels
│   ├── recaudos.py                # MODIFY: Replace placeholders with floating labels
│   ├── desocupaciones.py          # MODIFY: Migrate raw rx.select to neuro_floating_select
│   ├── incidentes.py              # MODIFY: Replace placeholders with floating labels
│   ├── seguros.py                 # MODIFY: Migrate raw rx.input/rx.select to neuro_ components
│   ├── recibos.py                 # MODIFY: Replace placeholders with floating labels
│   ├── saldos_favor.py            # MODIFY: Migrate raw rx.select to neuro_floating_select
│   ├── usuarios.py                # MODIFY: Replace placeholders with floating labels
│   └── reportes.py                # MODIFY: Migrate raw rx.input/rx.select to neuro_ components
└── styles.py                      # REFERENCE: FL_* tokens (already exist)
```

**Structure Decision**: Single project structure. All changes confined to `src/presentacion_reflex/pages/` (page modules) with no changes to `neuro_elements.py` or `floating_label.py` (components already exist and are correct).

## Complexity Tracking

No constitution violations. No complexity justifications needed.

## Phase 0: Research

See `research.md` for full research output. Key decisions:

1. **Component Selection**: Use `neuro_floating_input` for text/date inputs, `neuro_floating_select` for dropdowns
2. **Migration Strategy**: In-place replacement of `neuro_input`→`neuro_floating_input` and `neuro_select_root`→`neuro_floating_select`
3. **Raw Component Migration**: Seguros, Saldos a Favor, Reportes need import changes + component swap
4. **State Compatibility**: No state changes needed; existing `value`/`on_change` bindings work with floating components
5. **Accessibility**: Existing `floating_input`/`floating_select` already use `<label>` with `html_for` for screen reader support

## Phase 1: Design & Contracts

See `data-model.md` for entity analysis. See `contracts/component-api.md` for component interface contracts.

Key design decisions:
- **No new components needed**: Existing `neuro_floating_input` and `neuro_floating_select` are sufficient
- **No state changes**: All filter state vars remain unchanged
- **Import additions only**: Pages using raw components need `from ...neuro_elements import neuro_floating_input, neuro_floating_select`
- **Placeholder strategy**: Keep existing placeholder text as `placeholder=" "` (space) for CSS focus selector, labels provide the visible text

## Phase 2: Tasks

See `tasks.md` for the full task breakdown (generated by `/speckit.tasks`).
