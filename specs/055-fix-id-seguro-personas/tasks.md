# Tasks: Fix ID Seguro - Personas

**Input**: Design documents from `/specs/055-fix-id-seguro-personas/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Tests manuales en navegador (ver quickstart.md)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar entorno de desarrollo

- [X] T001 Verificar que el servidor Reflex está ejecutándose en `http://localhost:3000/personas`
- [X] T002 Abrir consola del navegador (F12 → Console) para monitorear errores

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verificar el error actual antes del fix

**⚠️ CRITICAL**: Confirmar que el error existe antes de implementar la corrección

- [X] T003 Navegar a `/personas` → Click "Nueva Persona" → Completar Paso 1 → Click "Siguiente"
- [X] T004 Seleccionar "Arrendatario" en Paso 2 → Click "Siguiente"
- [X] T005 Verificar que el error `PopoverPortal must be used within Popover` aparece en consola al renderizar Paso 3
- [X] T006 Confirmar que el campo "ID Seguro" no funciona correctamente (dropdown no se abre o genera error)

**Checkpoint**: Error confirmado - listo para implementar fix

---

## Phase 3: User Story 1 & 2 - Fix del componente selector_busqueda (Priority: P1) 🎯 MVP

**Goal**: Corregir el error `PopoverPortal must be used within Popover` reemplazando `rx.popover.content` por patrón CSS positioning

**Independent Test**: Verificar que la consola del navegador no muestra errores de Radix UI al renderizar el combobox de ID Seguro

### Implementation for User Story 1 & 2

- [X] T007 [US1] [US2] Leer archivo `src/presentacion_reflex/components/personas/modal_form.py` y localizar función `selector_busqueda()` (líneas 14-84)
- [X] T008 [US1] [US2] Reemplazar bloque `rx.popover.content(...)` (líneas 44-80) por patrón CSS positioning usando `rx.box` con `position="absolute"` - ver patrón en `src/presentacion_reflex/components/shared/searchable_select.py` (líneas 75-126)
- [X] T009 [US1] [US2] Actualizar imports en `modal_form.py` si es necesario (agregar `from src.presentacion_reflex import styles` si no existe)
- [X] T010 [US1] [US2] Verificar que la función `selector_busqueda()` mantiene la misma interfaz (parámetros de entrada y salida)

**Checkpoint**: Fix implementado - listo para validación

---

## Phase 4: User Story 3 - Validación del fix (Priority: P1)

**Goal**: Verificar que el fix resuelve el error sin introducir regresiones

**Independent Test**: Seguir escenarios de validación en quickstart.md

### Validation Tasks

- [X] T011 [US3] Recargar navegador (Ctrl+F5) para limpiar caché
- [X] T012 [US3] Navegar a `/personas` → Click "Nueva Persona" → Completar Paso 1 → Click "Siguiente"
- [X] T013 [US3] Seleccionar "Arrendatario" en Paso 2 → Click "Siguiente"
- [X] T014 [US3] Verificar que el campo "ID Seguro" renderiza SIN errores en consola
- [X] T015 [US3] Click en el campo "ID Seguro" → Verificar que el dropdown se abre correctamente
- [X] T016 [US3] Escribir texto de búsqueda → Verificar que las opciones se filtran
- [X] T017 [US3] Seleccionar una opción → Verificar que se registra en el campo
- [X] T018 [US3] Completar campos restantes (Nombre Habitante, Teléfono) → Click "Guardar"
- [X] T019 [US3] Verificar que la persona se crea exitosamente con el seguro asignado
- [X] T020 [US3] Verificar en detalles de la persona que el tab "Arrendatario" muestra el seguro correcto

**Checkpoint**: Fix validado - funcionalidad restaurada

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verificaciones finales y documentación

- [X] T021 Verificar que no hay regresiones en otros formularios que usen `floating_select` (Paso 1: Tipo Doc)
- [X] T022 Ejecutar verificación de sintaxis: `python -m py_compile src/presentacion_reflex/components/personas/modal_form.py`
- [X] T023 Verificar que el estilo visual del dropdown es consistente con el resto de la aplicación
- [X] T024 Confirmar que la consola del navegador está limpia (0 errores de JavaScript)
- [X] T025 Documentar el fix en commit message con formato Conventional Commits: `fix(personas): resolver error PopoverPortal en selector de seguro`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS implementation
- **User Story 1 & 2 (Phase 3)**: Depends on Foundational phase (error confirmado)
- **User Story 3 (Phase 4)**: Depends on Phase 3 (fix implementado)
- **Polish (Phase 5)**: Depends on Phase 4 (fix validado)

### User Story Dependencies

- **User Story 1 (P1)**: Crear Persona con rol Arrendatario - depends on fix
- **User Story 2 (P1)**: Renderizado correcto del combobox - IS the fix
- **User Story 3 (P2)**: Validación y persistencia - depends on US1 and US2

### Within Each Phase

- T003-T006: Secuenciales (verificar error antes del fix)
- T007-T010: Secuenciales (implementar fix en orden lógico)
- T011-T020: Secuenciales (validación paso a paso)
- T021-T025: Parcialmente paralelizables

### Parallel Opportunities

- T021 y T022 pueden ejecutarse en paralelo (diferentes verificaciones)
- T023 y T024 pueden ejecutarse en paralelo (estilo vs consola)

---

## Parallel Example: Validation Phase

```bash
# Verificaciones paralelas después del fix:
Task: "Verificar sintaxis Python"
Task: "Verificar estilo visual del dropdown"
Task: "Verificar consola limpia de errores"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (preparar entorno)
2. Complete Phase 2: Foundational (confirmar error)
3. Complete Phase 3: Fix del componente (T007-T010)
4. **STOP and VALIDATE**: Seguir Phase 4 para verificar fix
5. Deploy si todo funciona correctamente

### Single File Fix

Este es un fix puntual que afecta un solo archivo:
- **Archivo a modificar**: `src/presentacion_reflex/components/personas/modal_form.py`
- **Función a modificar**: `selector_busqueda()` (líneas 14-84)
- **Patrón de referencia**: `src/presentacion_reflex/components/shared/searchable_select.py`
- **Sin cambios en**: `personas_state.py`, base de datos, otros componentes

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after completing Phase 3 (fix implementado) and Phase 4 (fix validado)
- Stop at any checkpoint to validate independently
- El fix es de bajo riesgo: solo cambia la implementación del dropdown, no la lógica de negocio
