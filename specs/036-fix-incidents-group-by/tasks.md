# Tasks: Corrección GROUP BY en Módulo Incidentes

**Input**: Design documents from `/specs/036-fix-incidents-group-by/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No tests explicitly requested in specification. Validation via EXPLAIN ANALYZE and manual verification.

**Organization**: Tasks organized by user story. US1 and US2 are tightly coupled (same fix). US3 is a separate validation phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths included in descriptions

## Phase 1: Setup (No-op — Existing Project)

**Purpose**: No setup required. Existing project structure is already in place.

*Skip — no initialization tasks needed for a bug fix in an existing codebase.*

---

## Phase 2: Foundational (Cadena de Datos Completa)

**Purpose**: Verify the full data chain before applying the fix

**⚠️ CRITICAL**: The defect search scope covers repository → service → Reflex state (SC-008)

- [x] T001 [P] Trace the data chain from Reflex state `src/presentacion_reflex/state/incidentes/incidentes_base.py` through service `src/aplicacion/servicios/servicio_incidentes.py` to repository `src/infraestructura/persistencia/repositorio_incidentes_postgres.py` to confirm the defect is isolated to the `listar_con_filtros` method in the repository layer
- [x] T002 [P] Verify that `obtener_por_id` in `src/infraestructura/persistencia/repositorio_incidentes_postgres.py` (lines 157-215) works correctly (uses subqueries instead of LATERAL JOIN, no GROUP BY issue)
- [x] T003 [P] Verify that `servicio_incidentes.py` method `listar_con_filtros` (lines 128-155) delegates correctly to the repository without transformation

**Checkpoint**: Data chain traced. Defect confirmed isolated to repository `listar_con_filtros`.

---

## Phase 3: User Story 1 — Carga Exitosa de Incidentes (Priority: P1) 🎯 MVP

**Goal**: El módulo Incidentes carga la lista sin errores de GROUP BY y muestra cotizaciones correctamente.

**Independent Test**: Navegar al módulo Incidentes y verificar que la lista carga sin errores y muestra registros con sus cotizaciones.

### Implementation for User Story 1

- [x] T004 [US1] Eliminar la cláusula `GROUP BY` redundante en `src/infraestructura/persistencia/repositorio_incidentes_postgres.py` línea 398: `query += " GROUP BY I.ID_INCIDENTE, PER_PROV.ID_PERSONA, PROP.ID_PROPIEDAD, PER_PROP.ID_PERSONA, PER_INQ.ID_PERSONA, PER_HAB.ID_PERSONA"` — Esta línea causa el error porque `cot.cotizaciones` (derivada del LEFT JOIN LATERAL) no está en el GROUP BY ni en función de agregación. Los LATERAL JOINs ya manejan la agregación correctamente.
- [x] T005 [US1] Ejecutar `EXPLAIN ANALYZE` en la consulta corregida contra PostgreSQL para validar que: (1) no hay error de GROUP BY, (2) el plan usa Index Scan en INCIDENTES, (3) el tiempo es < 3 segundos
- [x] T006 [US1] Verificar en la UI que el módulo Incidentes carga correctamente: la lista muestra incidentes, las cotizaciones aparecen asociadas a cada incidente, y no hay errores en consola del navegador

**Checkpoint**: Módulo Incidentes carga sin errores. Cotizaciones se muestran correctamente.

---

## Phase 4: User Story 2 — Integridad de Datos en Consulta (Priority: P1)

**Goal**: La consulta SQL cumple completamente con las reglas de PostgreSQL y retorna datos consistentes.

**Independent Test**: Ejecutar la consulta SQL directamente contra la base de datos y verificar que retorna resultados sin errores, sin duplicación, y con arrays vacíos para incidentes sin cotizaciones.

### Implementation for User Story 2

- [x] T007 [US2] Validar que la consulta corregida (sin GROUP BY) retorna exactamente una fila por incidente — ejecutar `SELECT COUNT(DISTINCT I.ID_INCIDENTE) FROM INCIDENTES I LEFT JOIN LATERAL (...) cot ON TRUE` y comparar con `SELECT COUNT(*) FROM INCIDENTES`
- [x] T008 [US2] Validar que incidentes sin cotizaciones retornan `[]` (array vacío JSON), no `null` — ejecutar consulta con filtro `WHERE NOT EXISTS (SELECT 1 FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE)` y verificar campo COTIZACIONES_JSON
- [x] T009 [US2] Validar que incidentes con múltiples cotizaciones muestran todas las cotizaciones en el JSON sin duplicación — ejecutar consulta para un incidente con ≥ 3 cotizaciones y verificar el JSON retornado

**Checkpoint**: Integridad de datos verificada. Sin duplicación. Arrays vacíos correctos.

---

## Phase 5: User Story 3 — Rendimiento de Consulta (Priority: P2)

**Goal**: La consulta cumple el objetivo de < 3 segundos para 1000 registros y usa índices adecuados.

**Independent Test**: Ejecutar EXPLAIN ANALYZE y verificar tiempo < 3s y uso de índices.

### Implementation for User Story 3

- [x] T010 [US3] Ejecutar `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` en la consulta completa con 1000+ registros y documentar: tiempo total, plan de ejecución, uso de índices vs sequential scans
- [x] T011 [US3] Verificar que el plan de ejecución muestra `Index Scan` en `INCIDENTES` (no `Seq Scan`). Si hay `Seq Scan`, evaluar si se necesita un índice adicional en la tabla COTIZACIONES para `ID_INCIDENTE`
- [x] T012 [US3] Agregar log de tiempo de ejecución en el método `listar_con_filtros` de `src/infraestructura/persistencia/repositorio_incidentes_postgres.py` usando el logger existente `_log.debug()` para monitoreo en producción

**Checkpoint**: Rendimiento validado < 3s. Índices verificados. Observabilidad agregada.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación de regresiones y validación final

- [x] T013 [P] Verificar módulo Liquidaciones: navegar al módulo, cargar lista, verificar que los datos de incidentes se muestran correctamente en `src/presentacion_reflex/components/liquidaciones/modal_seleccion_incidentes.py`
- [x] T014 [P] Ejecutar validación completa de quickstart.md: escenarios EV-001 a EV-006
- [x] T015 Ejecutar linting: `python -m ruff check src/infraestructura/persistencia/repositorio_incidentes_postgres.py`
- [x] T016 Ejecutar type checking: `python -m mypy src/infraestructura/persistencia/repositorio_incidentes_postgres.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No-op — skip
- **Foundational (Phase 2)**: No dependencies — start immediately
- **US1 (Phase 3)**: Depends on Phase 2 completion (data chain traced)
- **US2 (Phase 4)**: Depends on T004 (fix applied) — can run in parallel with US1 validation
- **US3 (Phase 5)**: Depends on T004 (fix applied) — can run in parallel with US1/US2
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Core fix — applies the GROUP BY removal
- **US2 (P1)**: Data validation — depends on US1 fix being applied
- **US3 (P2)**: Performance — depends on US1 fix being applied, independent of US2
- **US1 and US2 can be validated in parallel** after T004
- **US3 can be validated in parallel** with US1/US2

