# Implementation Plan: Grupo de pago correcto y atómico en la renovación de contratos

**Branch**: `075-fix-grupo-pago-renovacion` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/075-fix-grupo-pago-renovacion/spec.md`

## Summary

Corregir la causa raíz por la que la renovación de contratos no deja el grupo de pago correcto: (1) renovación de arrendamiento y de mandato nunca recalculan `grupo_operativo`/`fecha_pago`; (2) el repositorio de arrendamientos no mapea `GRUPO_OPERATIVO` al materializar la entidad y la escritura lo degrada a 0; (3) la renovación de mandato no está envuelta en una transacción, y la ruta de renovación quedó fuera de la solución de la feature 067.

La solución técnica: una **regla única de dominio** (tramos V2) aplicada sobre la **fecha efectiva del período vigente** (última renovación: `FECHA_RENOVACION DESC, ID DESC`; si no hay historial, inicio del contrato; el mandato sin renovaciones propias hereda el período del arrendamiento activo de la misma propiedad por FR-005), recalculada y persistida dentro de la **misma transacción** de la renovación en ambos tipos de contrato; corrección del mapeo de persistencia; y un **script de auditoría/remediación** en modo solo-lectura por defecto con `--commit` explícito y **compare-and-set** (las filas modificadas concurrentemente se omiten y reportan) que alinea todos los contratos ACTIVOS (mandatos y arrendamientos) y produce reporte antes/después.

## Technical Context

**Language/Version**: Python 3.12 (runtime del proyecto; Reflex >= 0.6 en `requirements.txt`)

**Primary Dependencies**: Reflex (UI), psycopg2-binary (acceso a datos), python-dotenv (configuración), pytest/pytest-cov (pruebas)

**Storage**: PostgreSQL (Railway/Cloud) — único motor soportado (constitución §1). Pool `ThreadedConnectionPool` con conexión por contexto (`ContextVar`) y transacciones gestionadas por `DatabaseManager.transaccion()` (`src/infraestructura/persistencia/database.py:460`)

**Testing**: pytest (configuración en `pytest.ini`, `pythonpath=.`); unitarias en `tests/unit/`, integración en `tests/integration/` con guarda `DATABASE_URL` (se omiten sin base configurada)

**Target Platform**: Servidor Linux (Railway) + desarrollo local Windows

**Project Type**: single project — Clean Architecture (`src/dominio`, `src/aplicacion`, `src/infraestructura`, `src/presentacion_reflex`) con UI Reflex

**Performance Goals**: Auditoría/remediación sobre la totalidad de contratos activos (cientos) en una pasada SQL + cálculo en memoria; sin metas de latencia (excluidas explícitamente por el spec)

**Constraints**: Solo PostgreSQL, sin cambios de esquema ni tipos de columna; una única transacción por renovación y por remediación; 100% español; dominio sin dependencias externas; prohibido `except Exception` supresivo (constitución §2.2); la corrección no debe alterar historia financiera cerrada

**Scale/Scope**: ~500 contratos activos (mandatos + arrendamientos), 2 entidades de contrato, 1 tabla de renovaciones, 1 script operativo, UI de contratos existente

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Mandato constitucional | Cumplimiento del plan |
|---|---|
| §2.1 Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | La regla de grupo/día vivirá en `src/dominio/servicios/calculadora_contratos.py` (sin dependencias externas); el cálculo de fecha efectiva se alimenta de repositorios vía interfaces (`src/dominio/repositorios/interfaces.py`); la UI no contiene reglas |
| §2.2 Nomenclatura español, snake_case, type hints, Google Style, excepciones de dominio | Métodos nuevos tipados con docstring Google; se reutiliza `ValorFueraDeRangoError`/`ContratoNoRenovableError`; sin `except Exception` supresivo en código nuevo (re-raise + rollback) |
| §2.3 PostgreSQL nativo (%s, `INSERT ... RETURNING`, tipos estrictos) | El script y los repositorios usan `get_placeholder()` (%s) y `get_dict_cursor`; `NULLIF(campo,'')::date` para fechas TEXT; cast seguro de tipos |
| §5 Pruebas: cobertura >90%, dominio 100%, tests de integración con BD de prueba | Unitarias de calculadora (100% reglas), unitarias de servicio/repositorio y de las funciones puras del script (T027), integración con `DATABASE_URL` y medición de cobertura con `pytest-cov` (T024); se ejecuta la suite existente de Contratos/Liquidaciones/Recaudos (SC-004) |
| §7 Zero Guessing | Ambigüedades resueltas en `/speckit.clarify` (6 decisiones registradas en el spec) |
| §8 Cambios atómicos (~100 líneas) | Se divide en: calculadora (dominio), mapeo repo, renovación arriendo, renovación mandato, script auditoría, pruebas |
| §13 Stop-the-line / corregir raíz y blindar con test de regresión | Cada defecto de raíz con test de regresión; la corrección no se limita al síntoma |
| §5/§11 Gate de calidad pre-commit (`check_syntax.py`, mypy, ruff, black) | Se ejecutan antes de cerrar la implementación; tests verdes |
| §15 Documentación dinámica (ADRs) | `research.md` documenta decisiones y alternativas descartadas; quickstart operativo |

**Resultado del gate**: PASS (sin violaciones; no se requiere Complexity Tracking).

**Re-evaluación post-diseño (Fase 1)**: PASS — los artefactos de diseño no introducen dependencias de dominio hacia capas superiores, no modifican esquema, mantienen PostgreSQL-only y delegan toda la regla de negocio en `CalculadoraContratos`; el script operativo queda fuera del runtime de la aplicación.

**Refinamientos posteriores (2026-09-21)**: (1) FR-001 sanciona la herencia del período del arriendo por el mandato sin renovaciones propias (ya reflejada en research R2, data-model §4 y contracts §3); (2) FR-010 incorpora **compare-and-set** en la remediación para no sobrescribir renovaciones concurrentes (reflejado en research R5, contracts/cli-remediacion.md y tasks T015); (3) la estrategia de pruebas incorpora unitarias de las funciones puras del script (T027) y medición de cobertura con `pytest-cov` (T024), conforme a la constitución §5. El plan permanece alineado con el spec; sin cambios de alcance.

## Project Structure

### Documentation (this feature)

```text
specs/075-fix-grupo-pago-renovacion/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones y alternativas
├── data-model.md        # Fase 1: entidades, campos y reglas
├── quickstart.md        # Fase 1: guía de validación ejecutable
├── contracts/           # Fase 1: contratos de interfaces internas y CLI
│   ├── contratos-dominio.md
│   ├── servicios-renovacion.md
│   └── cli-remediacion.md
└── tasks.md             # Fase 2 (/speckit.tasks — pendiente)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── servicios/calculadora_contratos.py                  # + regla única grupo/día (tramos V2)
│   └── excepciones/excepciones_base.py                     # reutilizadas (sin cambios)
├── aplicacion/
│   └── servicios/
│       ├── servicio_contrato_arrendamiento.py              # renovación: recalcula grupo/día + sync mandato
│       └── servicio_contrato_mandato.py                    # renovación: transacción + recalcula grupo/día
├── infraestructura/
│   └── persistencia/
│       └── repositorio_contrato_arrendamiento_postgres.py  # _row_to_entity mapea GRUPO_OPERATIVO
└── presentacion_reflex/state/contratos_state.py            # mensaje operativo de rollback (FR-008)

scripts/remediacion/
└── remediar_grupos_pago_v4.py                              # auditoría solo-lectura + --commit con compare-and-set (FR-009/FR-010)

tests/
├── unit/
│   ├── test_grupo_pago_reglas.py                           # calculadora: tramos, bordes, unificación
│   ├── test_renovacion_grupo_pago.py                       # servicios: recálculo en renovación (mock)
│   └── test_arriendo_repo_grupo_pago.py                    # mapeo de entidad → grupo (regresión)
└── integration/
    ├── test_renovacion_grupo_pago_atomico.py               # persistencia + atomicidad + idempotencia (BD)
    └── test_auditoria_grupos_pago.py                       # auditoría/remediación y limpieza TEST (BD)
```

**Structure Decision**: proyecto único existente; se respeta la arquitectura por capas y los patrones vigentes (repositorios `repositorio_*_postgres.py`, servicios por especialidad, scripts operativos en `scripts/`). No se crean módulos nuevos de arquitectura; solo un script operativo y pruebas.

## Complexity Tracking

> No hay violaciones a la constitución que justificar.
