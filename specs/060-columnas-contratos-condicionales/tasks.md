# Tasks: Columnas Condicionales en Tabla de Contratos

**Input**: Design documents from `/specs/060-columnas-contratos-condicionales/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Preparar el DTO y repositorio que serán consumidos por todas las historias de usuario

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 [P] Agregar campo `informacion_adicional: str | None = None` al modelo `ContratoDict` en `src/presentacion_reflex/state/contratos_state.py`
- [x] T002 [P] Agregar función `construir_informacion_adicional(contrato: dict) -> str | None` en `src/presentacion_reflex/state/contratos_state.py` para formatear datos según tipo de contrato
- [x] T003 Modificar query en `repositorio_contrato_arrendamiento_postgres.py` para incluir LEFT JOIN con CODEUDORES y PERSONA (obtener `codeudor_nombre`, `codeudor_telefono`) en `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py`
- [x] T004 Modificar función `listar_arrendamientos_paginado()` para incluir campos de codeudor en el resultado en `src/infraestructura/persistencia/repositories/repo_contrato_arrendamiento.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 2: User Story 1 - Visualización de información adicional por tipo de contrato (Priority: P1) 🎯 MVP

**Goal**: Mostrar columna "Información Adicional" en la tabla de contratos con datos específicos según tipo

**Independent Test**: Cargar tabla y verificar que Mandatos muestran consignatario/banco/cuenta y Arrendamientos muestran codeudor/teléfono

### Implementation for User Story 1

- [x] T005 [US1] Agregar columna "Información Adicional" a la lista de columnas en `render_table_view()` en `src/presentacion_reflex/pages/contratos.py`
- [x] T006 [US1] Implementar lógica de renderizado condicional para la columna (pipe-separated format) en `src/presentacion_reflex/pages/contratos.py`
- [x] T007 [US1] Integrar campo `informacion_adicional` en la carga de datos del state `load_contratos()` en `src/presentacion_reflex/state/contratos_state.py`
- [x] T008 [US1] Manejar caso "No registrado" cuando los campos estén vacíos en `src/presentacion_reflex/state/contratos_state.py`

**Checkpoint**: User Story 1 fully functional - tabla muestra información adicional correctamente

---

## Phase 3: User Story 2 - Validación de integridad de datos (Priority: P2)

**Goal**: Verificar que la información proviene de entidades y relaciones correctas en la BD

**Independent Test**: Ejecutar consultas de validación contra la BD para verificar integridad

### Implementation for User Story 2

- [x] T009 [US2] Crear script de validación SQL para verificar relaciones Mandato-Consignatario en `scripts/validacion/validar_datos_contratos.py`
- [x] T010 [US2] Crear script de validación SQL para verificar relaciones Arrendamiento-Codeudor-Persona en `scripts/validacion/validar_datos_contratos.py`
- [x] T011 [US2] Ejecutar validación en BD de producción/staging y documentar resultados en `specs/060-columnas-contratos-condicionales/validacion_datos.md`

**Checkpoint**: Data integrity validated - no orphaned relations

---

## Phase 4: User Story 3 - Consistencia visual y funcional (Priority: P3)

**Goal**: Asegurar que las nuevas columnas mantienen consistencia visual con el resto de la tabla

**Independent Test**: Verificar estilo, alineación y comportamiento de ordenamiento de la nueva columna

### Implementation for User Story 3

- [x] T012 [US3] Aplicar estilos consistentes (tipografía, espaciado, colores) a la columna en `src/presentacion_reflex/pages/contratos.py`
- [x] T013 [US3] Habilitar ordenamiento alfabético en la columna "Información Adicional" en `src/presentacion_reflex/pages/contratos.py`
- [x] T014 [P] [US3] Verificar comportamiento responsive en diferentes viewports (desktop, tablet, mobile)
- [x] T015 [P] [US3] Actualizar vista card en `src/presentacion_reflex/components/contratos/tarjeta_contrato.py` si aplica

**Checkpoint**: All user stories complete - UI consistente y funcional

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y validación final

- [ ] T016 Ejecutar validación de quickstart.md completa
- [ ] T017 Ejecutar `reflex run --env dev` y verificar consola limpia (sin errores)
- [ ] T018 Documentar cambios en ESTADO_TAREAS.md
- [ ] T019 [P] Ejecutar linting (ruff, black) en archivos modificados
- [ ] T020 Realizar commit con mensaje convencional: `feat(contratos): agregar columna informacion adicional condicional`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Phase 1 completion
- **User Story 2 (Phase 3)**: Can run in parallel with US1 (validación independiente)
- **User Story 3 (Phase 4)**: Depends on US1 completion (necesita columna existente)
- **Polish (Phase 5)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 1 - Core functionality
- **User Story 2 (P2)**: Independent validation - can run in parallel with US1
- **User Story 3 (P3)**: Depends on US1 - Polish existing implementation

### Within Each User Story

- Models/State before UI
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- T001 y T002 pueden ejecutarse en paralelo (mismo archivo, diferentes funciones)
- T009 y T010 pueden ejecutarse en paralelo (scripts de validación)
- T014 y T015 pueden ejecutarse en paralelo (responsive y card)
- User Story 2 puede ejecutarse en paralelo con User Story 1

---

## Parallel Example: Phase 1

```bash
# Launch foundational tasks together:
Task: "Agregar campo informacion_adicional a ContratoDict en contratos_state.py"
Task: "Agregar función construir_informacion_adicional en contratos_state.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (DTO + Repository)
2. Complete Phase 2: User Story 1
3. **STOP and VALIDATE**: Test User Story 1 independently
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Validate data integrity → Document
4. Add User Story 3 → Polish UI → Final Deploy

### Validation Commands

```bash
# Ejecutar servidor en modo desarrollo
reflex run --env dev

# Verificar consola limpia (DevTools F12)
# Navegar a página de contratos
# Verificar columna "Información Adicional" visible
```

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No se requieren migraciones de BD - todos los campos ya existen
- Cambios mínimos: solo 3 archivos principales a modificar
