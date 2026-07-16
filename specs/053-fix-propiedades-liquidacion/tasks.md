# Tasks: Fix Propiedades a Liquidar

**Input**: Design documents from `/specs/053-fix-propiedades-liquidacion/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Diagnóstico y Análisis (Foundational)

**Purpose**: Confirmar el problema raíz mediante inspección directa del código y datos

- [ ] T001 Leer y analizar la consulta actual en `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py` método `obtener_activos_por_asesor()` (líneas 107-133) para documentar las condiciones exactas de filtrado
- [ ] T002 Ejecutar consulta SQL directa en PostgreSQL para contar contratos activos del asesor CRISTIAN JAMIOY y comparar con el resultado del método del repositorio
- [ ] T003 Leer el método `obtener_activos_todos_agrupados()` en el mismo archivo (líneas 135-174) para verificar si tiene el mismo problema

**Checkpoint**: Problema raíz confirmado con evidencia numérica

---

## Phase 2: Corrección de la Consulta SQL (US1 - Generación correcta)

**Goal**: Corregir la consulta `obtener_activos_por_asesor()` para que retorne TODOS los contratos activos del asesor

**Independent Test**: Seleccionar asesor CRISTIAN JAMIOY y verificar que la consulta retorna 46 propiedades

### Implementation

- [ ] T004 [US1] Corregir la consulta SQL en `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py` método `obtener_activos_por_asesor()` — aplicar `DISTINCT ON (ca.ID_CONTRATO_A)` con `ORDER BY ca.ID_CONTRATO_A, cm.ID_CONTRATO_M DESC` para evitar duplicados por múltiples mandatos históricos
- [ ] T005 [US1] Verificar que la consulta corregida usa placeholders `%s` (no `?`) y mantiene los filtros `ca.ESTADO_CONTRATO_A = 'ACTIVO'` y `cm.ESTADO_CONTRATO_M = 'ACTIVO'`
- [ ] T006 [US1] Revisar el método `obtener_activos_todos_agrupados()` en el mismo archivo para aplicar la misma corrección si tiene el mismo patrón de JOIN

**Checkpoint**: Consulta SQL corregida — retorna la cantidad correcta de contratos

---

## Phase 3: Consistencia Backend-Frontend (US1 + US2)

**Goal**: Asegurar que el frontend reciba y muestre todos los contratos retornados por el repositorio

**Independent Test**: Generar liquidación para CRISTIAN JAMIOY y verificar que la tabla de propiedades muestra 46 registros

### Implementation

- [x] T007 [US1] Revisar `src/presentacion_reflex/state/liquidacion_asesores/form_state.py` método `fetch_advisor_properties()` (líneas 461-525) para confirmar que recibe y procesa correctamente la lista completa de contratos del repositorio
- [x] T008 [US1] Revisar `src/presentacion_reflex/state/liquidacion_asesores/form_state.py` método `handle_save_form()` (líneas 166-268) para confirmar que la lista de contratos enviada al servicio no tiene filtros adicionales
- [x] T009 [US2] Revisar `src/presentacion_reflex/components/liquidacion_asesores/modal_form.py` para verificar que no existen restricciones de renderizado, paginación o límites de filas en la tabla de propiedades
- [x] T010 [P] [US2] Revisar componentes de tabla en `src/presentacion_reflex/components/liquidacion_asesores/` para verificar que no hay truncamiento de datos

**Checkpoint**: Backend y frontend alineados — todos los contratos se muestran en la UI

---

## Phase 4: Validación de Integridad de Datos (US3)

**Goal**: Garantizar que la cantidad de contratos en la liquidación coincida con PostgreSQL

**Independent Test**: Generar liquidación y comparar conteo en UI vs. consulta SQL directa

### Implementation

- [x] T011 [US3] Revisar el método `generar_liquidacion_multi_contrato()` en `src/aplicacion/servicios/servicio_liquidacion_asesores.py` (líneas 214-382) para confirmar que procesa TODOS los contratos de la lista recibida
- [x] T012 [US3] Revisar el método `guardar_contratos_liquidacion()` para confirmar que almacena TODOS los contratos procesados en la tabla `LIQUIDACIONES_CONTRATOS`
- [x] T013 [US3] Verificar que la consulta `obtener_contratos_de_liquidacion()` en `src/infraestructura/repositorios/repositorio_liquidacion_asesor.py` retorna todos los contratos almacenados

**Checkpoint**: Integridad de datos garantizada entre creación y consulta

---

## Phase 5: Comportamiento Universal y Edge Cases (US4)

**Goal**: Verificar que la corrección funciona para todos los asesores y maneja edge cases

**Independent Test**: Probar con múltiples asesores (1 contrato, muchos contratos, sin contratos)

### Implementation

- [ ] T015 [US4] Verificar que la restricción UNIQUE `UNIQUE(ID_ASESOR, PERIODO_LIQUIDACION)` previene duplicados a nivel de BD
- [ ] T016 [US4] Verificar que la lógica de soft delete (`ELIMINADA = FALSE`) permite reincorporación de contratos tras eliminación de liquidación
- [ ] T017 [P] [US4] Revisar `generar_liquidaciones_masivas_optimizado()` en `src/aplicacion/servicios/servicio_liquidacion_asesores.py` (líneas 830-910) para confirmar que usa la misma lógica corregida

**Checkpoint**: Todos los asesores obtienen resultados correctos — edge cases manejados

---

## Phase 6: Validación y Regresión (Cross-Cutting)

**Goal**: Ejecutar validaciones completas y verificar ausencia de regresiones

**Independent Test**: Seguir escenarios del quickstart.md

### Implementation

- [ ] T018 Ejecutar validación 1 del quickstart.md — consulta SQL directa para CRISTIAN JAMIOY
- [ ] T019 Ejecutar validación 2 del quickstart.md — generación de liquidación individual
- [ ] T020 Ejecutar validación 3 del quickstart.md — asesor con único contrato
- [ ] T021 Ejecutar validación 4 del quickstart.md — asesor con contratos mixtos
- [ ] T022 Ejecutar validación 5 del quickstart.md — contratos ya liquidados y reincorporación
- [ ] T023 Ejecutar validación 6 del quickstart.md — consistencia backend-UI
- [ ] T024 Ejecutar validación 7 del quickstart.md — generación masiva
- [ ] T025 Ejecutar checklist de regresión del quickstart.md — verificar que funcionalidad existente no se afectó

**Checkpoint**: Fix validado — sin regresiones

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Diagnóstico)**: No dependencies — start immediately
- **Phase 2 (Corrección SQL)**: Depends on Phase 1 confirmation — BLOCKS Phases 3-6
- **Phase 3 (Backend-Frontend)**: Depends on Phase 2 — can run in parallel with Phase 4
- **Phase 4 (Integridad)**: Depends on Phase 2 — can run in parallel with Phase 3
- **Phase 5 (Universal)**: Depends on Phases 3 and 4
- **Phase 6 (Validación)**: Depends on all previous phases

### User Story Dependencies

- **US1 (Generación correcta)**: Core fix — depends on Phase 1 diagnostic
- **US2 (Visualización UI)**: Independent from US1 backend fix, but benefits from it
- **US3 (Integridad datos)**: Depends on US1 fix being in place
- **US4 (Comportamiento universal)**: Depends on US1, US3 being complete

### Parallel Opportunities

- T001, T002, T003 can run in parallel (Phase 1)
- T004, T005, T006 are sequential (same file)
- T007, T008 can run in parallel with T009, T010 (different files)
- T011, T012, T013 are sequential (same flow)
- T014, T015, T016, T017 can run in parallel (different concerns)

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Diagnóstico
2. Complete Phase 2: Corrección SQL (THE FIX)
3. **STOP and VALIDATE**: Verificar que CRISTIAN JAMIOY obtiene 46 propiedades
4. Deploy fix si es validado

### Full Delivery

1. Phase 1 → Confirmar problema
2. Phase 2 → Corregir consulta
3. Phase 3 → Verificar frontend
4. Phase 4 → Verificar integridad
5. Phase 5 → Verificar edge cases
6. Phase 6 → Validación completa + regresión

---

## Notes

- Este es un **bug fix**, no un feature nuevo. Las tareas se enfocan en corrección, no creación.
- El cambio principal está en UN archivo: `repositorio_contrato_arrendamiento_postgres.py`
- Los demás archivos son de revisión/verificación, no de implementación.
- Commits después de cada fase completada.
- Si el fix de Phase 2 resuelve el problema, las fases 3-5 son de verificación, no de código.
