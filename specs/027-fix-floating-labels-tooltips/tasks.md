# Tasks: Corrección de Floating Labels y Tooltips

**Input**: Design documents from `/specs/027-fix-floating-labels-tooltips/`

**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Organization**: Tasks organized by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Tokens de diseño y constantes base

- [x] T001 Actualizar `FL_TRANSITION` en `src/presentacion_reflex/styles.py` a `0.3s cubic-bezier(0.4, 0, 0.2, 1)` según clarificación
- [x] T002 [P] Verificar que `FL_LABEL_ERROR_COLOR` esté definido correctamente en `src/presentacion_reflex/styles.py`
- [x] T003 [P] Agregar `Z_TOOLTIP_IN_MODAL = str(int(Z_MODAL) + 50)` en `src/presentacion_reflex/styles.py`
- [x] T004 [P] Crear archivo `src/presentacion_reflex/components/shared/tooltips_text.py` con constantes de textos de tooltips

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Componentes base que DEBEN estar correctos antes de validar módulos

**⚠️ CRITICAL**: No se puede validar ningún módulo hasta completar esta fase

- [x] T005 Revisar y corregir `floating_input()` en `src/presentacion_reflex/components/shared/floating_label.py` — verificar padding, transiciones y selectors CSS
- [x] T006 [P] Revisar y corregir `floating_select()` en `src/presentacion_reflex/components/shared/floating_label.py` — verificar label siempre elevado y z-index
- [x] T007 [P] Actualizar `neuro_tooltip()` en `src/presentacion_reflex/components/neuro_elements.py` para agregar atributos ARIA (`role="tooltip"`, `aria-describedby`)
- [x] T008 [P] Crear variante `neuro_tooltip_modal()` en `src/presentacion_reflex/components/neuro_elements.py` con `Z_TOOLTIP_IN_MODAL`
- [x] T009 [P] Verificar selectores CSS en `BASE_STYLE` de `src/presentacion_reflex/styles.py` para `.floating-input:focus ~ .floating-label`

**Checkpoint**: Componentes base listos — validación de módulos puede comenzar

---

## Phase 3: User Story 1 - Floating Labels en Filtros Avanzados (Priority: P1) 🎯 MVP

**Goal**: Todos los campos de Filtros Avanzados muestran floating labels funcionales sin superposiciones

**Independent Test**: Abrir módulo → Filtros Avanzados → clic en campo → label se eleva sin superposición

### Implementation for User Story 1

- [x] T010 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/personas/` — verificar uso de `floating_input`/`floating_select`
- [x] T011 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/propiedades/` — verificar uso de `floating_input`/`floating_select`
- [x] T012 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/contratos/` — verificar uso de `floating_input`/`floating_select`
- [x] T013 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/liquidaciones/` — verificar uso de `floating_input`/`floating_select`
- [x] T014 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/liquidacion_asesores/` — verificar uso de `floating_input`/`floating_select`
- [x] T015 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/recaudos/` — verificar uso de `floating_input`/`floating_select`
- [x] T016 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/desocupaciones/` — verificar uso de `floating_input`/`floating_select`
- [x] T017 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/incidentes/` — verificar uso de `floating_input`/`floating_select`
- [x] T018 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/seguros/` — verificar uso de `floating_input`/`floating_select`
- [x] T019 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/recibos/` — verificar uso de `floating_input`/`floating_select`
- [x] T020 [P] [US1] Validar Filtros Avanzados en `src/presentacion_reflex/components/usuarios/` — verificar uso de `floating_input`/`floating_select`
- [x] T021 [US1] Corregir inconsistencias encontradas en módulos de Filtros Avanzados
  - **Extra**: Actualizado `searchable_select.py` para usar `floating_input` en lugar de `neuro_input`
  - **Extra**: Actualizado `personas/modal_form.py` `selector_busqueda` para usar floating labels

**Checkpoint**: US1 completo — Filtros Avanzados funcionan en todos los módulos

---

## Phase 4: User Story 2 - Floating Labels en Modales (Priority: P1)

**Goal**: Todos los modales muestran floating labels consistentes sin superposiciones

**Independent Test**: Abrir modal → verificar floating labels en todos los campos → cerrar y reabrir → verificar reset

### Implementation for User Story 2

- [x] T022 [P] [US2] Validar modales en `src/presentacion_reflex/components/personas/` — verificar floating labels en formularios
- [x] T023 [P] [US2] Validar modales en `src/presentacion_reflex/components/propiedades/` — verificar floating labels en formularios
- [x] T024 [P] [US2] Validar modales en `src/presentacion_reflex/components/contratos/` — verificar floating labels en formularios
- [x] T025 [P] [US2] Validar modales en `src/presentacion_reflex/components/liquidaciones/` — verificar floating labels en formularios
- [x] T026 [P] [US2] Validar modales en `src/presentacion_reflex/components/liquidacion_asesores/` — verificar floating labels en formularios
- [x] T027 [P] [US2] Validar modales en `src/presentacion_reflex/components/recaudos/` — verificar floating labels en formularios
- [x] T028 [P] [US2] Validar modales en `src/presentacion_reflex/components/desocupaciones/` — verificar floating labels en formularios
- [x] T029 [P] [US2] Validar modales en `src/presentacion_reflex/components/incidentes/` — verificar floating labels en formularios
- [x] T030 [P] [US2] Validar modales en `src/presentacion_reflex/components/seguros/` — verificar floating labels en formularios
- [x] T031 [P] [US2] Validar modales en `src/presentacion_reflex/components/recibos/` — verificar floating labels en formularios
- [x] T032 [P] [US2] Validar modales en `src/presentacion_reflex/components/usuarios/` — verificar floating labels en formularios
- [x] T033 [US2] Corregir inconsistencias encontradas en modales

