# Implementation Plan: Renovación de Contratos (Debug de casting de fechas)

**Branch**: working tree local | **Date**: 2026-09-13 | **Spec**: [spec.md](spec.md) | **Rama remota**: `072-renovacion-contratos-debug` (por crear en push)

**Input**: Feature specification from `/specs/072-renovacion-contratos-debug/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

El cliente reportó una falla durante las renovaciones de contratos. La investigación técnica (Phase 0) determinó que el error es un fallo de casting de fecha en PostgreSQL introducido durante `063-fix-canon-propagation`: los `RECAUDOS` y `LIQUIDACIONES` futuros pueden tener fechas vacías (`""`), que fallan al castearse con `""::date`, rompiendo toda la transacción de renovación. Además, los flujos de renovación construyen `RenovacionContrato` sin `fecha_inicio_renovacion` (el dataclass y el INSERT del repositorio ya incluyen la columna), persistiendo una fecha vacía en `RENOVACIONES_CONTRATOS`.

El alcance clarificado añade: (1) el incremento IPC aplica **solo** si `duracion_contrato_a >= 12` meses y existe valor IPC vigente; si no, incremento 0%; (2) a nivel de contrato/propiedad/mandato solo se actualiza el canon (comisión, IVA, totales y neto se recalculan como derivados en `LIQUIDACIONES`/`RECAUDOS` futuros); (3) excepción tipada `ContratoNoRenovableError` (FR-008); (4) sincronización del mandato activo más reciente ante múltiples activos (FR-009) y del canon estimado de la propiedad (FR-010); (5) idempotencia en ambos flujos respaldada en `IDEMPOTENCY_KEYS` (FR-011); (6) invalidación NO bloqueante de la caché de canon tras commit exitoso, tolerando data obsoleta temporal (FR-012); (7) cast seguro `NULLIF` alineado a las 6 queries del contrato 063 (FR-007). Atomicidad verificable: fallo inducido → sin estado parcial; reintento idempotente sin duplicados (SC-001). Auditoría solo de filas realmente modificadas (FR-002). Cobertura verificada por 7 casos + atomicidad (SC-001), test de concurrencia (CHK032) y suite de regresión completa (SC-003).

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex, psycopg2

**Storage**: PostgreSQL (único SGBD permitido por la constitución)

**Testing**: Pytest

**Target Platform**: Linux server (Railway)

**Project Type**: Web service (Reflex App)

**Performance Goals**: N/A

**Constraints**: Tipado estricto de PostgreSQL; `%s` como placeholder obligatorio; `NULLIF(campo,'')::date` para cast seguro de fechas vacías (también en queries Q1–Q6 del contrato 063); comparaciones con `>= date_trunc('month', %s::date)`; invalidación de caché NO bloqueante tras commit (FR-012); supuesto de transacción única sin deadlocks validado por test de concurrencia (CHK032); cumplimiento de cobertura de tests según constitución (dominio 100%, aplicación >90%).

**Scale/Scope**: Herramienta interna de Inmobiliaria Velar SAS

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **PostgreSQL Compliance**: Queries de fix usan `NULLIF(campo_fecha,'')::date` y `%s` placeholders; `NULLIF` es estándar y cumple en PostgreSQL. Solo PostgreSQL (sin SQLite ni Flet).
- [x] **Zero Guessing**: El error de fechas vacías se reprodujo y validó contra la BD local; hipótesis confirmadas leyendo el código real (`servicio_contrato_arrendamiento.py`, `servicio_contrato_mandato.py`).
- [x] **Clean Code (Typed Exceptions §2.2)**: `ContratoNoRenovableError` (dominio/excepciones) sustituye `ValueError`; corrección iterativa sin refactors masivos.
- [x] **Stop-the-line**: Se investigó la causa raíz (casting de fechas + constructor sin `fecha_inicio_renovacion`) en lugar de parchear síntomas.
- [x] **Idempotencia (FR-011)**: `@idempotent` presente en `renovar_arrendamiento`; se añadirá a `renovar_mandato`; respaldo DB-backed en `IDEMPOTENCY_KEYS` (entre sesiones/instancias, CHK031).
- [x] **Transaccionalidad (FR-003)**: actualización de canon, propagación y auditoría dentro de una transacción atómica con ROLLBACK.

## Project Structure

### Documentation (this feature)

```text
specs/072-renovacion-contratos-debug/
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
├── aplicacion/
│   ├── cache/
│   │   └── (invalidate_cache → infraestructura/cache/cache_manager.py)  # FR-012
│   ├── servicios/
│   │   ├── servicio_contrato_arrendamiento.py   # _ejecutar_renovacion_arrendamiento, propagación, @idempotent
│   │   └── servicio_contrato_mandato.py         # renovar_mandato + @idempotent (nuevo)
│   └── decorators/
│       └── idempotent.py                # decorador existente
├── dominio/
│   ├── excepciones.py                   # ContratoNoRenovableError (FR-008)
│   ├── servicios/
│   │   └── calculadora_contratos.py     # sumar_meses (bordes 31/fin de mes)
│   └── entidades/
│       └── renovacion_contrato.py       # fecha_inicio_renovacion en constructor (fix)
tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: La lógica vive íntegra en los servicios de aplicación (`servicio_contrato_arrendamiento.py`, `servicio_contrato_mandato.py`) y en la entidad de dominio `renovacion_contrato.py`. No se requieren cambios estructurales; los entregables son correcciones dentro de los archivos existentes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| `black --check` falla en 4 archivos tocados por la feature (`servicio_contrato_arrendamiento.py`, `servicio_contrato_mandato.py`, `servicio_contratos.py`, `repositorio_contrato_mandato_postgres.py`) — Constitución §5 | Los 4 archivos ya fallaban en HEAD (repo nunca fue black-formateado; 74/410 archivos de `src` sin formatear). El código de la feature sí cumple ruff/mypy sin errores nuevos. | Ejecutar black sobre los archivos completos generaría un diff de solo-formato de miles de líneas ajenas a la feature, violando §8 (cambios atómicos ~100 líneas) e imposibilitando la revisión del fix. Se pospone el formateo repo-wide a un cambio dedicado. |
| Cobertura de paquetes completa (dominio 64.86% / aplicación 30.78% vs §5: dominio 100% / nueva >90%) | Brecha de código legacy preexistente (no introducida por la feature). Todo el código nuevo de la feature tiene cobertura vía 51 tests verdes (dominio: `sumar_meses` 100% incl. rama de truncado, `calcular_fecha_inicio_renovacion`, `ContratoNoRenovableError`). | Escribir tests para los ~3.500 statements legacy de dominio/aplicación excede el alcance de la feature (spec Assumptions) y desbordaría el presupuesto de revisión. Se registra como deuda conocida en `tasks.md` (T026) para una feature de saneamiento de cobertura. |