# Implementation Plan: Liquidación de Propietarios requiere Contrato de Arrendamiento Activo

**Branch**: `076-liquidacion-requiere-arrendamiento` | **Date**: 2026-09-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/076-liquidacion-requiere-arrendamiento/spec.md`

## Summary

Reforzar el criterio de elegibilidad del módulo de Liquidación de Propietarios: además del Contrato de Mandato ACTIVO se exige un Contrato de Arrendamiento ACTIVO sobre la MISMA propiedad (identificador único del inmueble, nunca dirección/nombre). La regla debe residir en la lógica de negocio (capa Aplicación vía `ServicioFinanciero` + repositorio de arrendamiento) y aplicar de forma idéntica en generación individual y masiva, de modo que las combinaciones 2–5 de la matriz no produzcan liquidación. Incluye: (1) validación conjunta en `generar_liquidacion_mensual()`/`generar_liquidacion_propietario()` y filtrado de candidatos en las consultas del formulario individual y de la masiva; (2) reporte de auditoría de SOLO LECTURA de liquidaciones históricas generadas bajo la regla anterior, evaluadas contra el estado vigente en la fecha de generación, con criterios registrados y re-generable sin persistir resultados; (3) eliminación total de datos TEST mediante limpieza dirigida por bitácora de creación, re-ejecutable e idempotente, con cierre/verificación de las 5 combinaciones de la matriz.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Reflex (framework UI/state), psycopg2 (PostgreSQL driver), pytest (testing), `dateutil` (periodos)
**Storage**: PostgreSQL (Railway)
**Testing**: pytest (unitarios de dominio/aplicación), Playwright e2e (`tests/e2e/test_liquidaciones.py`, `tests/e2e/test_liquidaciones_playwright.py`)
**Target Platform**: Linux server (Railway deployment)
**Project Type**: web-application (Full-stack: Reflex frontend + Python backend, Clean Architecture `src/dominio` → `src/aplicacion` → `src/infraestructura` → `src/presentacion_reflex`)
**Performance Goals**: Generación masiva < 30s para ~100 propietarios (robustez prioritaria: no aborta por exclusiones, solo reporta omitidas/no elegibles). Reporte de auditoría completa (< 60s sobre volumen histórico del sistema actual). Limpieza TEST dirigida por bitácora < 10s.
**Constraints**: Regla en lógica de negocio (no solo UI); mismas rutas individual/masiva; mismo ID de propiedad entre mandato y arrendamiento; PostgreSQL nativo (`%s`, `RETURNING id`, sin sufijo `_sqlite.py`); 100% español; excepciones de dominio específicas (prohibido `except Exception` supresivo); Value Objects con `frozen=True`.
**Scale/Scope**: ~50 propiedades con contratos, ~20 propietarios, ~24 periodos de liquidación; 5 combinaciones de matriz como escenarios obligatorios.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Capas unidireccionales) | ✅ PASS | Regla de elegibilidad en Dominio/Aplicación; consultas en Infraestructura; presentación solo filtra opciones y consolida conteos |
| PostgreSQL Native (PLACEHOLDERS %s, RETURNING id) | ✅ PASS | Nuevas consultas usan `%s` de `db_manager.get_placeholder()` y `RETURNING id` |
| Prohibido sufijo `_sqlite.py` / SQLite / Flet | ✅ PASS | Sin nuevos repos `_sqlite`; la limpieza reutiliza el patrón Postgres de `limpiar_datos_prueba_pg.py` |
| Idioma 100% Español | ✅ PASS | Código, mensajes de negocio, docstrings y documentación en español |
| Value Objects con `frozen=True` | ✅ PASS | Resultado de elegibilidad como Value Object inmutable (similar a `ResultadoGeneracionPropietario`) |
| Type Hints obligatorios | ✅ PASS | Firmas completas en servicios, repositorios y Value Objects |
| Excepciones específicas (no `except Exception`) | ✅ PASS | Post-diseño: nueva excepción de dominio `LiquidacionNoElegibleError(ValueError)` para "inelegible"; no se agrega ningún `except Exception` nuevo; los no elegibles se clasifican en el Value Object extendido, no como errores |
| RBAC en operaciones core | ✅ PASS | Post-diseño: la feature NO introduce nuevas rutas/endpoints; reutiliza los handlers de generación existentes (con su RBAC vigente) y solo modifica lógica interna del servicio y consultas |
| Cobertura de tests > 90% lógica nueva | ✅ PASS | Dominio y aplicación nuevos con tests unitarios; e2e para la matriz 5×2 |
| Semantic Commits | ✅ PASS | `feat(liquidaciones): ...`, `feat(auditoria): ...`, `chore(limpieza): ...` |

**GATE**: ✅ PASS (con 2 pendientes de verificación en Phase 0: refinar manejo de excepciones sin `except Exception` nuevo y confirmar RBAC existente en los handlers).

## Project Structure

### Documentation (this feature)

```text
specs/076-liquidacion-requiere-arrendamiento/
├── plan.md              # Este archivo
├── spec.md              # Spec aprobada con 7 clarificaciones
├── research.md          # Phase 0: decisiones de diseño (elegibilidad, auditoría, limpieza)
├── data-model.md        # Phase 1: modelo de datos y bitácora TEST
├── quickstart.md        # Phase 1: matriz de validación 5 combinaciones × 2 rutas + auditoría + limpieza
├── contracts/           # Phase 1: contratos de interfaz
│   ├── servicio-financiero.md   # Elegibilidad en generación individual/masiva
│   ├── auditoria-elegibilidad.md # Reporte de solo lectura re-generable
│   └── limpieza-test.md          # Script de limpieza por bitácora (re-ejecutable/idempotente)
└── tasks.md             # Phase 2: tareas de implementación (generado por /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   ├── resultado_generacion.py          # YA EXISTE: ResultadoGeneracionPropietario
│   │   └── resultado_elegibilidad.py        # NUEVO: Value Object frozen con motivo de exclusión
│   ├── constantes/
│   │   └── estados_contrato.py              # YA EXISTE: EstadoContrato + es_activo()
│   ├── interfaces/
│   │   └── repositorio_arrendamiento.py     # YA EXISTE (verificar obtener_activo_por_propiedad)
│   └── excepciones/
│       └── excepciones_liquidacion.py       # NUEVO: LiquidacionNoElegibleError (dominio específica)
├── aplicacion/servicios/
│   ├── servicio_financiero.py               # FIX: validación conjunta en generar_liquidacion_mensual/propietario
│   ├── servicio_auditoria_elegibilidad.py   # NUEVO: reporte de solo lectura re-generable
│   └── servicio_contratos.py                # FIX (si aplica): listar_mandatos_ACTIVOs con arrendamiento activo
├── infraestructura/persistencia/
│   ├── repositorio_liquidacion_postgres.py  # FIX (si aplica): nuevas consultas de auditoría
│   └── repositorio_contrato_mandato_postgres.py  # FIX (si aplica): consulta elegibilidad conjunta
└── presentacion_reflex/state/
    ├── liquidaciones_state.py               # FIX: query_propiedades/propietarios con arrendamiento activo + contador no_elegibles + mensajes de negocio
    └── auditoria_state.py                   # NUEVO (o adicionar a liquidaciones_state): estado del reporte de auditoría re-generable

