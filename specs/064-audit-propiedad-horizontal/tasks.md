# Tasks: Ingeniería Inversa del Módulo de Propiedad Horizontal

**Input**: Design documents from `specs/064-audit-propiedad-horizontal/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Esta feature es de naturaleza analítica (auditoría). No se requieren pruebas de código (TDD), sino revisiones de completitud del informe según el `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Crear el archivo base AUDIT_REPORT.md en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md
- [x] T002 [P] Identificar el árbol de directorios del módulo de Propiedad Horizontal usando comandos de búsqueda en el repositorio

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Revisar reglas actuales en GEMINI.md y CLAUDE.md para establecer la línea base (baseline) arquitectónica a auditar

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Diagnóstico y Mapeo Funcional (Priority: P1) 🎯 MVP

**Goal**: Generar un mapa funcional del módulo y un inventario de funcionalidades clasificadas.

**Independent Test**: Revisar que el informe contiene los flujos funcionales documentados al 100%.

### Implementation for User Story 1

- [x] T004 [P] [US1] Analizar UI y estados de Reflex en src/presentacion_reflex/ para identificar flujos e interacciones de usuario
- [x] T005 [P] [US1] Analizar casos de uso y lógica de negocio en src/aplicacion/ y src/dominio/
- [x] T006 [US1] Redactar sección "Análisis Funcional Integral" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md
- [x] T007 [US1] Redactar sección "Inventario de Funcionalidades" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Análisis Técnico, Arquitectónico y de BD (Priority: P1)

**Goal**: Revisión integral de arquitectura y modelo de datos relacional.

**Independent Test**: Modelos de arquitectura documentados y legibles.

### Implementation for User Story 2

- [x] T008 [P] [US2] Mapear dependencias internas y externas de la arquitectura actual revisando imports
- [x] T009 [P] [US2] Extraer esquema y relaciones de las tablas de Propiedad Horizontal desde src/infraestructura/
- [x] T010 [US2] Redactar sección "Análisis Técnico y Arquitectónico" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md
- [x] T011 [US2] Redactar sección "Ingeniería Inversa de Base de Datos" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Auditoría de Deuda Técnica y Riesgos (Priority: P2)

**Goal**: Inventario exhaustivo de deuda técnica y matriz de riesgos.

**Independent Test**: Matriz de riesgos consolidada en el reporte.

### Implementation for User Story 3

- [x] T012 [P] [US3] Auditar calidad de código, legibilidad y rendimiento en los módulos identificados previamente
- [x] T013 [P] [US3] Clasificar riesgos operativos, de seguridad y funcionales detectados
- [x] T014 [US3] Redactar sección "Deuda Técnica" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md
- [x] T015 [US3] Redactar sección "Diagnóstico de Riesgos" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Plan de Evolución y Recomendaciones (Priority: P2)

**Goal**: Generar una propuesta de mejora estructurada.

**Independent Test**: Hoja de ruta accionable y priorizada listada en el informe.

### Implementation for User Story 4

- [x] T016 [P] [US4] Formular recomendaciones a corto plazo (fixes) con base en la deuda detectada
- [x] T017 [P] [US4] Formular recomendaciones a mediano y largo plazo (refactor y evolución)
- [x] T018 [US4] Redactar sección "Plan de Evolución" y "Resumen Ejecutivo" en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T019 Revisar coherencia general, consistencia de términos y formato Markdown en specs/064-audit-propiedad-horizontal/AUDIT_REPORT.md
- [x] T020 Validar el informe resultante contra specs/064-audit-propiedad-horizontal/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independently testable, aunque el análisis de DB puede complementar el análisis funcional.
- **User Story 3 (P2)**: Depende indirectamente del entendimiento generado en US1 y US2, ya que no se puede auditar la deuda sin comprender el módulo.
- **User Story 4 (P2)**: Depende de los hallazgos en US3 para formular planes de remediación.

### Within Each User Story

- El análisis de código (Tasks pares) precede a la redacción (Tasks impares/finales).
- La revisión documental final debe ocurrir al completar la fase de recolección de información.

### Parallel Opportunities

- Todas las tareas marcadas con [P] se pueden ejecutar en paralelo de forma segura.
- Una vez finalizada la Foundation, los desarrolladores (o agentes) pueden repartirse el análisis de distintos subsistemas (UI, DB, Lógica).

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently (Leer el mapeo funcional inicial)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Validar flujo funcional del módulo (MVP)
3. Add User Story 2 → Integrar diseño arquitectónico al documento
4. Add User Story 3 → Añadir matriz de riesgos al conocimiento del proyecto
5. Add User Story 4 → Concluir con recomendaciones prácticas

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
