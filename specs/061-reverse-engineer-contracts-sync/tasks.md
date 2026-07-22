# Tasks: Ingeniería Inversa - Sincronización Contratos, Liquidaciones y Recaudos

**Input**: Design documents from `/specs/061-reverse-engineer-contracts-sync/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuración inicial del proyecto de validación

- [X] T001 Crear directorio de verificación en tests/verification/
- [X] T002 [P] Configurar pytest.ini para tests de integración
- [X] T003 [P] Crear archivo conftest.py base para tests de validación en tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura core que DEBE completarse ANTES de cualquier user story

**⚠️ CRITICAL**: No se puede iniciar trabajo en user stories hasta completar esta fase

- [X] T004 Crear script base de auditoría en tests/verification/audit_sincronizacion.py
- [X] T005 [P] Implementar función de conexión a BD de staging en tests/verification/audit_sincronizacion.py
- [X] T006 [P] Implementar generador de informes estructurados en tests/verification/audit_sincronizacion.py
- [X] T007 Crear fixture de datos de prueba en tests/integration/conftest.py

**Checkpoint**: Infraestructura lista - se puede iniciar implementación de user stories en paralelo

---

## Phase 3: User Story 1 - Validación de Cascada de Renovación (Priority: P1) 🎯 MVP

**Goal**: Verificar que la renovación propaga correctamente el canon a mandato y propiedad

**Independent Test**: Ejecutar renovación y verificar que mandato y propiedad se actualizaron

### Implementation for User Story 1

- [X] T008 [P] [US1] Implementar VR-001 (Cascada Canon) en tests/verification/audit_sincronizacion.py
- [X] T009 [P] [US1] Implementar VR-002 (Historial Renovación) en tests/verification/audit_sincronizacion.py
- [X] T010 [P] [US1] Implementar VR-003 (Fechas) en tests/verification/audit_sincronizacion.py
- [X] T011 [US1] Crear test de integración para cascada en tests/integration/test_sincronizacion_contratos.py
- [X] T012 [US1] Agregar validación de cascada al informe de auditoría

**Checkpoint**: User Story 1 funcional y testeable independientemente

---

## Phase 4: User Story 2 - Preservación de Registros Históricos (Priority: P1)

**Goal**: Verificar que liquidaciones y recaudos antiguos no se modifican después de renovación

**Independent Test**: Verificar que registros históricos mantienen valores originales

### Implementation for User Story 2

- [X] T013 [P] [US2] Implementar VR-004 (Preservación Liquidaciones) en tests/verification/audit_sincronizacion.py
- [X] T014 [P] [US2] Implementar VR-005 (Preservación Recaudos) en tests/verification/audit_sincronizacion.py
- [X] T015 [US2] Crear test de integración para preservación en tests/integration/test_sincronizacion_contratos.py
- [X] T016 [US2] Agregar validación de preservación al informe de auditoría

**Checkpoint**: User Stories 1 Y 2 funcionales independientemente

---

## Phase 5: User Story 3 - Generación con Canon Actualizado (Priority: P2)

**Goal**: Verificar que liquidaciones y recaudos futuros usan el nuevo canon después de renovación

**Independent Test**: Generar liquidaciones/recaudos después de renovación y verificar valores

### Implementation for User Story 3

- [X] T017 [P] [US3] Implementar VR-006 (Generación Liquidaciones) en tests/verification/audit_sincronizacion.py
- [X] T018 [P] [US3] Implementar VR-007 (Generación Recaudos) en tests/verification/audit_sincronizacion.py
- [X] T019 [US3] Crear test de integración para generación en tests/integration/test_sincronizacion_contratos.py
- [X] T020 [US3] Agregar validación de generación al informe de auditoría

**Checkpoint**: User Stories 1, 2 Y 3 funcionales

---

## Phase 6: User Story 4 - Consistencia entre Módulos (Priority: P2)

**Goal**: Verificar que no hay discrepancias de datos entre Contratos, Liquidaciones y Recaudos

**Independent Test**: Ejecutar consultas cruzadas y verificar que valores coinciden

### Implementation for User Story 4

- [X] T021 [P] [US4] Implementar VR-008 (Consistencia Módulos) en tests/verification/audit_sincronizacion.py
- [X] T022 [US4] Crear test de integración para consistencia en tests/integration/test_sincronizacion_contratos.py
- [X] T023 [US4] Agregar validación de consistencia al informe de auditoría

**Checkpoint**: User Stories 1, 2, 3 Y 4 funcionales

---

## Phase 7: User Story 5 - Ausencia de Actualizaciones Retroactivas (Priority: P2)

**Goal**: Verificar que no existen procesos que modifiquen registros históricos

**Independent Test**: Analizar código fuente en busca de procesos de actualización retroactiva

### Implementation for User Story 5

- [X] T024 [P] [US5] Implementar VR-009 (Ausencia Retroactivos) en tests/verification/audit_sincronizacion.py
- [X] T025 [US5] Crear análisis estático de código para detectar actualizaciones en tests/verification/audit_sincronizacion.py
- [X] T026 [US5] Agregar validación de retroactivos al informe de auditoría

**Checkpoint**: User Stories 1, 2, 3, 4 Y 5 funcionales

---

## Phase 8: User Story 6 - Respeto de Fecha de Vigencia (Priority: P3)

**Goal**: Verificar que la fecha de vigencia de la renovación es respetada por todos los procesos

**Independent Test**: Generar liquidaciones antes y después de fecha de vigencia y verificar valores

### Implementation for User Story 6

- [X] T027 [P] [US6] Implementar VR-010 (Reseto Fecha Vigencia) en tests/verification/audit_sincronizacion.py
- [X] T028 [US6] Crear test de integración para fecha de vigencia en tests/integration/test_sincronizacion_contratos.py
- [X] T029 [US6] Agregar validación de fecha de vigencia al informe de auditoría

**Checkpoint**: Todos los user stories funcionales

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras que afectan múltiples user stories

- [X] T030 [P] Ejecutar suite completa de tests de validación
- [X] T031 [P] Verificar que informe de auditoría genera salida correcta
- [X] T032 Integrar script de auditoría en pipeline de CI/CD
- [X] T033 Ejecutar quickstart.md validation para verificar escenarios
- [X] T034 [P] Actualizar documentación con resultados de auditoría

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias - puede iniciar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup - BLOQUEA todos los user stories
- **User Stories (Phase 3-8)**: Todas dependen de Foundational
  - User stories pueden proceder en paralelo (si hay capacidad)
  - O secuencialmente en orden de prioridad (P1 → P2 → P3)
- **Polish (Phase 9)**: Depende de que todos los user stories deseados estén completos

### User Story Dependencies

- **User Story 1 (P1)**: Puede iniciar después de Foundational - Sin dependencias en otras stories
- **User Story 2 (P1)**: Puede iniciar después de Foundational - Independiente de US1
- **User Story 3 (P2)**: Puede iniciar después de Foundational - Puede integrar con US1/US2
- **User Story 4 (P2)**: Puede iniciar después de Foundational - Puede integrar con US1/US2/US3
- **User Story 5 (P2)**: Puede iniciar después de Foundational - Independiente (análisis de código)
- **User Story 6 (P3)**: Puede iniciar después de Foundational - Puede integrar con US1/US2/US3

### Within Each User Story

- Implementación de reglas de validación primero
- Tests de integración después
- Agregar al informe de auditoría al final

### Parallel Opportunities

- Todas las tareas marcadas [P] en Setup pueden ejecutarse en paralelo
- Todas las tareas marcadas [P] en Foundational pueden ejecutarse en paralelo
- Una vez completado Foundational, todos los user stories pueden iniciar en paralelo
- Reglas de validación dentro de cada story marcadas [P] pueden ejecutarse en paralelo
- Diferentes user stories pueden trabajarse en paralelo por diferentes miembros del equipo

---

## Parallel Example: User Story 1

```bash
# Ejecutar todas las reglas de validación para US1 juntas:
Task: "Implementar VR-001 (Cascada Canon) en tests/verification/audit_sincronizacion.py"
Task: "Implementar VR-002 (Historial Renovación) en tests/verification/audit_sincronizacion.py"
Task: "Implementar VR-003 (Fechas) en tests/verification/audit_sincronizacion.py"

