# Implementation Plan: Recaudos - Filtros Avanzados y Ordenamiento de Tabla

**Branch**: `015-recaudos-filtros-sort` | **Date**: 2026-07-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-recaudos-filtros-sort/spec.md`

## Summary

Homologar la sección de Filtros Avanzados del módulo Recaudos con el módulo Liquidaciones, incorporando el filtro "Pago Contrato" (`neuro_select_root`), validando el filtro "Estado" existente, agregando un botón de limpiar filtros, implementando estados vacíos con `rx.callout`, y validando/corrigiendo el ordenamiento de todas las columnas de la tabla (excepto Acciones). La mayor parte de la infraestructura backend ya existe; el trabajo se concentra en la capa de presentación (UI + State).

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: Reflex >=0.6.0 (Web UI), Pydantic >=2.5.0 (validación)

**Storage**: PostgreSQL (producción) / SQLite (desarrollo) — sin cambios en esquema

**Testing**: pytest >=7.4.0, pytest-cov

**Target Platform**: Web application (browser)

**Project Type**: Web application (Clean Architecture: Dominio → Aplicación → Infraestructura → Presentación)

**Performance Goals**: Filtros y sorting con respuesta < 2 segundos; tabla hasta 10,000 registros sin degradación percibida < 3 segundos

**Constraints**: Sin cambios en backend (servicios, repositorios, DTOs); solo capa de presentación (UI + State)

**Scale/Scope**: ~10,000 registros de recaudos; módulo individual con ~630 líneas de UI y ~740 líneas de state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dependencias Unidireccionales) | ✅ PASS | Solo se modifica `src/presentacion_reflex/` (capa Presentación). Sin imports hacia capas superiores. |
| Consolidación Tecnológica (Reflex/PostgreSQL) | ✅ PASS | Se usa Reflex para UI. Sin referencias a Flet o SQLite. |
| 100% Español | ✅ PASS | Todo el código, UI, comentarios y documentación en español. |
| Type Hints obligatorios | ✅ PASS | Todos los componentes y handlers usan type hints. |
| Zero Guessing | ✅ PASS | Clarificaciones resueltas en spec (2 preguntas respondidas). |
| Componentes reutilizables | ✅ PASS | Se reusan `neuro_select_root`, `neuro_input`, `neuro_button` de `neuro_elements.py`. |
| Validación en Fronteras | ✅ PASS | Filtros validados en state antes de pasar al backend. |
| Clean Code (Claridad sobre Cleverness) | ✅ PASS | Cambios incrementales, sin over-engineering. |
| Commits Semver + Conventional | ⚠️ PENDING | Se aplicará al hacer commit: `feat(recaudos): ...` |

**Gate Result**: ✅ PASS — No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/015-recaudos-filtros-sort/
├── plan.md              # Este archivo
├── research.md          # Phase 0: decisiones técnicas
├── data-model.md        # Phase 1: modelo de datos
├── quickstart.md        # Phase 1: guía de validación
├── contracts/           # Phase 1: contratos de interfaz (N/A — sin API externa)
└── tasks.md             # Phase 2: (/speckit.tasks — no creado por /speckit.plan)
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── pages/
│   └── recaudos.py              # ← MODIFICAR: toolbar + tabla + empty state
├── state/
│   └── recaudos_state.py        # ← MODIFICAR: handlers de filtros + clear + sort validation
├── components/
│   ├── recaudos/
│   │   ├── __init__.py
│   │   ├── modal_form.py        # Sin cambios
│   │   └── detail_modal.py      # Sin cambios
│   ├── neuro_elements.py        # Sin cambios (reutilizar existentes)
│   └── shared/
│       └── searchable_select.py # Sin cambios
└── styles.py                    # Sin cambios

src/dominio/
├── entidades/recaudo.py         # Sin cambios
├── interfaces/repositorio_recaudo.py  # Sin cambios (FiltrosRecaudo ya soporta id_contrato)
└── constantes/recaudo.py        # Sin cambios

src/aplicacion/
├── servicios/servicio_recaudo.py  # Sin cambios
└── esquemas/recaudo.py            # Sin cambios

src/infraestructura/
└── persistencia/repositorio_recaudo.py  # Sin cambios (SORT_COLUMNS ya completo)
```

**Structure Decision**: Solo se modifican 2 archivos en la capa de Presentación: `recaudos.py` (UI) y `recaudos_state.py` (State). No hay cambios en otras capas.

## Complexity Tracking

> No hay violaciones constitucionales que justificar.
