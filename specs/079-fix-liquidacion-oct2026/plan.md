# Implementation Plan: Liquidación Propietarios Octubre 2026 Invisible

**Branch**: `079-fix-liquidacion-oct2026` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/079-fix-liquidacion-oct2026/spec.md`

## Summary

La liquidación masiva de octubre 2026 no aparece en la tabla porque `ServicioFinanciero.generar_liquidacion_propietario` lanza `KeyError: 'tiene_arriendo'` en PostgreSQL (el `UpperCaseCursorWrapper` devuelve claves en MAYÚSCULAS y el código accede el alias en minúsculas), de modo que la masiva cuenta todo como errores y persiste 0 filas. El fix es mínimo y ya validado: acceso dual a claves dict (Backend) + recarga incondicional con sincronización de `filter_periodo` tras la masiva (Frontend). Se preserva la diferencia LIKE vs = y la idempotencia por UNIQUE.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Reflex >=0.6.0 (presentación, soporte `@rx.event(background=True)`), psycopg2-binary >=2.9.0 + RealDictCursor / `UpperCaseCursorWrapper` (persistencia PG), Pydantic >=2.5 (DTOs/State). Rangos declarados en `requirements.txt`.

**Storage**: PostgreSQL en Railway (prod, `DATABASE_URL` con SSL); SQLite solo dev/test fallback.

**Testing & Test Universe**: pytest (unitarios `tests/aplicacion/test_servicio_financiero_elegibilidad.py`, dominio); universo de referencia de 64 contratos elegibles (79 mandatos activos, 64 arriendos activos al 2026-10-14); scripts de verificación contra PG con períodos TEST `2099-*` y borrado físico garantizado (`COUNT(*) = 0`).

**Target Platform**: Servidor Linux (Railway) + web Reflex

**Project Type**: Web application (backend servicios + frontend Reflex en el mismo repo)

**Performance Goals**: Consulta por período <5s para ~60-80 filas; generación masiva en background async sin límite explícito, con toast resumen al finalizar

**Constraints**: Placeholders PG `%s` únicamente; estado Reflex con mutaciones atómicas; cambios atómicos (~100 líneas); español 100%

**Scale/Scope**: ~79 mandatos activos, ~64 contratos elegibles, ~50 propietarios; 2 archivos fuente a modificar

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Capas unidireccionales: el fix vive en Aplicación (`servicio_financiero.py`) e Infraestructura-agnóstico + Presentación (`liquidaciones_state.py`); Dominio intacto.
- [x] PG nativo: `%s` preservado; sin sufijos `_sqlite`; sin referencias nuevas a Flet/SQLite en lógica de negocio.
- [x] Type hints y Google docstrings en firmas tocadas; sin `except` genérico supresivo nuevo (el `except Exception` por-propietario ya existía y se mantiene con conteo de errores).
- [x] Español 100% en código y docs.
- [x] Higiene: scripts de diagnóstico fuera de la raíz (`C:\Users\PC\AppData\Local\Temp\opencode`, pre-aprobado); cero filtraciones (`.env` nunca en diffs).
- [x] Stop-the-Line: causa raíz reproducida antes de corregir; tests de regresión ejecutados.
- [x] Cambios atómicos: 2 archivos, ~30 líneas netas.

Gates: PASS sin violaciones; Complexity Tracking vacío.

## Project Structure

### Documentation (this feature)

```text
specs/079-fix-liquidacion-oct2026/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── servicio-generacion.md
│   └── evento-masiva.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── aplicacion/servicios/servicio_financiero.py   # generar_liquidacion_propietario (fix dual-key)
├── presentacion_reflex/state/liquidaciones_state.py  # generar_liquidacion_masiva (reload + filter sync)
├── dominio/entidades/liquidacion.py
├── dominio/entidades/resultado_generacion.py
└── infraestructura/persistencia/repositorio_liquidacion_postgres.py  # solo lectura, sin cambios

tests/
├── aplicacion/test_servicio_financiero_elegibilidad.py  # regresión existente
└── dominio/test_liquidacion_asesor.py
```

**Structure Decision**: fix quirúrgico en 2 archivos existentes; sin archivos nuevos en `src/`; artefactos de validación como scripts efímeros fuera del repo.

## Complexity Tracking

> N/A — sin violaciones al Constitution Check.
