# Tasks: Floating Labels en Filtros Avanzados

**Input**: Design documents from `/specs/016-floating-labels-filters/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: No solicitados en spec - tareas de prueba excluidas.

**Organization**: Tareas organizadas por user story para implementación e testing independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (diferentes archivos, sin dependencias)
- **[Story]**: User story a la que pertenece (US1, US2, US3)
- Incluir rutas exactas de archivos en descripciones

---

## Phase 1: Setup (Infraestructura Compartida)

**Purpose**: Inicialización del proyecto y estructura básica

- [x] T001 [P] Agregar tokens CSS de floating label en `src/presentacion_reflex/styles.py`
- [x] T002 [P] Crear archivo `src/presentacion_reflex/components/shared/__init__.py` si no existe

---

## Phase 2: Foundational (Prerrequisitos Bloqueantes)

**Purpose**: Infraestructura core que DEBE completarse ANTES de cualquier user story

**⚠️ CRITICAL**: No se puede iniciar trabajo en user stories hasta completar esta fase

- [x] T003 Crear componente base `floating_input` en `src/presentacion_reflex/components/shared/floating_label.py`
- [x] T004 Crear componente base `floating_select` en `src/presentacion_reflex/components/shared/floating_label.py`
- [x] T005 [P] Agregar export de componentes en `src/presentacion_reflex/components/shared/__init__.py`

**Checkpoint**: Foundation lista - implementación de user stories puede comenzar

---

## Phase 3: User Story 1 - Floating Label para Inputs (Priority: P1) 🎯 MVP

**Goal**: Campo de texto con etiqueta visible permanente que se desplaza al recibir foco

**Independent Test**: Abrir formulario, verificar que label se anima correctamente al hacer clic en input

### Implementation for User Story 1

- [x] T006 [US1] Implementar `floating_input` con props: label, value, on_change, error, disabled en `src/presentacion_reflex/components/shared/floating_label.py`
- [x] T007 [US1] Implementar transición CSS `cubic-bezier(0.4, 0, 0.2, 1)` en 200ms para label
- [x] T008 [US1] Implementar detección de estado vacío/foco/con valor usando CSS `:focus-within` + `:not(:placeholder-shown)`
- [x] T009 [US1] Implementar estado de error con color `var(--red-9)` en label
- [x] T010 [US1] Agregar `<label>` HTML nativo con `htmlFor`/`id` para accesibilidad
- [x] T011 [US1] Crear wrapper neumórfico `neuro_floating_input` en `src/presentacion_reflex/components/neuro_elements.py`

**Checkpoint**: User Story 1 funcional y testeable independientemente - MVP listo

---

## Phase 4: User Story 2 - Floating Label para Selects (Priority: P2)

**Goal**: Campo select/dropdown con etiqueta visible permanente

**Independent Test**: Abrir formulario con select, verificar que label se anima y muestra opciones correctamente

### Implementation for User Story 2

- [x] T012 [US2] Implementar `floating_select` con props: label, value, on_change, options, error, disabled en `src/presentacion_reflex/components/shared/floating_label.py`
- [x] T013 [US2] Integrar `floating_select` con `neuro_select_root` existente
- [x] T014 [US2] Manejar valores preseleccionados (label arriba desde inicio)
- [x] T015 [US2] Crear wrapper neumórfico `neuro_floating_select` en `src/presentacion_reflex/components/neuro_elements.py`

**Checkpoint**: User Story 2 funcional - selects con floating label operativos

---

## Phase 5: User Story 3 - Integración con Dashboard Filters (Priority: P2)

**Goal**: Reemplazar placeholders en filtros del Dashboard por floating labels

**Independent Test**: Navegar al Dashboard, verificar que todos los filtros muestran labels permanentes

### Implementation for User Story 3

- [x] T016 [US3] Actualizar import en `src/presentacion_reflex/components/dashboard/dashboard_filters.py`
- [x] T017 [US3] Reemplazar filtro "Mes" usando `neuro_floating_select` en `src/presentacion_reflex/components/dashboard/dashboard_filters.py`
- [x] T018 [US3] Reemplazar filtro "Año" usando `neuro_floating_select` en `src/presentacion_reflex/components/dashboard/dashboard_filters.py`
- [x] T019 [US3] Reemplazar filtro "Asesor" usando `neuro_floating_select` en `src/presentacion_reflex/components/dashboard/dashboard_filters.py`

**Checkpoint**: Dashboard filters completo con floating labels

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras que afectan múltiples user stories

- [x] T020 [P] Verificar responsividad en viewport móvil (DevTools)
- [x] T021 [P] Verificar navegación por teclado (Tab + Enter)
- [x] T022 Ejecutar `ruff check` y `mypy` en archivos modificados
- [x] T023 Ejecutar validación visual en navegador (`reflex run --env dev`)
- [x] T024 [P] Documentar componentes en `src/presentacion_reflex/components/shared/floating_label.py` (Google Style docstrings)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias - puede iniciar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup - BLOQUEA todas las user stories
- **User Story 1 (Phase 3)**: Depende de Foundational - MVP
- **User Story 2 (Phase 4)**: Depende de Foundational - Puede ejecutarse en paralelo con US1
- **User Story 3 (Phase 5)**: Depende de US2 (necesita `neuro_floating_select`)
- **Polish (Phase 6)**: Depende de todas las user stories completas

### User Story Dependencies

- **User Story 1 (P1)**: Puede iniciar después de Foundational - Sin dependencias de otras stories
- **User Story 2 (P2)**: Puede iniciar después de Foundational - Independiente de US1
- **User Story 3 (P2)**: Depende de US2 completion (necesita `neuro_floating_select`)

### Within Each User Story

- Modelos/Componentes antes de integración
- Core implementation antes de wrappers neumórficos
- Story completa antes de siguiente prioridad

### Parallel Opportunities

- T001 y T002 pueden ejecutarse en paralelo
- T003 y T004 pueden ejecutarse en paralelo (mismo archivo)
- T005 puede ejecutarse en paralelo con T003/T004
- US1 y US2 pueden ejecutarse en paralelo después de Foundational
- T020, T021, T024 pueden ejecutarse en paralelo

---

## Parallel Example: User Story 1

```bash
# Componentes base en paralelo:
Task: "Implementar floating_input en shared/floating_label.py"
Task: "Implementar floating_select en shared/floating_label.py"

