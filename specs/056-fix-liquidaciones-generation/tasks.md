# Tasks: Corrección Generación de Liquidaciones de Propietarios

**Input**: Design documents from `/specs/056-fix-liquidaciones-generation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No se solicitaron tests explícitos en la especificación.

**Organization**: Tareas agrupadas por user story para implementación e independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos diferentes, sin dependencias)
- **[Story]**: User story a la que pertenece (US1, US2, US3)

## Phase 1: Setup (Infraestructura Compartida)

**Purpose**: Verificar estado actual del código y preparar entorno

- [X] T001 Verificar que la propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" tiene Contrato de Mandato activo en la base de datos ejecutando query de diagnóstico en `src/aplicacion/servicios/servicio_financiero.py`
- [X] T002 Verificar que la consulta de propietarios activos en `generar_liquidacion_masiva()` retorna resultados en `src/presentacion_reflex/state/liquidaciones_state.py:1085-1093`

---

## Phase 2: Foundational (Prerrequisitos Bloqueantes)

**Purpose**: Crear el Value Object de retorno que todos los user stories necesitan

**CRITICAL**: No se puede avanzar a User Stories sin completar esta fase

- [X] T003 Crear dataclass `ResultadoGeneracionPropietario` con campos `generadas`, `omitidas`, `errores` en `src/dominio/entidades/resultado_generacion.py`

**Checkpoint**: Value Object listo - las User Stories pueden comenzar

---

## Phase 3: User Story 1 - Generación Individual (Priority: P1)

**Goal**: Corregir la generación individual de liquidaciones para que funcione para todas las propiedades con Contrato de Mandato activo

**Independent Test**: Seleccionar "BRR EL SILENCIO ET 2 MZ D CS 4" en el formulario, verificar que se cargue el contrato y se cree la liquidación

### Implementation for User Story 1

- [X] T004 [US1] Diagnosticar por qué la propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" no aparece en el formulario de creación - verificar query de `load_filter_options()` en `src/presentacion_reflex/state/liquidaciones_state.py:222-229`
- [X] T005 [US1] Verificar que `handle_propiedad_change()` busca correctamente el contrato de mandato activo en `src/presentacion_reflex/state/liquidaciones_state.py:607-696`
- [X] T006 [US1] Verificar que `generar_liquidacion_mensual()` crea la liquidación correctamente en `src/aplicacion/servicios/servicio_financiero.py:155-263`

**Checkpoint**: Generación individual funciona para todas las propiedades elegibles

---

## Phase 4: User Story 2 - Generación Masiva (Priority: P1)

**Goal**: Corregir la generación masiva para que clasifique correctamente generadas, omitidas y errores

**Independent Test**: Ejecutar generación masiva, verificar toast muestra "X generadas, Y ya existían, Z con error"

### Implementation for User Story 2

- [X] T007 [US2] Modificar `generar_liquidacion_propietario()` para retornar `ResultadoGeneracionPropietario` en lugar de `int` en `src/aplicacion/servicios/servicio_financiero.py:265-317`
- [X] T008 [US2] Actualizar `generar_liquidacion_masiva()` para rastrear tres contadores (`total_generadas`, `total_omitidas`, `total_errores`) en `src/presentacion_reflex/state/liquidaciones_state.py:1100-1120`
- [X] T009 [US2] Actualizar lógica de toast para mostrar mensajes precisos según FR-006 y FR-008 en `src/presentacion_reflex/state/liquidaciones_state.py:1141-1147`
- [X] T010 [US2] Refinar manejo de excepciones: cambiar `except Exception` por manejo específico de errores reales en `src/presentacion_reflex/state/liquidaciones_state.py:1113-1117`

**Checkpoint**: Generación masiva muestra conteos correctos y no confunde duplicados con errores

---

## Phase 5: User Story 3 - Diagnóstico y Logging (Priority: P1)

**Goal**: Registrar errores detallados en logs para diagnóstico futuro

**Independent Test**: Revisar logs del servidor después de generación masiva con errores, verificar que se registra ID del propietario, ID del contrato y causa

### Implementation for User Story 3

- [X] T011 [US3] Agregar logging detallado para errores reales durante generación masiva (ID propietario, ID contrato, causa) en `src/presentacion_reflex/state/liquidaciones_state.py`
- [X] T012 [US3] Actualizar retorno de `generar_liquidacion_propietario()` para incluir detalles de errores en `src/aplicacion/servicios/servicio_financiero.py`

**Checkpoint**: Errores se registran en logs con información suficiente para diagnóstico

---

## Phase 6: Polish & Validación

**Purpose**: Validación final y limpieza

- [X] T013 Ejecutar escenarios de validación de `specs/056-fix-liquidaciones-generation/quickstart.md`
- [X] T014 Verificar que no se producen liquidaciones duplicadas (restricción UNIQUE) ejecutando generación masiva dos veces para el mismo período
- [X] T015 Verificar que el toast muestra "0 generadas, N ya existían" cuando todos los contratos ya tienen liquidaciones
- [X] T016 Verificar que el toast muestra "X generadas, Y ya existían" en caso mixto
- [X] T017 Verificar que errores reales se muestran como warning en el toast y se registran en logs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias - puede iniciar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup - BLOQUEA todas las User Stories
- **User Story 1 (Phase 3)**: Depende de Foundational - Generación individual
- **User Story 2 (Phase 4)**: Depende de Foundational + US1 (usa ResultadoGeneracionPropietario)
- **User Story 3 (Phase 5)**: Depende de US2 (usa logging de errores)
- **Polish (Phase 6)**: Depende de todas las User Stories completadas

### User Story Dependencies

- **User Story 1 (P1)**: Puede iniciar después de Foundational - Sin dependencias en otras stories
- **User Story 2 (P1)**: Depende de US1 (modifica la misma función de servicio)
- **User Story 3 (P1)**: Depende de US2 (usa el nuevo manejo de errores)

### Within Each User Story

- Diagnóstico antes de implementación
- Modelo/Dominio antes de Servicio
- Servicio antes de State/UI
- Core implementation antes de validación

### Parallel Opportunities

- T001 y T002 pueden ejecutarse en paralelo (diagnóstico independiente)
- T004, T005, T006 pueden ejecutarse en paralelo (verificación de componentes US1)
- T013-T017 pueden ejecutarse en paralelo (validación independiente)

---

## Parallel Example: User Story 1

```bash
# Diagnóstico en paralelo:
Task: "Verificar query de propiedades activas en load_filter_options()"
Task: "Verificar handle_propiedad_change() busca contrato correctamente"
Task: "Verificar generar_liquidacion_mensual() crea liquidación"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (Value Object)
3. Completar Phase 3: User Story 1 (generación individual)
4. Completar Phase 4: User Story 2 (generación masiva)
5. **PARAR Y VALIDAR**: Ejecutar escenarios de quickstart.md
6. Desplegar si está listo

### Incremental Delivery

1. Setup + Foundational → Fundación lista
2. US1 → Validar generación individual → MVP parcial
3. US2 → Validar generación masiva → MVP completo
4. US3 → Agregar logging → Versión final
5. Polish → Validación completa → Despliegue

---

## Notes

- [P] tasks = archivos diferentes, sin dependencias
- [Story] label mapea tarea a user story para trazabilidad
- Cada user story debe ser independently complet y testable
- Verificar que los escenarios de quickstart.md pasan después de cada phase
- Commit después de cada tarea o grupo lógico
- Parar en cualquier checkpoint para validar independientemente
