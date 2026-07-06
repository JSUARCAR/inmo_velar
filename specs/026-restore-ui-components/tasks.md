# Tasks: Auditoría y Restauración de Componentes UI

**Input**: Design documents from `/specs/026-restore-ui-components/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story (batches) to enable independent implementation and testing of each batch.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*(No setup tasks needed. Infrastructure for components already implemented globally in 025)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*(No foundational tasks needed. Global CSS and Base Style already in place)*

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Core Modules (Priority: P1) 🎯 MVP

**Goal**: Restaurar Floating Labels y Tooltips en los módulos centrales (Personas, Propiedades, Contratos, Liquidaciones).

**Independent Test**: Navegar a las secciones mencionadas y verificar visualmente los tooltips y los inputs reactivos.

### Implementation for User Story 1

- [X] T001 [P] [US1] Refactorizar `rx.input`, `rx.select` y `rx.button` en `src/presentacion_reflex/components/personas/` (e.g. `formulario_personas.py`) para usar `neuro_floating_input`, `neuro_floating_select` y proveer `tooltip_content`.
- [X] T002 [P] [US1] Refactorizar inputs y botones en `src/presentacion_reflex/components/propiedades/` (e.g. `formulario_propiedades.py`) siguiendo el estándar.
- [X] T003 [P] [US1] Refactorizar inputs y botones en `src/presentacion_reflex/components/contratos/` siguiendo el estándar y placeholders estáticos en DatePickers si hay.
- [X] T004 [P] [US1] Refactorizar inputs y botones en `src/presentacion_reflex/components/liquidaciones/` siguiendo el estándar.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Operations Modules (Priority: P2)

**Goal**: Restaurar Floating Labels y Tooltips en módulos operativos (Asesores, Recaudos, Desocupaciones, Incidentes).

**Independent Test**: Navegar a estas secciones y verificar visualmente.

### Implementation for User Story 2

- [X] T005 [P] [US2] Refactorizar inputs y botones en `src/presentacion_reflex/components/liquidacion_asesores/` siguiendo el estándar.
- [X] T006 [P] [US2] Refactorizar inputs y botones en `src/presentacion_reflex/components/recaudos/` siguiendo el estándar.
- [X] T007 [P] [US2] Refactorizar inputs y botones en `src/presentacion_reflex/components/desocupaciones/` siguiendo el estándar.
- [X] T008 [P] [US2] Refactorizar inputs y botones en `src/presentacion_reflex/components/incidentes/` siguiendo el estándar.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Support Modules (Priority: P3)

**Goal**: Restaurar Floating Labels y Tooltips en módulos de soporte (Seguros, Recibos, Usuarios, Proveedores).

**Independent Test**: Navegar a estas secciones y verificar visualmente.

### Implementation for User Story 3

- [X] T009 [P] [US3] Refactorizar inputs y botones en `src/presentacion_reflex/components/seguros/` siguiendo el estándar.
- [X] T010 [P] [US3] Refactorizar inputs y botones en `src/presentacion_reflex/components/recibos/` siguiendo el estándar.
- [X] T011 [P] [US3] Refactorizar inputs y botones en `src/presentacion_reflex/components/usuarios/` siguiendo el estándar.
- [X] T012 [P] [US3] Refactorizar inputs y botones en `src/presentacion_reflex/components/proveedores/` siguiendo el estándar.

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T013 Exportar el proyecto completo localmente (`reflex export --frontend-only --no-zip`) para asegurar que no hay errores de compilación introducidos por la refactorización.

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Stories (Phase 3+)**: Can start immediately in parallel.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- Todas las US (1, 2, 3) son completamente independientes y pueden realizarse en paralelo.

### Parallel Opportunities

- Todos los tasks de refactorización (`T001` - `T012`) operan en directorios separados y son completamente paralelizables.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar T001-T004 (Módulos Core).
2. **STOP and VALIDATE**: Testear UI independientemente.
3. Avanzar a siguientes User Stories incrementalmente.

---

## Phase 6: Convergence - Módulos Faltantes (Post-Auditoría)

**Purpose**: Modular en spec.md que NO fueron cubiertos por T001-T012. Auditoría de convergencia reveló estos gaps.

**Source**: Convergencia spec.md vs. tasks.md - 2026-07-05

### Implementation for Convergence

- [X] T014 [P] [US4] Refactorizar `src/presentacion_reflex/pages/saldos_favor.py` - Módulo Saldos a Favor (spec #11). Reemplazar 3× `rx.input` → `neuro_floating_input`, 3× `rx.select` → `neuro_floating_select`, 1× `rx.text_area` → `neuro_text_area`, 7× `rx.button` → `neuro_button`/`neuro_icon_action_button` con `tooltip_content`.
- [X] T015 [P] [US4] Refactorizar `src/presentacion_reflex/pages/reportes.py` - Módulo Reportes (spec #14). Reemplazar 7× `rx.input` → `neuro_floating_input`, 7× `rx.select` → `neuro_floating_select`, 4× `rx.button` → `neuro_button`/`neuro_icon_action_button` con `tooltip_content`.
- [X] T016 [P] [US4] Refactorizar `src/presentacion_reflex/components/asambleas/calendario_mensual.py` - Reemplazar 2× `rx.icon_button` → `neuro_icon_action_button` con `tooltip_content` ("Mes anterior", "Mes siguiente").
- [X] T017 [P] [US4] Refactorizar `src/presentacion_reflex/components/dashboard/dashboard_filters.py` - Reemplazar 1× `rx.icon_button` (línea 90) → `neuro_icon_action_button` con `tooltip_content="Limpiar filtros"`.

**Checkpoint**: Todos los módulos en spec.md convergidos. Verificar `reflex export --frontend-only --no-zip` sin errores.

---

## Notes

- En cada módulo, inspeccionar rápidamente si se usan DatePickers complejos. En tal caso, aplicar placeholder estático.
- Proporcionar textos inferidos como `tooltip_content="Eliminar"` o `tooltip_content="Ver Detalles"` según contexto a los botones sin label visual.
- `proveedores/` y `contratos/modal_incremento_ipc.py` ya estaban convergidos (verificados en auditoría 2026-07-05).
- `Gestión de IPC / Incrementos` (spec #13) ya cubierto en `contratos/modal_incremento_ipc.py` - sin work adicional.
- `asambleas/` y `dashboard/` son gaps menores (3 instancias de `rx.icon_button`).
- `saldos_favor.py` y `reportes.py` son los gaps mayores (~24 instancias de componentes no estandarizados).