# Wrappers neumórficos en paralelo:
Task: "Crear neuro_floating_input en neuro_elements.py"
Task: "Crear neuro_floating_select en neuro_elements.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRITICAL - bloquea todas las stories)
3. Completar Phase 3: User Story 1
4. **PARAR y VALIDAR**: Testear User Story 1 independientemente
5. Desplegar/demo si está listo

### Incremental Delivery

1. Completar Setup + Foundational → Foundation lista
2. Agregar User Story 1 → Testear independientemente → Deploy/Demo (MVP!)
3. Agregar User Story 2 → Testear independientemente → Deploy/Demo
4. Agregar User Story 3 → Testear independientemente → Deploy/Demo
5. Cada story agrega valor sin romper stories anteriores

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Una vez Foundational completo:
   - Developer A: User Story 1 (floating_input)
   - Developer B: User Story 2 (floating_select)
3. Stories se completan e integran independientemente

---

## Notes

- [P] tasks = diferentes archivos, sin dependencias
- [Story] label mapea task a user story para trazabilidad
- Cada user story debe ser completable y testeable independientemente
- Verificar que tests fallan antes de implementar (si se solicitan)
- Commit después de cada task o grupo lógico
- Parar en cualquier checkpoint para validar story independientemente
- Evitar: tareas vagas, conflictos en mismo archivo, dependencias cross-story que rompan independencia