# Ejecutar test de integración:
Task: "Crear test de integración para cascada en tests/integration/test_sincronizacion_contratos.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRÍTICO - bloquea todas las stories)
3. Completar Phase 3: User Story 1
4. **DETENERSE Y VALIDAR**: Testear User Story 1 independientemente
5. Desplegar/demostrar si está listo

### Incremental Delivery

1. Completar Setup + Foundational → Infraestructura lista
2. Agregar User Story 1 → Testear independientemente → Desplegar/Demo (¡MVP!)
3. Agregar User Story 2 → Testear independientemente → Desplegar/Demo
4. Agregar User Story 3 → Testear independientemente → Desplegar/Demo
5. Cada story agrega valor sin romper stories anteriores

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Una vez Foundational completado:
   - Desarrollador A: User Story 1
   - Desarrollador B: User Story 2
   - Desarrollador C: User Story 3
3. Stories se completan e integran independientemente

---

## Notes

- Tareas [P] = archivos diferentes, sin dependencias
- Etiqueta [Story] mapea tarea a user story específica para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Verificar que tests fallen antes de implementar
- Commit después de cada tarea o grupo lógico
- Detenerse en cualquier checkpoint para validar story independientemente
- Evitar: tareas vagas, conflictos en mismo archivo, dependencias cross-story que rompan independencia