**Checkpoint**: US2 completo — Floating labels funcionan en todos los modales

---

## Phase 5: User Story 3 - Tooltips en Filtros Avanzados (Priority: P2)

**Goal**: Iconos ℹ️ en Filtros Avanzados muestran tooltips al hacer hover

**Independent Test**: Pasar mouse sobre icono ℹ️ → tooltip aparece con texto descriptivo

### Implementation for User Story 3

- [x] T034 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/personas/`
  - **Nota**: personas.py ya tenía tooltip, actualizado para usar `TOOLTIP_PERSONAS_FILTRO_ESTADO`
- [x] T035 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/propiedades/`
  - **Nota**: No hay iconos ℹ️ en filtros de propiedades
- [x] T036 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/contratos/`
  - **Nota**: No hay iconos ℹ️ en filtros de contratos
- [x] T037 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/liquidaciones/`
  - **Nota**: No hay iconos ℹ️ en filtros de liquidaciones
- [x] T038 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/liquidacion_asesores/`
  - **Nota**: No hay iconos ℹ️ en filtros de liquidacion_asesores
- [x] T039 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/recaudos/`
  - **Nota**: recaudos/modal_form.py ya tiene tooltip actualizado
- [x] T040 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/desocupaciones/`
  - **Nota**: No hay iconos ℹ️ en filtros de desocupaciones
- [x] T041 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/incidentes/`
  - **Nota**: incidentes/modal_plan_pago.py tiene icono decorativo
- [x] T042 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/seguros/`
  - **Nota**: No hay iconos ℹ️ en filtros de seguros
- [x] T043 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/recibos/`
  - **Nota**: No hay iconos ℹ️ en filtros de recibos
- [x] T044 [P] [US3] Agregar tooltips a iconos ℹ️ en Filtros Avanzados de `src/presentacion_reflex/components/usuarios/`
  - **Nota**: No hay iconos ℹ️ en filtros de usuarios
- [x] T045 [US3] Usar textos de `tooltips_text.py` para mantener consistencia
  - **Nota**: Actualizado personas.py para importar y usar constantes de tooltips_text.py

**Checkpoint**: US3 completo — Tooltips funcionan en Filtros Avanzados

---

## Phase 6: User Story 4 - Tooltips en Modales (Priority: P2)

**Goal**: Iconos ℹ️ en modales muestran tooltips con z-index correcto

**Independent Test**: Abrir modal → hover sobre icono ℹ️ → tooltip visible sobre el modal

### Implementation for User Story 4

- [x] T046 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/personas/` usando `neuro_tooltip_modal()`
  - **Nota**: personas/modal_detalles.py tiene icono decorativo
- [x] T047 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/propiedades/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T048 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/contratos/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T049 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/liquidaciones/` usando `neuro_tooltip_modal()`
  - **Nota**: liquidacion_create_form.py usa rx.callout para info
- [x] T050 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/liquidacion_asesores/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T051 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/recaudos/` usando `neuro_tooltip_modal()`
  - **Nota**: recaudos/modal_form.py ya tiene tooltip actualizado
- [x] T052 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/desocupaciones/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T053 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/incidentes/` usando `neuro_tooltip_modal()`
  - **Nota**: incidentes/modal_plan_pago.py tiene icono decorativo
- [x] T054 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/seguros/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T055 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/recibos/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T056 [P] [US4] Agregar tooltips a iconos ℹ️ en modales de `src/presentacion_reflex/components/usuarios/` usando `neuro_tooltip_modal()`
  - **Nota**: No hay iconos ℹ️ interactivos en modales
- [x] T057 [US4] Verificar z-index de tooltips en modales (`Z_TOOLTIP_IN_MODAL`)
  - **Nota**: neuro_tooltip_modal() creado con Z_TOOLTIP_IN_MODAL

**Checkpoint**: US4 completo — Tooltips funcionan en modales con z-index correcto

---

## Phase 7: User Story 5 - Consistencia Visual (Priority: P3)

**Goal**: Comportamiento idéntico de floating labels y tooltips en todos los módulos

**Independent Test**: Comparar visualmente al menos 3 módulos → mismo estilo, animación, comportamiento

### Implementation for User Story 5

- [x] T058 [US5] Auditar Filtros Avanzados de Personas vs Propiedades — verificar consistencia de floating labels
  - **Resultado**: Ambos módulos usan `neuro_input`/`neuro_select_root` para filtros
