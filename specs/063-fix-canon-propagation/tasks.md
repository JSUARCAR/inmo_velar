# Tasks: Corrección de Propagación de Canon en Renovaciones

**Input**: Design documents from `/specs/063-fix-canon-propagation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No se incluyen tasks de tests (no solicitados en la especificación)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar el entorno de desarrollo y dependencias necesarias

- [x] T001 Verificar que el script de auditoría existente funciona correctamente ejecutando `python scripts/diagnostico/audit_renovaciones_2026.py`
- [x] T002 [P] Revisar la estructura actual de `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` para entender el cascade sync existente
- [x] T003 [P] Revisar la estructura de tablas LIQUIDACIONES y RECAUDOS en el esquema de base de datos

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparar las consultas SQL y estructura de datos que serán utilizadas por todas las user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Definir las consultas SQL de actualización para LIQUIDACIONES y RECAUDOS en `specs/063-fix-canon-propagation/contracts/sql-queries.md`
- [x] T005 Verificar que los campos `canon_bruto` (LIQUIDACIONES) y `valor_total` (RECAUDOS) existen y son actualizables
- [x] T006 Definir la función de utilidad para obtener el ID de mandato desde un contrato de arrendamiento

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Propagación Automática de Canon en Renovación (Priority: P1) 🎯 MVP

**Goal**: Cuando un contrato se renueva, el sistema actualiza automáticamente `canon_bruto` en LIQUIDACIONES y `valor_total` en RECAUDOS para registros futuros, preservando registros históricos.

**Independent Test**: Ejecutar una renovación de contrato y verificar que liquidaciones y recaudos futuros tienen el nuevo canon, mientras que los históricos permanecen intactos.

### Implementation for User Story 1

- [x] T007 [US1] Agregar método `actualizar_canon_liquidaciones_futuras` en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` que actualice `canon_bruto` donde `fecha_generacion::date > fecha_renovacion`
- [x] T008 [US1] Agregar método `actualizar_valor_recaudos_futuros` en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` que actualice `valor_total` donde `fecha_pago::date > fecha_renovacion`
- [x] T009 [US1] Integrar llamadas a los nuevos métodos en el flujo de cascade sync existente (después de actualizar Mandatos y Propiedades)
- [x] T010 [US1] Envolver las actualizaciones de LIQUIDACIONES y RECAUDOS en una transacción atómica con rollback completo
- [x] T011 [US1] Agregar logging de auditoría para cada actualización realizada (FR-009)

**Checkpoint**: At this point, User Story 1 should be fully functional - las renovaciones propagan correctamente el canon a Liquidaciones y Recaudos

---

## Phase 4: User Story 2 - Verificación de Integridad Post-Renovación (Priority: P2)

**Goal**: Proporcionar un mecanismo de verificación que valide que la propagación del canon se realizó correctamente, identificando inconsistencias.

**Independent Test**: Ejecutar el script de auditoría y verificar que detecta inconsistencias entre contratos, liquidaciones y recaudos.

### Implementation for User Story 2

- [x] T012 [P] [US2] Agregar método `verificar_propagacion_canon` en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- [x] T013 [US2] Implementar lógica para comparar `canon_bruto` de LIQUIDACIONES futuras contra `canon_arrendamiento` del contrato
- [x] T014 [US2] Implementar lógica para comparar `valor_total` de RECAUDOS futuros contra `canon_arrendamiento` del contrato
- [x] T015 [US2] Generar reporte de inconsistencias con severidad (ALTA, MEDIA, BAJA) y detalles del registro afectado
- [x] T016 [US2] Actualizar script de auditoría `scripts/diagnostico/audit_renovaciones_2026.py` para incluir verificación de integridad post-renovación

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Corrección Manual de Canon en Registros Futuros (Priority: P3)

**Goal**: Cuando se detecta una inconsistencia, el sistema puede corregir automáticamente los valores en registros futuros sin modificar los históricos.

**Independent Test**: Ejecutar una corrección sobre un conjunto de registros futuros y verificar que solo los futuros son actualizados.

### Implementation for User Story 3

- [x] T017 [P] [US3] Agregar método `corregir_propagacion_canon` en `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- [x] T018 [US3] Implementar lógica para identificar registros futuros con inconsistencias (canon_bruto != canon_arrendamiento o valor_total != canon_arrendamiento)
- [x] T019 [US3] Ejecutar actualización masiva de registros futuros inconsistentes en una transacción atómica
- [x] T020 [US3] Registrar en log de auditoría cada registro corregido con valores anterior/nuevo

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y validación final

- [x] T021 [P] Ejecutar script de auditoría completo para validar que no hay inconsistencias en el sistema
- [x] T022 [P] Verificar que los tests existentes no están fallidos después de los cambios
- [x] T023 Revisar que el código cumple con los estándares de Clean Architecture (dependencias unidireccionales)
- [x] T024 [P] Ejecutar validación del quickstart.md para verificar escenarios end-to-end
- [x] T025 Documentar los cambios realizados en el CHANGELOG o commits con convención `fix(servicio): propagacion canon liquidaciones recaudos`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational
  - User Story 2 (P2): Can start after Foundational, may integrate with US1
  - User Story 3 (P3): Can start after Foundational, may integrate with US1/US2
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May use US1 for validation
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May use US1/US2 for validation

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T002 and T003 (revisión de código y esquema) can run in parallel
- T007 and T008 (métodos de actualización) can run in parallel
- T012 (verificación de integridad) can run in parallel with US1 implementation
- T021, T022, T024 (validaciones) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch parallel tasks for US1:
Task: "Agregar método actualizar_canon_liquidaciones_futuras en servicio_contrato_arrendamiento.py"
Task: "Agregar método actualizar_valor_recaudos_futuros en servicio_contrato_arrendamiento.py"

# Then sequential integration:
Task: "Integrar llamadas en cascade sync"
Task: "Envolver en transacción atómica"
Task: "Agregar logging de auditoría"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently with `python scripts/diagnostico/audit_renovaciones_2026.py`
5. Deploy if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All code must be 100% in Spanish (per constitution)
- Use `%s` placeholders for PostgreSQL queries (per constitution)
- Type hints are mandatory in all new code (per constitution)
