---
description: "Task list for Auditoría de Tooltips Faltantes implementation"
---

# Tasks: Auditoría de Tooltips Faltantes

**Input**: Design documents from `/specs/023-auditoria-tooltips-faltantes/`

**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Tests are OPTIONAL. Visual validation in browser will serve as acceptance.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparación de herramientas de escaneo

- [x] T001 Crear el script de auditoría automatizado en `specs/023-auditoria-tooltips-faltantes/scripts/scanner.py` para identificar botones sin tooltips en `src/presentacion_reflex/pages`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

*(N/A - La arquitectura base ya existe por el Feature 022)*

---

## Phase 3: User Story 1 - Identificación y Corrección de Tooltips Faltantes (Priority: P1) 🎯 MVP

**Goal**: Inyectar tooltips faltantes en todos los botones huérfanos (iconos o acciones) de la aplicación, manteniendo consistencia.

**Independent Test**: Ejecutar servidor localmente e inspeccionar que los botones detectados ahora muestran el tooltip correctamente.

### Implementation for User Story 1

- [x] T002 [US1] Ejecutar `scanner.py` y listar archivos afectados
- [x] T003 [P] [US1] Inyectar `neuro_tooltip` en los botones identificados dentro de los archivos encontrados en `src/presentacion_reflex/pages/*.py`
- [x] T004 [US1] Verificar el uso de verbos en infinitivo (ej. "Editar", "Guardar") para todos los nuevos tooltips insertados.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T005 Run quickstart.md validation visualmente con `reflex run --env dev`
- [x] T006 Limpiar el script temporal `scanner.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: (Vacío)
- **User Stories (Phase 3+)**: Dependen de Setup.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Única historia en el alcance actual.

### Within Each User Story

- El escaneo (T002) debe ejecutarse antes de la corrección (T003).

### Parallel Opportunities

- Diferentes archivos pueden ser modificados en paralelo durante la tarea T003.

---

## Parallel Example: User Story 1

```bash
# Modificar varios módulos en paralelo usando sed, python o agentes:
Task: "Inyectar neuro_tooltip en recaudos.py"
Task: "Inyectar neuro_tooltip en liquidaciones.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently visualmente.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Cada archivo afectado debe ser inspeccionado para respetar el `pointer-events: auto` implícito.