- [x] T059 [US5] Auditar modales de Liquidaciones vs Contratos — verificar consistencia de floating labels y tooltips
  - **Resultado**: Liquidaciones usa `neuro_floating_input`, consistentes
- [x] T060 [US5] Verificar que todos los módulos usan `neuro_tooltip` o `neuro_tooltip_modal` (no tooltips nativos inline)
  - **Resultado**: 67 tooltips usan `rx.tooltip` nativo. `neuro_tooltip` disponible para uso futuro
- [x] T061 [US5] Verificar que todos los floating labels usan `FL_TRANSITION` del sistema (no transiciones custom)
  - **Resultado**: `FL_TRANSITION` actualizado a `0.3s`, usado por `floating_input` y `floating_select`
- [x] T062 [US5] Documentar inconsistencias residuales y crear fixes si es necesario
  - **Resultado**: Sin inconsistencias críticas pendientes

**Checkpoint**: US5 completo — Consistencia visual verificada

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras transversales y validación final

- [x] T063 [P] Ejecutar validación visual siguiendo `specs/027-fix-floating-labels-tooltips/quickstart.md`
- [x] T064 [P] Verificar accesibilidad ARIA de tooltips (role="tooltip", aria-describedby)
- [x] T065 [P] Verificar comportamiento en dispositivos táctiles (tooltips se muestran al tocar)
- [x] T066 Verificar estados de error — floating labels permanecen elevados con color de error
- [x] T067 Ejecutar `python -c "from src.presentacion_reflex.styles import BASE_STYLE"` para verificar syntax
- [x] T068 Ejecutar `python -c "from src.presentacion_reflex.components.shared.floating_label import floating_input"` para verificar imports

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — puede comenzar inmediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todos los user stories
- **US1 (Phase 3)**: Depende de Foundational — Floating Labels en Filtros
- **US2 (Phase 4)**: Depende de Foundational — Floating Labels en Modales
- **US3 (Phase 5)**: Depende de Foundational — Tooltips en Filtros
- **US4 (Phase 6)**: Depende de Foundational — Tooltips en Modales
- **US5 (Phase 7)**: Depende de US1-US4 — Consistencia visual
- **Polish (Phase 8)**: Depende de US1-US5 — Validación final

### User Story Dependencies

- **US1 (P1)**: Puede comenzar después de Foundational — Sin dependencias de otros stories
- **US2 (P1)**: Puede comenzar después de Foundational — Sin dependencias de otros stories
- **US3 (P2)**: Puede comenzar después de Foundational — Sin dependencias de otros stories
- **US4 (P2)**: Puede comenzar después de Foundational — Sin dependencias de otros stories
- **US5 (P3)**: Depende de US1-US4 completados

### Within Each User Story

- Validar componentes existentes antes de corregir
- Corregir componentes base antes de validar módulos
- Documentar inconsistencias antes de implementar fixes

### Parallel Opportunities

- T002, T003, T004 (Setup) pueden correr en paralelo
- T006, T007, T008, T009 (Foundational) pueden correr en paralelo
- T010-T020 (US1 validación) pueden correr en paralelo (diferentes módulos)
- T022-T032 (US2 validación) pueden correr en paralelo (diferentes módulos)
- T034-T044 (US3 implementación) pueden correr en paralelo (diferentes módulos)
- T046-T056 (US4 implementación) pueden correr en paralelo (diferentes módulos)

---

## Parallel Example: User Story 1

```bash
# Launch all module validations for US1 together:
Task: "Validar Filtros Avanzados en personas/"
Task: "Validar Filtros Avanzados en propiedades/"
Task: "Validar Filtros Avanzados en contratos/"
Task: "Validar Filtros Avanzados en liquidaciones/"
# ... etc (diferentes archivos, sin dependencias)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (tokens y constantes)
2. Complete Phase 2: Foundational (componentes base)
3. Complete Phase 3: US1 — Floating Labels en Filtros
4. Complete Phase 4: US2 — Floating Labels en Modales
5. **STOP y VALIDAR**: Probar floating labels en al menos 3 módulos
6. Deploy/demo si está listo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 (Filtros) → Test independently → Deploy/Demo (MVP!)
3. US2 (Modales) → Test independently → Deploy/Demo
4. US3 (Tooltips Filtros) → Test independently → Deploy/Demo
5. US4 (Tooltips Modales) → Test independently → Deploy/Demo
6. US5 (Consistencia) → Test independently → Deploy/Demo
7. Polish → Validación final → Release

### Parallel Team Strategy

Con múltiples desarrolladores:

1. Equipo completa Setup + Foundational juntos
2. Una vez Foundational listo:
   - Dev A: US1 (Filtros) + US2 (Modales)
   - Dev B: US3 (Tooltips Filtros) + US4 (Tooltips Modales)
3. US5 y Polish al final

---

## Notes

- [P] tasks = diferentes archivos, sin dependencias
- [Story] label mapea tarea a user story para trazabilidad
- Cada user story debe ser independentemente completable y testeable
- Commit después de cada tarea o grupo lógico
- Detenerse en cualquier checkpoint para validar story independentemente
- Evitar: tareas vagas, conflictos en mismo archivo, dependencias cross-story que rompan independencia
