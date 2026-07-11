# Tasks: Corrección valor_incidentes en Reportes

**Input**: Design documents from `/specs/044-fix-valor-incidentes-reportes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: No se solicitaron tests explícitos en la especificación. Las tareas de validación se incluyen como parte de cada fase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificación previa a la implementación

- [X] T001 Verificar que la columna VALOR_INCIDENTES existe en tabla LIQUIDACIONES de PostgreSQL
- [X] T002 Verificar que la entidad Liquidacion en src/dominio/entidades/liquidacion.py tiene el campo valor_incidentes
- [X] T003 Ejecutar baseline de rendimiento para reportes (medir tiempo actual de generación)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Análisis de causa raíz y preparación

**⚠️ CRITICAL**: No se puede implementar hasta completar esta fase

- [X] T004 Ejecutar ingeniería inversa en repositorio_reportes.py para mapear queries incompletas
- [X] T005 Documentar hallazgos en research.md (causa raíz identificada)

**Checkpoint**: Causa raíz documentada - se puede proceder con implementación

---

## Phase 3: User Story 1 - Visualización en Reporte de Liquidaciones (Priority: P1) 🎯 MVP

**Goal**: El Reporte de Liquidaciones muestra la columna valor_incidentes con valores correctos

**Independent Test**: Generar PDF de liquidación y verificar que la columna aparece con valor formateado

### Implementation for User Story 1

- [X] T006 [US1] Agregar COALESCE(l.VALOR_INCIDENTES, 0) AS "Valor_Incidentes" a la consulta SQL en obtener_reporte_liquidaciones() en src/infraestructura/persistencia/repositorio_reportes.py línea 269
- [X] T007 [US1] Verificar que el alias "Valor_Incidentes" es consistente con el formato de otros campos del reporte
- [X] T008 [US1] Ejecutar syntax check: python -m py_compile src/infraestructura/persistencia/repositorio_reportes.py

**Checkpoint**: Reporte de Liquidaciones ahora incluye valor_incidentes

---

## Phase 4: User Story 2 - Visualización en Reporte Financiero Consolidado (Priority: P1)

**Goal**: El Reporte Financiero Consolidado muestra valor_incidentes y NETO_A_PAGAR calculado correctamente

**Independent Test**: Generar CSV de reporte consolidado y verificar columna + cálculo correcto

### Implementation for User Story 2

- [X] T009 [P] [US2] Agregar COALESCE(l.VALOR_INCIDENTES, 0) AS "VALOR_INCIDENTES" a la consulta SQL en obtener_reporte_consolidado() en src/infraestructura/persistencia/repositorio_reportes.py línea 668
- [X] T010 [P] [US2] Actualizar constante HEADERS_REPORTE_CONSOLIDADO en src/aplicacion/servicios/servicio_reportes.py línea 55 para incluir "VALOR_INCIDENTES" después de "TOTAL_EGRESOS"
- [X] T011 [US2] Corregir cálculo de NETO_A_PAGAR en obtener_reporte_consolidado() línea 671-678: agregar COALESCE(l.VALOR_INCIDENTES, 0) a la resta
- [X] T012 [US2] Verificar correspondencia 1:1 entre HEADERS_REPORTE_CONSOLIDADO y columnas del SELECT SQL
- [X] T013 [US2] Ejecutar syntax check: python -m py_compile src/aplicacion/servicios/servicio_reportes.py

**Checkpoint**: Reporte Financiero Consolidado ahora incluye valor_incidentes con cálculo correcto

---

## Phase 5: User Story 3 - Consistencia de Formato Monetario (Priority: P2)

**Goal**: El formato de valor_incidentes es consistente con otros campos financieros

**Independent Test**: Comparar visualmente formato de valor_incidentes con comision_monto u otro campo

### Implementation for User Story 3

- [X] T014 [US3] Verificar que COALESCE(..., 0) maneja valores NULL correctamente (retorna 0)
- [X] T015 [US3] Verificar que el formato de presentación en UI (liquidacion_detail_modal.py línea 224) ya usa formato monetario correcto
- [X] T016 [US3] Ejecutar pruebas de integración: pytest tests/integration/test_reportes.py -v (si existe)

**Checkpoint**: Formato monetario consistente verificado

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validación final y limpieza

- [X] T017 Ejecutar pruebas unitarias: pytest tests/unit/dominio/test_liquidacion.py -v
- [X] T018 Ejecutar type checking: mypy src/infraestructura/persistencia/repositorio_reportes.py
- [X] T019 Ejecutar validación manual en navegador:
  1. Ejecutar `reflex run --env dev`
  2. Navegar a Liquidaciones → Generar PDF → Verificar campo Valor_Incidentes
  3. Navegar a Reportes → Consolidado → Generar CSV → Verificar columna VALOR_INCIDENTES
  4. Comparar valores con consulta SQL directa a PostgreSQL
- [X] T020 Ejecutar quickstart.md validation scenarios
- [X] T021 Verificar que NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES en ambas queries
- [X] T022 Crear commit con mensaje: fix(reportes): agregar valor_incidentes a reportes de liquidaciones y consolidado

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Phase 2 completion
  - US1 (Phase 3) and US2 (Phase 4) can run in parallel (diferentes archivos/secciones)
  - US3 (Phase 5) depende de US1 y US2 completados
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Phase 2 - Can run in parallel with US1 (diferentes archivos)
- **User Story 3 (P2)**: Depends on US1 and US2 completion (verificación de consistencia)

### Within Each User Story

- Implementation tasks before validation tasks
- Syntax check before integration testing
- Core implementation before manual validation

### Parallel Opportunities

- **T009 y T010** [P]: Pueden ejecutarse en paralela (diferentes archivos)
- **US1 y US2**: Pueden ejecutarse en paralela por diferentes desarrolladores
- **T017, T018** [P]: Pruebas independientes pueden ejecutarse en paralela

---

## Parallel Example: User Stories 1 y 2

```bash
# Desarrollador A: User Story 1 (Reporte de Liquidaciones)
Task: "T006 Agregar VALOR_INCIDENTES a obtener_reporte_liquidaciones()"
Task: "T007 Verificar consistencia de alias"
Task: "T008 Syntax check repositorio_reportes.py"

# Desarrollador B: User Story 2 (Reporte Financiero Consolidado)
Task: "T009 Agregar VALOR_INCIDENTES a obtener_reporte_consolidado()"
Task: "T010 Actualizar HEADERS_REPORTE_CONSOLIDADO"
Task: "T011 Corregir calculo NETO_A_PAGAR"
Task: "T012 Verificar correspondencia headers-SQL"
Task: "T013 Syntax check servicio_reportes.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verificaciones)
2. Complete Phase 2: Foundational (análisis causa raíz)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Generar PDF de liquidación y verificar campo
5. Deploy si está listo

### Incremental Delivery

1. Complete Setup + Foundational → Causa raíz documentada
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Polish → Validación completa → Commit final

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Una vez completada la fase Foundational:
   - Desarrollador A: User Story 1 (repositorio_reportes.py - obtener_reporte_liquidaciones)
   - Desarrollador B: User Story 2 (repositorio_reportes.py - obtener_reporte_consolidado + servicio_reportes.py)
3. Historias se completan e integran independientemente
4. Ambos hacen merge y verifican consistencia

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify syntax before integration testing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