src/scripts/
└── limpiar_datos_test_bitacora_pg.py        # NUEVO: limpieza TEST idempotente dirigida por bitácora

tests/
├── unit/... (o tests/dominio, tests/aplicacion)
│   ├── test_resultado_elegibilidad.py       # NUEVO: matriz 5 combinaciones a nivel dominio
│   └── test_servicio_financiero_elegibilidad.py  # NUEVO: individual + masiva
└── e2e/
    ├── test_liquidaciones.py                # FIX: escenarios de la matriz
    └── test_liquidaciones_playwright.py     # FIX: flujo UI individual + masiva

docs/ (solo si aplica ADR)
```

**Structure Decision**: Se respeta la arquitectura en capas ya existente (`src/dominio|aplicacion|infraestructura|presentacion_reflex`). La regla de elegibilidad vive en el servicio de aplicación (`ServicioFinanciero`) apoyada en un Value Object de dominio (`ResultadoElegibilidad`) y una excepción de dominio (`LiquidacionNoElegibleError`); la infraestructura aporta consultas de arrendamiento activo por ID de propiedad (ya existe `obtener_activo_por_propiedad`); la presentación solo filtra candidatos en las consultas del formulario y consolida el conteo de no elegibles. La limpieza TEST es un script Postgres autónomo inspirado en `limpiar_datos_prueba_pg.py`, dirigido por la bitácora de creación, idempotente y con detención ante error.

## Complexity Tracking

> No hay violaciones de constitución que justificar. Los pendientes señalados (manejo de excepciones y RBAC) son refinamientos verificables en Phase 0/Implementación, no desviaciones estructurales.