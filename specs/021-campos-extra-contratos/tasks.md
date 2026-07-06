# Tasks: campos-extra-contratos

**Input**: Design documents from `specs/021-campos-extra-contratos/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: No se solicitaron tests explícitamente en la especificación. Se incluye una tarea de validación manual (quickstart).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Migración de base de datos y actualización de la entidad de dominio compartida.

- [ ] T001 Ejecutar migración SQL: `ALTER TABLE contratos ADD COLUMN enlace_video VARCHAR(512); ALTER TABLE contratos ADD COLUMN responsable_deposito_id INTEGER REFERENCES asesores(id);`
- [ ] T002 Agregar atributos `enlace_video: str = ""` y `responsable_deposito_id: Optional[int] = None` a la clase `Contrato` en `src/dominio/contrato.py`
- [ ] T003 Actualizar queries SELECT (método `_mapear_contrato` o equivalente) para incluir `enlace_video` y `responsable_deposito_id` en `src/infraestructura/repositorio_contrato.py`
- [ ] T004 Actualizar query INSERT en método `crear` para incluir `enlace_video` y `responsable_deposito_id` en `src/infraestructura/repositorio_contrato.py`
- [ ] T005 Actualizar query UPDATE en método `actualizar` para incluir `enlace_video` y `responsable_deposito_id` en `src/infraestructura/repositorio_contrato.py`

**Checkpoint**: La capa de persistencia ahora soporta los nuevos campos. Toda operación CRUD los incluye.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Actualización del servicio de aplicación para orquestar los nuevos campos.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Actualizar método `crear_contrato` en `src/aplicacion/contrato_service.py` para pasar `enlace_video` y `responsable_deposito_id` al repositorio
- [ ] T007 Actualizar método `actualizar_contrato` en `src/aplicacion/contrato_service.py` para pasar `enlace_video` y `responsable_deposito_id` al repositorio
- [ ] T008 Agregar campos `enlace_video: str = ""` y `responsable_deposito_id: int = 0` al State `EstadoContrato` en `src/presentacion_reflex/contratos.py`

**Checkpoint**: Foundation ready — implementación de user stories puede comenzar.

---

## Phase 3: User Story 1 — Video de recibo en contratos (Priority: P1) 🎯 MVP

**Goal**: Permitir al usuario registrar y consultar la URL del video de recibo del inmueble en ambos tipos de contrato.

**Independent Test**: Crear un contrato de Mandato o Arrendamiento con un enlace de video, guardarlo, y verificar que al re-abrir el modal el enlace aparece precargado.

### Implementation for User Story 1

- [ ] T009 [US1] Agregar campo `rx.input` para "Enlace de video" en la función `modal_contrato_mandato()` en `src/presentacion_reflex/contratos.py`, usando `on_change=EstadoContrato.set_enlace_video`
- [ ] T010 [P] [US1] Agregar campo `rx.input` para "Enlace de video" en la función `modal_contrato_arrendamiento()` en `src/presentacion_reflex/contratos.py`, usando `on_change=EstadoContrato.set_enlace_video`
- [ ] T011 [US1] Actualizar método `guardar_contrato_mandato` en `EstadoContrato` para incluir `enlace_video` en el objeto `Contrato` enviado al servicio, en `src/presentacion_reflex/contratos.py`
- [ ] T012 [P] [US1] Actualizar método `guardar_contrato_arrendamiento` en `EstadoContrato` para incluir `enlace_video` en el objeto `Contrato` enviado al servicio, en `src/presentacion_reflex/contratos.py`
- [ ] T013 [US1] Actualizar método `editar_contrato` en `EstadoContrato` para cargar `enlace_video` desde el contrato seleccionado, en `src/presentacion_reflex/contratos.py`
- [ ] T014 [US1] Actualizar método de reset/limpieza del formulario para reiniciar `enlace_video` a `""` al cerrar el modal, en `src/presentacion_reflex/contratos.py`

**Checkpoint**: User Story 1 funcional — el enlace de video se crea, edita y visualiza en ambos tipos de contrato.

---

## Phase 4: User Story 2 — Responsable del depósito en Mandato (Priority: P1)

**Goal**: Permitir seleccionar un asesor activo como responsable del depósito exclusivamente en contratos de Mandato.

**Independent Test**: Crear un contrato de Mandato, seleccionar un asesor del ComboBox, guardar, y verificar que al editar el contrato el asesor aparece seleccionado.

### Implementation for User Story 2

- [ ] T015 [US2] Agregar componente `rx.select` (ComboBox) para "Responsable del depósito" en la función `modal_contrato_mandato()` en `src/presentacion_reflex/contratos.py`, poblado con `EstadoContrato.asesores` y usando `on_change=EstadoContrato.set_responsable_deposito_id`
- [ ] T016 [US2] Manejar estado vacío de asesores: si `EstadoContrato.asesores` está vacío, mostrar texto informativo "No hay asesores activos" dentro del selector, en `src/presentacion_reflex/contratos.py`
- [ ] T017 [US2] Actualizar método `guardar_contrato_mandato` para incluir `responsable_deposito_id` en el objeto `Contrato` enviado al servicio, en `src/presentacion_reflex/contratos.py`
- [ ] T018 [US2] Actualizar método `editar_contrato` para cargar `responsable_deposito_id` desde el contrato seleccionado cuando `tipo_contrato == "mandato"`, en `src/presentacion_reflex/contratos.py`
- [ ] T019 [US2] Asegurar que `cargar_asesores()` se invoque al abrir `modal_contrato_mandato()` (dentro de `abrir_modal_mandato`) para poblar el selector dinámicamente, en `src/presentacion_reflex/contratos.py`
- [ ] T020 [US2] Actualizar método de reset/limpieza del formulario para reiniciar `responsable_deposito_id` a `0` al cerrar el modal, en `src/presentacion_reflex/contratos.py`

**Checkpoint**: User Story 2 funcional — el ComboBox muestra asesores activos, se puede seleccionar uno, y persiste correctamente.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validaciones finales, estilo visual y verificación E2E.

- [ ] T021 [P] Verificar que el estilo visual de los nuevos campos (Enlace de video e input, Responsable del depósito y select) respeten el Design System (Anthropic/Claude) del proyecto en `src/presentacion_reflex/contratos.py`
- [ ] T022 [P] Agregar validación de URL en el frontend: si el usuario ingresa texto sin formato http/https, mostrar indicador visual de error, en `src/presentacion_reflex/contratos.py`
- [ ] T023 Ejecutar validación completa siguiendo el `quickstart.md`: crear, editar, guardar y consultar contratos con los nuevos campos
- [ ] T024 Verificar que contratos existentes (sin los nuevos campos) se carguen correctamente sin errores (compatibilidad retroactiva)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — starts immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **User Stories (Phase 3, 4)**: Depend on Phase 2 completion
  - US1 and US2 can proceed in parallel (different form sections, same file but different functions)
- **Polish (Phase 5)**: Depends on Phase 3 and Phase 4 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 — No dependencies on US2
- **User Story 2 (P1)**: Can start after Phase 2 — No dependencies on US1. Reuses existing `cargar_asesores()` method.

### Within Each User Story

- Models/entities before services (already done in Phase 1/2)
- Service updates before UI components
- UI form fields before save/edit logic
- Save/edit before reset/cleanup

### Parallel Opportunities

- T003, T004, T005 within Phase 1 can run in parallel (different SQL operations in same file, but non-overlapping)
- T009/T010 (mandato/arrendamiento modals) can be parallel
- T011/T012 (guardar mandato/arrendamiento) can be parallel
- T021/T022 (polish tasks) can be parallel
- US1 and US2 phases can be parallel

---

## Parallel Example: User Story 1

```bash
# Launch modal input additions in parallel:
Task: "T009 — Agregar rx.input 'Enlace de video' en modal_contrato_mandato()"
Task: "T010 — Agregar rx.input 'Enlace de video' en modal_contrato_arrendamiento()"

# Launch save method updates in parallel:
Task: "T011 — Actualizar guardar_contrato_mandato con enlace_video"
Task: "T012 — Actualizar guardar_contrato_arrendamiento con enlace_video"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migración DB + entidad)
2. Complete Phase 2: Foundational (servicio + state)
3. Complete Phase 3: User Story 1 (enlace_video en ambos modales)
4. **STOP and VALIDATE**: Verificar enlace_video persiste en crear/editar
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Polish → Final validation with quickstart.md

---

## Notes

- [P] tasks = different files or non-overlapping sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each phase or logical group
- Stop at any checkpoint to validate story independently
- **Hallazgo clave**: El sistema usa UNA sola tabla `contratos` con campo `tipo_contrato`, no tablas separadas
- El servicio `obtener_asesores_activos()` ya existe y se reutiliza para el ComboBox