### Parallel Opportunities

```bash
# Phase 2: Foundational tasks in parallel
Task: "T001 Trace data chain"
Task: "T002 Verify obtener_por_id"
Task: "T003 Verify service delegation"

# After T004 (fix applied): US2 + US3 validation in parallel
Task: "T007 Validate no duplication"
Task: "T008 Validate empty arrays"
Task: "T009 Validate multiple cotizaciones"
Task: "T010 EXPLAIN ANALYZE performance"
Task: "T011 Verify index usage"

# Phase 6: Regression checks in parallel
Task: "T013 Verify Liquidaciones"
Task: "T014 Run quickstart validation"
```

---

## Implementation Strategy

### MVP First (US1 Only — Critical Path)

1. Complete Phase 2: Trace data chain (T001-T003)
2. Complete Phase 3: Apply fix (T004) + validate (T005-T006)
3. **STOP and VALIDATE**: Module loads without errors
4. Deploy to staging/production

### Incremental Delivery

1. Phase 2 → Data chain traced → Foundation ready
2. Phase 3 → Fix applied → Module loads (MVP!)
3. Phase 4 → Data integrity verified → Complete confidence
4. Phase 5 → Performance validated → Production-ready
5. Phase 6 → Regression checks → Full release

### Time Estimate

- **Total estimated effort**: ~2-3 hours
- **Critical path**: T001 → T004 → T005 → T006 (~1 hour)
- **Full validation**: +1-2 hours for US2, US3, and regression checks

---

## Notes

- This is a **targeted bug fix**, not a feature build. Tasks are minimal and focused.
- The core fix is a **single line deletion** (T004). All other tasks are validation.
- No test tasks included per specification (validation via EXPLAIN ANALYZE and manual testing).
- The fix has been analyzed: `GROUP BY` on line 398 is redundant because `LEFT JOIN LATERAL` with `JSON_AGG` already handles aggregation correctly.
