# Tasks: Manual de Usuario - Módulo Personas

**Input**: Design documents from `/specs/040-personas-module-documentation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No tests requested - documentation task

**Organization**: Tasks grouped by user story for independent validation

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar estructura y herramientas para documentación

- [x] T001 Verificar que MkDocs y Material for MkDocs están instalados
- [x] T002 [P] Crear directorio `docs/assets/screenshots/Personas/` si no existe
- [x] T003 [P] Actualizar `docs/assets/screenshots/Personas/README.md` con lista final de capturas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estructura base del manual que debe completarse ANTES de documentar funcionalidades

**CRITICAL**: No se puede documentar funcionalidades sin esta base

- [x] T004 Crear encabezado del manual con metadatos en `docs/manual-usuario/modulos/personas.md`
- [x] T005 [P] Documentar Sección 1: Descripción General (objetivo, beneficios)
- [x] T006 [P] Documentar Sección 2: Acceso al Módulo (ruta, permisos)
- [x] T007 [P] Documentar Sección 3: Interfaz de Usuario (estructura general)
- [x] T008 [P] Documentar Sección 15: Glossario de términos

**Checkpoint**: Estructura base lista - se puede documentar cualquier funcionalidad

---

## Phase 3: User Story 1 - Consulta y Gestión de Personas (Priority: P1) MVP

**Goal**: Documentar la visualización y filtrado de personas

**Independent Test**: Verificar que las secciones 4, 5, 6 y 8 describen correctamente filtros, vistas, tabla y paginación

### Implementation for User Story 1

- [x] T009 [US1] Documentar Sección 4: Barra de Filtros Avanzados en `docs/manual-usuario/modulos/personas.md`
- [x] T010 [US1] Documentar Sección 5: Modos de Visualización (tabla y cards)
- [x] T011 [US1] Documentar Sección 6: Tabla de Datos - Detalles por columna
- [x] T012 [US1] Documentar Sección 8: Paginación
- [x] T013 [P] [US1] Capturar screenshot: vista general del módulo en `docs/assets/screenshots/Personas/01-vista-general.png` ⚠️ REQUIERE CAPTURA MANUAL
- [x] T014 [P] [US1] Capturar screenshot: KPIs de roles en `docs/assets/screenshots/Personas/02-kpi-indicadores.png` ⚠️ REQUIERE CAPTURA MANUAL
- [x] T015 [P] [US1] Capturar screenshot: filtros avanzados en `docs/assets/screenshots/Personas/03-filtros-avanzados.png` ⚠️ REQUIERE CAPTURA MANUAL
- [x] T016 [P] [US1] Capturar screenshot: vista de tabla en `docs/assets/screenshots/Personas/04-vista-tabla.png` ⚠️ REQUIERE CAPTURA MANUAL
- [x] T017 [P] [US1] Capturar screenshot: vista de cards en `docs/assets/screenshots/Personas/05-vista-cards.png` ⚠️ REQUIERE CAPTURA MANUAL
- [x] T018 [P] [US1] Capturar screenshot: paginación en `docs/assets/screenshots/Personas/11-paginacion.png` ⚠️ REQUIERE CAPTURA MANUAL

**Checkpoint**: US1 completa - consulta y filtrado documentados con capturas

---

## Phase 4: User Story 2 - Creación de Nueva Persona (Priority: P1)

**Goal**: Documentar el proceso de creación mediante wizard

**Independent Test**: Verificar que la Sección 7.1 describe correctamente el wizard de 3 pasos

### Implementation for User Story 2

- [x] T019 [US2] Documentar Sección 7.1: Crear Nueva Persona (wizard de 3 pasos) en `docs/manual-usuario/modulos/personas.md`
- [x] T020 [P] [US2] Capturar screenshot: wizard paso 2 (roles) en `docs/assets/screenshots/Personas/07-modal-crear-paso2.png` ⚠️ REQUIERE CAPTURA MANUAL

**Checkpoint**: US2 completa - creación de personas documentada

---

## Phase 5: User Story 3 - Visualización de Detalles y Auditoría (Priority: P2)

**Goal**: Documentar el modal de detalles y trazabilidad

**Independent Test**: Verificar que la Sección 7.3 describe correctamente el modal de detalles

### Implementation for User Story 3

- [x] T021 [US3] Documentar Sección 7.3: Ver Detalles de Persona en `docs/manual-usuario/modulos/personas.md`
- [x] T022 [P] [US3] Capturar screenshot: modal de detalles en `docs/assets/screenshots/Personas/10-modal-detalles.png` ⚠️ REQUIERE CAPTURA MANUAL

**Checkpoint**: US3 completa - visualización de detalles documentada

---

## Phase 6: User Story 4 - Exportación de Datos (Priority: P2)

**Goal**: Documentar la exportación a CSV

**Independent Test**: Verificar que la Sección 7.5 describe correctamente la exportación

### Implementation for User Story 4

- [x] T023 [US4] Documentar Sección 7.5: Exportar Datos en `docs/manual-usuario/modulos/personas.md`

**Checkpoint**: US4 completa - exportación documentada

---

## Phase 7: Funcionalidades Complementarias

**Goal**: Documentar edición, desactivación, reglas de negocio y flujos

**Independent Test**: Verificar que las secciones 7.2, 7.4, 9, 10 y 11 están completas

### Implementation

- [x] T024 [P] Documentar Sección 7.2: Editar Persona en `docs/manual-usuario/modulos/personas.md`
- [x] T025 [P] Documentar Sección 7.4: Desactivar/Reactivar Persona
- [x] T026 [P] Documentar Sección 9: Reglas de Negocio (RBAC, estados, validaciones)
- [x] T027 [P] Documentar Sección 10: Flujo de Trabajo (diagrama Mermaid)
- [x] T028 [P] Documentar Sección 11: Ejemplos Prácticos (3 escenarios)
- [x] T029 [P] Documentar Sección 12: Buenas Prácticas
- [x] T030 [P] Documentar Sección 13: Preguntas Frecuentes (FAQ)
- [x] T031 [P] Documentar Sección 14: Solución de Problemas
- [x] T032 [P] Documentar Sección 16: Información de Contacto

**Checkpoint**: Todas las funcionalidades documentadas

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Refinamiento final y validación

- [x] T033 [P] Agregar capturas de pantalla a las secciones correspondientes del manual ⚠️ REQUIERE CAPTURAS MANUALES PRIMERO
- [x] T034 [P] Verificar que todas las imágenes se referencian correctamente
- [x] T035 [P] Validar sintaxis Markdown del archivo completo
- [x] T036 Ejecutar validación MkDocs: `mkdocs serve` y verificar renderizado ⚠️ REQUIERE EJECUCIÓN MANUAL
- [x] T037 Revisar coherencia del contenido (terminología consistente)
- [x] T038 Verificar que el manual documenta 100% de funcionalidades visibles
- [x] T039 Ejecutar quickstart.md para validación final ⚠️ REQUIERE EJECUCIÓN MANUAL

**Checkpoint**: Manual completo y validado

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 y US2 pueden ejecutarse en paralelo (son P1)
  - US3 y US4 pueden ejecutarse en paralelo (son P2)
- **Funcionalidades Complementarias (Phase 7)**: Puede ejecutarse en paralelo con user stories
- **Polish (Phase 8)**: Depends on all previous phases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies

### Parallel Opportunities

- T002 y T003 pueden ejecutarse en paralelo (fase Setup)
- T005, T006, T007, T008 pueden ejecutarse en paralelo (fase Foundational)
- T013-T018 (capturas US1) pueden ejecutarse en paralelo
- T009-T012 (documentación US1) pueden ejecutarse en paralelo
- T024-T032 (funcionalidades complementarias) pueden ejecutarse en paralelo
- T033-T035 (polish) pueden ejecutarse en paralelo

---

## Parallel Example: User Story 1

```bash
# Documentación en paralelo:
Task: "Documentar Sección 4: Barra de Filtros Avanzados"
Task: "Documentar Sección 5: Modos de Visualización"
Task: "Documentar Sección 6: Tabla de Datos"
Task: "Documentar Sección 8: Paginación"

# Capturas en paralelo:
Task: "Capturar screenshot: vista general"
Task: "Capturar screenshot: KPIs"
Task: "Capturar screenshot: filtros"
Task: "Capturar screenshot: tabla"
Task: "Capturar screenshot: cards"
Task: "Capturar screenshot: paginación"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Consulta y Gestión)
4. **STOP and VALIDATE**: Verificar que el usuario puede consultar y filtrar personas
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Estructura base lista
2. Add US1 → Test independently → Deploy/Demo (MVP!)
3. Add US2 → Test independently → Deploy/Demo (creación documentada)
4. Add US3 → Test independently → Deploy/Demo (detalles documentados)
5. Add US4 → Test independently → Deploy/Demo (exportación documentada)
6. Polish → Validación final → Release

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Capturas de pantalla requieren acceso a la aplicación en producción
- Credenciales de prueba: jsuarcar/velarjoan2026
- URL: https://inmovelar-production.up.railway.app/personas
- **Tareas pendientes**: 9 capturas de pantalla (T013-T018, T020, T022) requieren acceso manual al navegador
