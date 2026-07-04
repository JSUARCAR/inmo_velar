---
description: "Task list for feature implementation"
---

# Tasks: Mejoras en Tabla de Liquidaciones

**Input**: Design documents from `/specs/012-mejoras-tabla-liquidaciones/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions
- **Presentación Reflex**: `src/presentacion_reflex/`
- **Infraestructura**: `src/infraestructura/`
- **Aplicación**: `src/aplicacion/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Checkout a la nueva rama de feature `feature/012-mejoras-tabla-liquidaciones` (o nombre equivalente) en la raíz del repositorio.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Checkpoint**: Foundation ready - no foundational blockers for this UI/UX extension.

---

## Phase 3: User Story 1 - Ordenamiento de Columnas (Priority: P1) 🎯 MVP

**Goal**: Permitir al usuario ordenar la tabla de Liquidaciones por cualquiera de sus columnas (excepto Acciones) tanto de forma ascendente como descendente.

**Independent Test**: Hacer clic en el encabezado de las columnas en la UI; la data se recarga ordenada ASC/DESC y los íconos de flecha se actualizan.

### Implementation for User Story 1

- [x] T002 [US1] Modificar el método de consulta en `src/infraestructura/repositorios/repositorio_liquidacion.py` para aceptar y aplicar `order_by` (str) y `order_desc` (bool).
- [x] T003 [US1] Actualizar el DTO / Servicio asociado en `src/aplicacion/` (si existe intermediación) para propagar los nuevos parámetros de ordenamiento.
- [x] T004 [P] [US1] Ampliar el Estado en `src/presentacion_reflex/` (estado de liquidaciones) incorporando variables `columna_orden` y `orden_descendente`, y una función `alternar_orden(columna)`.
- [x] T005 [US1] Actualizar la vista de la tabla en `src/presentacion_reflex/` para vincular cada cabecera (excepto 'Acciones') al evento `alternar_orden`, y renderizar el ícono correspondiente (flecha arriba/abajo).

**Checkpoint**: User Story 1 (Ordenamiento) functional and testable independently.

---

## Phase 4: User Story 2 - Filtro por Ciclo Operativo (Priority: P1)

**Goal**: Permitir filtrar los registros de la tabla de Liquidaciones por "Ciclo Operativo".

**Independent Test**: Aplicar un ciclo en la UI y validar que la tabla devuelve resultados limitados a ese período (y respeta el ordenamiento actual si lo hay).

### Implementation for User Story 2

- [x] T006 [US2] Modificar el método de consulta en `src/infraestructura/repositorios/repositorio_liquidacion.py` (y en `src/aplicacion/`) para aceptar y procesar el parámetro opcional `ciclo_operativo`.
- [x] T007 [P] [US2] Agregar la variable reactiva `filtro_ciclo_operativo` en el Estado de Liquidaciones (`src/presentacion_reflex/`) y acoplarla a la función de búsqueda.
- [x] T008 [US2] Insertar el componente UI (`rx.select` o input) para el "Ciclo Operativo" dentro del contenedor de filtros avanzados en `src/presentacion_reflex/`.

**Checkpoint**: User Story 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Corrección Visual y Reorganización UI/UX de Filtros (Priority: P2)

**Goal**: Corregir problemas de superposición, márgenes y distribución lógica en la sección de filtros avanzados.

**Independent Test**: Achicar y agrandar la ventana (responsive) y observar que los controles no se traslapan; verificar márgenes uniformes.

### Implementation for User Story 3

- [x] T009 [US3] Refactorizar la disposición de componentes en el panel de Filtros Avanzados (ubicado en `src/presentacion_reflex/`) usando `wrap="wrap"` y espaciados del `BASE_STYLE`.
- [x] T010 [US3] Validar que los botones de "Aplicar" y "Limpiar" no se solapen con otros inputs tras la adición del filtro del Ciclo Operativo.

**Checkpoint**: All user stories should now be independently functional.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T011 [P] Revisar que no existan dependencias no utilizadas en los imports de las vistas y repositorios modificados.
- [x] T012 Run quickstart.md validation tests to verify all functionality works end-to-end.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Completa.
- **User Stories (Phase 3+)**: US1, US2 y US3 pueden ser ejecutadas secuencial o paralelamente (cuidado con merge conflicts si editan el mismo archivo de Estado y Repositorio en paralelo).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### Parallel Opportunities

- T004 y T007 (Modificaciones de Estado Reflex puro) pueden avanzar en paralelo una vez iniciada su respectiva historia.
- Las vistas pueden rediseñarse independientemente de si el backend está 100% conectado (mocking en Reflex).

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Completar Setup.
2. Completar US1 (Ordenamiento).
3. Completar US2 (Filtro).
4. **STOP and VALIDATE**.
5. Completar US3 (Refactor UI).
