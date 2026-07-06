---
description: "Task list for tooltips on advanced filters feature"
---

# Tasks: Estandarización de Tooltips en Filtros Avanzados

**Input**: Design documents from `/specs/022-tooltips-filtros-avanzados/`

**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verificación y/o configuración de constantes globales (`Z_TOOLTIP` y estilos base) en `src/presentacion_reflex/styles.py` para asegurar consistencia de z-index y pointer-events.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*(No hay dependencias bloqueantes de infraestructura para esta característica, ya que es puramente de UI).*

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Estandarización de Tooltips en Filtros (Priority: P1) 🎯 MVP

**Goal**: Mostrar tooltips descriptivos en todos los botones de la sección Filtros Avanzados, usando verbos en infinitivo, deshabilitados en móviles y con posición "top".

**Independent Test**: Navegar a cada módulo, pasar el cursor (hover) por los botones de Filtros Avanzados, y validar que el tooltip aparece arriba, con texto en infinitivo. Inspeccionar desde móvil para asegurar que no se dispara en el primer touch y respeta estilos CSS (`display=["none", "none", "block"]` u otra implementación que lo esconda en pantallas pequeñas).

### Implementation for User Story 1

- [x] T002 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Dashboard** (`src/presentacion_reflex/pages/dashboard.py`).
- [x] T003 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Personas** (`src/presentacion_reflex/pages/gestion_personas.py`).
- [x] T004 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Propiedades** (`src/presentacion_reflex/pages/gestion_propiedades.py`).
- [x] T005 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Contratos** (`src/presentacion_reflex/pages/gestion_contratos.py`).
- [x] T006 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Liquidaciones** (`src/presentacion_reflex/pages/gestion_liquidaciones.py`).
- [x] T007 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Liquidación de Asesores** (`src/presentacion_reflex/pages/liquidacion_asesores.py`).
- [x] T008 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Recaudos** (`src/presentacion_reflex/pages/gestion_recaudos.py`).
- [x] T009 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Desocupaciones** (`src/presentacion_reflex/pages/gestion_desocupaciones.py`).
- [x] T010 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Incidentes** (`src/presentacion_reflex/pages/gestion_incidentes.py`).
- [x] T011 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Seguros** (`src/presentacion_reflex/pages/gestion_seguros.py`).
- [x] T012 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Recibos Públicos** (`src/presentacion_reflex/pages/recibos_publicos.py`).
- [x] T013 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Saldos a Favor** (`src/presentacion_reflex/pages/saldos_a_favor.py`).
- [x] T014 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Usuarios** (`src/presentacion_reflex/pages/usuarios.py`).
- [x] T015 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Gestión de IPC** (`src/presentacion_reflex/pages/gestion_ipc.py`).
- [x] T016 [P] [US1] Refactorizar la sección de Filtros Avanzados e inyectar `rx.tooltip` en el módulo **Reportes** (`src/presentacion_reflex/pages/reportes.py`).

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T017 Run `quickstart.md` validation y asegurar compatibilidad general (verificando logs de Reflex o errores de consola).
- [x] T018 Confirmar responsividad y accesibilidad final con lectores de pantalla/teclado.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion. En este caso los módulos se pueden refactorizar en paralelo total.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories. 

### Parallel Opportunities

- Todos los componentes y módulos desde T002 hasta T016 marcados como `[P]` se pueden refactorizar en paralelo de ser necesario.

## Parallel Example: User Story 1

```bash
# Launch implementations of independent pages together
Task: "[US1] Refactorizar la sección de Filtros Avanzados e inyectar rx.tooltip en el módulo Dashboard (src/presentacion_reflex/pages/dashboard.py)"
Task: "[US1] Refactorizar la sección de Filtros Avanzados e inyectar rx.tooltip en el módulo Personas (src/presentacion_reflex/pages/gestion_personas.py)"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Validar `Z_TOOLTIP` en `styles.py`).
2. Complete Phase 3: User Story 1 (Refactorización de todos los módulos iterativamente o en paralelo).
3. **STOP and VALIDATE**: Test User Story 1 independently siguiendo `quickstart.md`.
4. Deploy/demo if ready.
