# Tasks: Ingeniería Inversa Estado de Cuenta PDF Individual

**Input**: Design documents from `/specs/058-reverse-engineer-pdf-statement/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Tests are OPTIONAL - only include if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar entorno y preparar contexto de implementación

- [X] T001 Verificar formato `comision_porcentaje` en BD ejecutando query SQL de diagnóstico
- [X] T002 Confirmar que el método `_add_resumen_financiero()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` es el punto de modificación

**Checkpoint**: Entorno verificado, punto de modificación confirmado

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparar estructura de datos y documentación base

**⚠️ CRITICAL**: No se puede continuar sin esta fase completada

- [X] T003 Actualizar sección "Reverse Engineering Summary" en `specs/058-reverse-engineer-pdf-statement/spec.md` con flujo documentado
- [X] T004 Verificar que `data["resumen"]` contiene todos los campos requeridos para renderización

**Checkpoint**: Documentación base lista, estructura de datos verificada

---

## Phase 3: User Story 1 - Validación de Textos Descriptivos (Priority: P1) 🎯 MVP

**Goal**: Mostrar textos descriptivos entre paréntesis debajo de cada concepto financiero en el RESUMEN FINANCIERO

**Independent Test**: Generar PDF y verificar que cada concepto muestra su texto descriptivo

### Implementation for User Story 1

- [X] T005 [US1] Modificar `_add_resumen_financiero()` en `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py` para usar `Paragraph` en celdas de la columna "Concepto"
- [X] T006 [US1] Agregar texto descriptivo "(Total Canon Mandato)" debajo de "Total Ingresos"
- [X] T007 [US1] Agregar texto descriptivo "(Gravamen sobre la comisión)" debajo de "IVA 19%"
- [X] T008 [US1] Agregar texto descriptivo "(Solo aplica para propiedad horizontal)" debajo de "Administración"
- [X] T009 [US1] Agregar texto descriptivo "(Solo aplica para Energía, Agua y Gas)" debajo de "Servicios"
- [X] T010 [US1] Agregar texto descriptivo "(Pago anual del impuesto predial de la vivienda)" debajo de "Predial"
- [X] T011 [US1] Agregar texto descriptivo "(Valor del incidente; aquí se puede presentar el valor total o parcial del mismo)" debajo de "Incidentes"
- [X] T012 [US1] Verificar que "Comisión" y "NETO A PAGAR" NO muestran texto descriptivo adicional

**Checkpoint**: Textos descriptivos funcionando correctamente en todos los conceptos

---

## Phase 4: User Story 2 - Visualización Correcta del Porcentaje de Comisión (Priority: P1)

**Goal**: Mostrar el porcentaje de comisión correctamente formateado como "Comisión (X%)"

**Independent Test**: Generar PDF y verificar que el porcentaje coincide con el registrado en el contrato

### Implementation for User Story 2

- [X] T013 [US2] Verificar formato de `comision_porcentaje` en BD (base 10000 vs porcentaje directo)
- [X] T014 [US2] Ajustar cálculo de `comision_pct` en `_add_resumen_financiero()` según formato verificado
- [X] T015 [US2] Implementar redondeo al entero más cercano para porcentajes decimales
- [X] T016 [US2] Implementar valor por defecto "Comisión (0%)" cuando `comision_porcentaje` es 0 o NULL
- [X] T017 [US2] Verificar formato "Comisión (X%)" en la tabla del resumen

**Checkpoint**: Porcentaje de comisión mostrándose correctamente en todos los escenarios

---

## Phase 5: User Story 3 - Ingeniería Inversa Documentada (Priority: P2)

**Goal**: Documentar el flujo completo de generación del PDF en la especificación

**Independent Test**: Revisar documentación generada que describe el flujo completo

### Implementation for User Story 3

- [X] T018 [US3] Actualizar sección "Flujo de Generación del PDF" en `specs/058-reverse-engineer-pdf-statement/spec.md`
- [X] T019 [US3] Documentar puntos de verificación de datos en la sección "Puntos de Verificación"
- [X] T020 [US3] Validar que la documentación refleja el estado real del código post-implementación

**Checkpoint**: Documentación de ingeniería inversa completa y actualizada

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validación final y mejoras transversales

- [X] T021 Ejecutar validación completa usando `specs/058-reverse-engineer-pdf-statement/quickstart.md`
- [X] T022 Verificar que no hay regresiones en PDFs existentes
- [X] T023 Verificar caracteres especiales (tildes, ñ) en textos descriptivos
- [X] T024 Ejecutar pruebas de renderizado con diferentes escenarios (propiedad horizontal, sin horizontal, con incidentes, sin incidentes)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 y US2 pueden ejecutarse en paralelo (ambas son P1)
  - US3 puede ejecutarse después de US1/US2 o en paralelo
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Can run in parallel with US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Can run in parallel with US1/US2

### Within Each User Story

- Verificación antes de implementación
- Implementación incremental
- Validación al final de cada tarea

### Parallel Opportunities

- US1 y US2 pueden ejecutarse en paralelo (diferentes aspectos del mismo método)
- T005-T012 (US1) pueden ejecutarse secuencialmente (mismo archivo)
- T013-T017 (US2) pueden ejecutarse secuencialmente (mismo archivo)
- T018-T020 (US3) pueden ejecutarse en paralelo (diferentes documentos)

---

## Parallel Example: User Stories 1 & 2

```bash
# Launch US1 and US2 in parallel (different aspects):
Task US1: "Modificar _add_resumen_financiero() para textos descriptivos"
Task US2: "Verificar y ajustar formato de porcentaje de comisión"

# Note: Both modify the same file, so coordinate execution
# Recommended: Complete US1 first, then US2
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verificar entorno)
2. Complete Phase 2: Foundational (documentación base)
3. Complete Phase 3: User Story 1 (textos descriptivos)
4. **STOP and VALIDATE**: Generar PDF y verificar textos descriptivos
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Polish → Final validation → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (textos descriptivos)
   - Developer B: User Story 2 (porcentaje comisión)
   - Developer C: User Story 3 (documentación)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify format in BD before implementing US2
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Critical Path

```
T001 → T002 → T003 → T004 → T005-T012 (US1) → T021-T024
                ↓
                → T013-T017 (US2) → T021-T024
                ↓
                → T018-T020 (US3) → T021-T024
```

**Estimated Total Tasks**: 24
**MVP Tasks (US1)**: 12 tasks (T001-T012)
**Parallel Potential**: US1 + US2 can run in parallel after T004
