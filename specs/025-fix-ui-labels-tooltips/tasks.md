---
description: "Task list for Restablecer Etiquetas Flotantes y Tooltips implementation"
---

# Tasks: Restablecer Etiquetas Flotantes y Tooltips

**Input**: Design documents from `specs/025-fix-ui-labels-tooltips/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Testing is manual and visual, as described in quickstart.md. Code tests are not required for these UI tweaks unless requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Revisar `src/presentacion_reflex/styles.py` para identificar `Z_TOOLTIP`, `Z_POPOVER` y transiciones base requeridas por la funcionalidad.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Asegurar que el sistema de tokens y z-index en `src/presentacion_reflex/styles.py` esté configurado y exportado correctamente para su uso por los componentes.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Etiquetas Flotantes (Priority: P1) 🎯 MVP

**Goal**: Restaurar las etiquetas flotantes en todos los inputs para mejorar el contexto y la UX al rellenar formularios.

**Independent Test**: Navegar a un formulario, hacer foco en un input, verificar que la etiqueta se desplaza arriba y que se mantiene si hay texto, o regresa si se borra el texto y se quita el foco.

### Implementation for User Story 1

- [x] T003 [US1] Modificar `src/presentacion_reflex/componentes/inputs.py` para agregar las clases de estado (focus/filled) a los controles de formulario, o actualizar los estilos base en `styles.py` si se maneja globalmente, restaurando el comportamiento flotante.
- [x] T004 [US1] Validar el comportamiento de las etiquetas flotantes con `rx.select` u otros inputs especiales en el mismo componente `inputs.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Tooltips en Botones (Priority: P2)

**Goal**: Mostrar un tooltip descriptivo en los botones interactivos al hacer hover, para mejorar la accesibilidad y entendimiento.

**Independent Test**: Hacer hover sobre un botón principal o secundario y confirmar que aparece un tooltip descriptivo sin errores de z-index (superposición).

### Implementation for User Story 2

- [x] T005 [P] [US2] Modificar `src/presentacion_reflex/componentes/botones.py` para envolver los componentes de botón (`rx.button` o similares) con un `rx.tooltip` nativo de Reflex.
- [x] T006 [US2] Asegurar que el `rx.tooltip` en `botones.py` aplique los tokens de estilo y el índice `Z_TOOLTIP` adecuado (heredado de `styles.py`).

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T007 [P] Ejecutar la validación manual local descrita en `quickstart.md` (`reflex run --env dev`).
- [x] T008 [P] Verificar que los cambios en inputs y botones no generen regresiones visuales en módulos principales de la aplicación.
- [x] T009 Exportar el frontend de Reflex para validar compilación (`reflex export --frontend-only --no-zip`) y asegurar que no hay errores de sintaxis CSS/JS.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially in priority order (P1 → P2), o en paralelo si no se cruzan.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independently testable.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel.
- User Story 1 y User Story 2 tocan archivos diferentes (`inputs.py` y `botones.py`), por lo que T003 y T005 pueden desarrollarse en paralelo si `styles.py` (Fundación) ya está estable.

---

## Parallel Example: User Story 1 y 2

```bash
# Developer A trabaja en User Story 1 (inputs)
Task: "Modificar src/presentacion_reflex/componentes/inputs.py para agregar las clases de estado..."

# Developer B trabaja en User Story 2 (botones)
Task: "Modificar src/presentacion_reflex/componentes/botones.py para envolver los componentes de botón..."
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories
