# Implementation Plan: Auditoría y Corrección de Persistencia en Módulo de Contratos

**Branch**: `059-debug-contratos-persistence` | **Date**: 2026-07-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/059-debug-contratos-persistence/spec.md`

## Summary

Auditoría exhaustiva de ingeniería inversa del módulo de Contratos (Mandato y Arrendamiento) con corrección de bugs de persistencia identificados. El análisis reveló **3 bugs concretos** en el repositorio de Mandato que explican la pérdida de datos reportada: (1) campo `ENLACE_VIDEO` ausente en el UPDATE SQL, (2) campos `consignatario` y `documento_consignatario` sin fallback a mayúsculas en la lectura, y (3) campo `enlace_video` sin fallback a mayúsculas en la lectura. Corrección + tests de integración + documentación del mapeo campo-a-columna.

## Technical Context

**Language/Version**: Python 3.11+ (Reflex framework)
**Primary Dependencies**: Reflex (rx), psycopg2, Pydantic
**Storage**: PostgreSQL (CONTRATOS_MANDATOS, CONTRATOS_ARRENDAMIENTOS tables)
**Testing**: pytest + integration tests against PostgreSQL
**Target Platform**: Web application (Reflex SSR)
**Project Type**: Web application (Real Estate management system)
**Performance Goals**: N/A (debugging/fix task, not performance-critical)
**Constraints**: Must not break existing contract data; retroactive fix for existing records
**Scale/Scope**: ~30+ fields across 2 contract types, 2 repository files, 2 service files, 2 UI form files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Fix is in Infrastructure layer (repository), no cross-layer violations |
| PostgreSQL Native (%s placeholders, RETURNING id) | ✅ PASS | Existing queries already follow this pattern |
| snake_case / PascalCase naming | ✅ PASS | Existing code follows conventions |
| Type Hints obligatorios | ✅ PASS | Existing entities have type hints |
| Zero Guessing Policy | ✅ PASS | Bugs are identified with evidence |
| Stop-the-Line | ✅ PASS | This IS the stop-the-line fix |
| Atomic Changes | ✅ PASS | Fix is surgical (~5 lines per file) |
| Commit Conventions (Conventional Commits) | ✅ PASS | Will use `fix(infraestructura): ...` |

## Project Structure

### Documentation (this feature)

```text
specs/059-debug-contratos-persistence/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (persistence mapping)
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   ├── contrato_mandato.py          # Entity (no changes needed)
│   │   └── contrato_arrendamiento.py    # Entity (no changes needed)
│   └── repositorios/
│       └── interfaces.py                # Interfaces (no changes needed)
├── aplicacion/
│   └── servicios/
│       ├── servicio_contratos.py        # Facade (no changes needed)
│       ├── servicio_contrato_mandato.py # Service (no changes needed)
│       └── servicio_contrato_arrendamiento.py # Service (no changes needed)
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_contrato_mandato_postgres.py    # 🔧 FIX TARGET
│       └── repositorio_contrato_arrendamiento_postgres.py # ✅ Already correct
└── presentacion_reflex/
    ├── state/
    │   └── contratos_state.py           # State (verify no issues)
    └── components/contratos/
        ├── formulario_contrato_mandato.py    # UI Form (no changes needed)
        └── formulario_contrato_arrendamiento.py # UI Form (no changes needed)

tests/
└── integration/
    └── test_servicios_aplicacion/
        └── test_persistencia_contratos.py   # 🔧 NEW: Integration tests
```

**Structure Decision**: Fix is surgical — concentrated in the Mandato repository file. No structural changes needed.

## Complexity Tracking

No constitution violations to justify. The fix is a straightforward bug correction within existing architecture.
