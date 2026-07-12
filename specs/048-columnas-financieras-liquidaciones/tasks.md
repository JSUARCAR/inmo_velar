# Tasks: Columnas Financieras Liquidaciones

**Input**: Design documents from `/specs/048-columnas-financieras-liquidaciones/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar el entorno y verificar que los campos existen en la base de datos

- [x] T001 Verificar que los 8 campos financieros existen en tabla LIQUIDACIONES de PostgreSQL ejecutando query de inspección de esquema
- [x] T002 [P] Ejecutar tests existentes del módulo liquidaciones para establecer baseline de regresión

**Checkpoint**: Entorno verificado, baseline de tests establecido

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Actualizar el modelo DTO y las consultas del repositorio (capas Domain y Infrastructure)

**⚠️ CRITICAL**: No se puede continuar con UI hasta completar esta fase

- [x] T003 [P] Agregar 8 campos financieros a LiquidacionDict en src/presentacion_reflex/state/liquidaciones_state.py (campos: otros_ingresos, gastos_administracion, gastos_servicios, gastos_reparaciones, valor_incidentes, pago_predial, otros_egresos, iva_comision con sus versiones _view)
- [x] T004 [P] Agregar lógica de formateo para los 8 campos en el método load_liquidaciones de src/presentacion_reflex/state/liquidaciones_state.py usando format_currency()
- [x] T005 Actualizar query SQL individual en src/infraestructura/persistencia/repositorio_liquidacion_postgres.py para incluir los 8 campos financieros en el SELECT
- [x] T006 Actualizar query SQL agrupada en src/infraestructura/persistencia/repositorio_liquidacion_postgres.py para incluir sumatorias de los 8 campos financieros

**Checkpoint**: Modelo DTO y repositorio listos - la UI puede consumir los nuevos campos

---

## Phase 3: User Story 1 - Visualización Completa de Datos Financieros (Priority: P1) 🎯 MVP

**Goal**: Mostrar las 8 nuevas columnas financieras en la tabla de liquidaciones después de la columna Canon

**Independent Test**: Cargar la tabla de liquidaciones y verificar que las 8 nuevas columnas aparecen con los datos correctos de PostgreSQL

### Implementation for User Story 1

- [x] T007 [P] [US1] Agregar encabezados de las 8 columnas financieras en liquidaciones_table() de src/presentacion_reflex/pages/liquidaciones.py usando header_cell_sortable() después de la columna Canon
- [x] T008 [P] [US1] Agregar celdas de las 8 columnas financieras en la fila de datos de liquidaciones_table() de src/presentacion_reflex/pages/liquidaciones.py renderizando liq["campo_view"]
- [x] T009 [P] [US1] Agregar encabezados de las 8 columnas financieras en liquidaciones_table_agrupada() de src/presentacion_reflex/pages/liquidaciones.py con headers "Total" para cada campo
- [x] T010 [P] [US1] Agregar celdas de las 8 columnas financieras en liquidaciones_table_agrupada() de src/presentacion_reflex/pages/liquidaciones.py
- [x] T011 [US1] Ejecutar `reflex run --env dev` y verificar visualmente que las columnas aparecen en el orden correcto después de Canon
- [x] T012 [US1] Verificar que valores nulos muestran $0,00 en la tabla

**Checkpoint**: User Story 1 completa - tabla muestra las 8 columnas financieras correctamente

---

## Phase 4: User Story 2 - Funcionalidades de Interacción con Columnas (Priority: P2)

**Goal**: Las nuevas columnas participan en ordenamiento, filtros y exportación

**Independent Test**: Ordenar por cada columna financiera, aplicar filtros por rango, exportar a Excel y verificar consistencia

### Implementation for User Story 2

- [x] T013 [P] [US2] Agregar handler de ordenamiento para las 8 columnas financieras en el método sort_liquidaciones de src/presentacion_reflex/state/liquidaciones_state.py
- [x] T014 [P] [US2] Agregar filtros por rango (mín/máx) para las 8 columnas financieras en src/presentacion_reflex/components/shared/advanced_filter_bar.py
- [x] T015 [P] [US2] Agregar lógica de filtrado por rango para columnas financieras en el método apply_filters de src/presentacion_reflex/state/liquidaciones_state.py
- [x] T016 [US2] Actualizar payload de exportación en src/presentacion_reflex/components/liquidaciones/export_modal.py para incluir los 8 campos financieros
- [x] T017 [US2] Verificar ordenamiento ascendente/descendente para cada columna financiera
- [x] T018 [US2] Verificar filtro por rango funciona correctamente con valores mínimo y máximo
- [x] T019 [US2] Verificar exportación a Excel incluye las 8 columnas con valores correctos

**Checkpoint**: User Story 2 completa - interacción funciona correctamente

---

## Phase 5: User Story 3 - Consistencia y Calidad Visual (Priority: P3)

**Goal**: Formato monetario uniforme y alineación consistente en todas las columnas

**Independent Test**: Verificar que todos los valores monetarios muestran formato correcto ($XX.XXX,XX) y están alineados

### Implementation for User Story 3

- [x] T020 [P] [US3] Verificar que format_currency() en src/presentacion_reflex/utils/formatters.py produce formato correcto ($XX.XXX,XX) para valores de 0 a 999,999,999
- [x] T021 [P] [US3] Aplicar alineación derecha (text_align="right") a las 8 columnas financieras en src/presentacion_reflex/pages/liquidaciones.py
- [x] T022 [US3] Verificar formato monetario en diferentes magnitudes: $0, $1, $1.000, $1.000.000, $100.000.000
- [x] T023 [US3] Verificar alineación visual en diferentes resoluciones de pantalla (desktop, tablet, mobile)
- [x] T024 [US3] Verificar scroll horizontal mantiene formato y alineación de columnas financieras

**Checkpoint**: User Story 3 completa - formato y alineación consistentes

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y validación final

- [x] T025 Ejecutar todos los tests existentes del módulo liquidaciones para verificar no hay regresiones
- [x] T026 [P] Verificar rendimiento de carga de tabla < 3 segundos con datos de prueba
- [x] T027 [P] Verificar que la tabla es visualmente consistente con otras tablas del sistema
- [x] T028 Ejecutar validación completa del quickstart.md
- [x] T029 [P] Actualizar documentación existente si aplica

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (uses same UI components)
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (verifies formatting)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (modifies same UI files)
- **User Story 3 (P3)**: Depends on User Story 1 (verifies formatting applied in US1)

### Within Each User Story

- Models/DTOs before UI components
- UI components before validation
- Core implementation before integration testing

### Parallel Opportunities

- T003 and T004 can run in parallel (different aspects of state)
- T007, T008, T009, T010 can run in parallel (different table functions)
- T013, T014, T015 can run in parallel (different interaction aspects)
- T020 and T021 can run in parallel (format verification and alignment)

---

## Parallel Example: User Story 1

```bash
# Launch all UI tasks for User Story 1 together:
Task: "T007 [P] [US1] Agregar encabezados columnas financieras en liquidaciones_table()"
Task: "T008 [P] [US1] Agregar celdas columnas financieras en liquidaciones_table()"
Task: "T009 [P] [US1] Agregar encabezados columnas financieras en liquidaciones_table_agrupada()"
Task: "T010 [P] [US1] Agregar celdas columnas financieras en liquidaciones_table_agrupada()"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently - tabla muestra 8 columnas
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) - Tabla con columnas
3. Add User Story 2 → Test independently → Deploy/Demo - Ordenamiento y filtros
4. Add User Story 3 → Test independently → Deploy/Demo - Formato perfecto
5. Polish → Final validation → Production ready

---

## Task Summary

| Phase | Tasks | Parallel [P] | Story |
|-------|-------|--------------|-------|
| Phase 1: Setup | 2 | 1 | - |
| Phase 2: Foundational | 4 | 2 | - |
| Phase 3: US1 (P1) | 6 | 4 | US1 |
| Phase 4: US2 (P2) | 7 | 3 | US2 |
| Phase 5: US3 (P3) | 5 | 2 | US3 |
| Phase 6: Polish | 5 | 2 | - |
| **Total** | **29** | **14** | - |

**MVP Scope**: Phases 1-3 (12 tasks) - Visualización de columnas

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Entity `Liquidacion` already has all 8 fields - no domain changes needed
- Database schema already has all 8 columns - no migrations needed
