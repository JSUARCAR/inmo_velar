# Tasks: Ciclo Operativo en Módulo Recaudos

**Input**: Design documents from `/specs/045-ciclo-operativo-recaudos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No incluidos (cambio de display puro, validación manual via quickstart.md)

**Organization**: Tareas agrupadas por user story para implementación y prueba independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (diferentes archivos, sin dependencias)
- **[Story]**: User story a la que pertenece (US1, US2, US3)

---

## Phase 1: Foundational (Backend + DTO)

**Purpose**: Preparar la capa de datos y contratos para que las user stories puedan consumir el ciclo operativo.

**⚠️ CRITICAL**: Ninguna user story puede implementarse hasta que esta fase esté completa.

- [X] T001 [P] Agregar campo `ciclo_operativo: str = ""` a `RecaudoDTO` en `src/aplicacion/esquemas/recaudo.py`
- [X] T002 [P] Agregar mapeo de `ciclo_operativo` en `RecaudoMapper.map_to_dto()` en `src/aplicacion/esquemas/recaudo.py` — mapear desde `row.get("ciclo_operativo", "")`
- [X] T003 Agregar JOIN a `CONTRATOS_MANDATOS` en el query `listar_paginado` de `src/infraestructura/persistencia/repositorio_recaudo.py` — usar `INNER JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO'`
- [X] T004 Agregar `cm.GRUPO_OPERATIVO` al SELECT del query `listar_paginado` en `src/infraestructura/persistencia/repositorio_recaudo.py`
- [X] T005 Agregar mapeo `"ciclo_operativo"` al dict de salida del `listar_paginado` en `src/infraestructura/persistencia/repositorio_recaudo.py` — formatear como `f"Grupo {row['GRUPO_OPERATIVO']}" if row.get("GRUPO_OPERATIVO") else "-"`
- [X] T006 Agregar `"ciclo_operativo": "ciclo_operativo"` al `SORT_COLUMNS` en `src/infraestructura/persistencia/repositorio_recaudo.py` para permitir ordenamiento por esta columna
- [X] T007 Agregar el mismo JOIN y SELECT al query `contar_con_filtros` en `src/infraestructura/persistencia/repositorio_recaudo.py` para mantener consistencia de datos

**Checkpoint**: Backend retorna `ciclo_operativo` en la respuesta. DTO listo para consumo.

---

## Phase 2: User Story 1 - Visualización del Ciclo Operativo (Priority: P1) 🎯 MVP

**Goal**: El usuario ve la columna "Ciclo Operativo" en la tabla de Recaudos con valores correctos ("Grupo N").

**Independent Test**: Abrir módulo Recaudos → verificar columna aparece después de "Pago Contrato" → verificar propiedad BRR BOSQUES DE PINARES MZ 4 CS 144 PI 1 muestra "Grupo 1".

### Implementation for User Story 1

- [X] T008 [US1] Agregar columna "Ciclo Operativo" al header de la tabla en `src/presentacion_reflex/pages/recaudos.py` — insertar después de "Pago Contrato" usando `header_cell_sortable("Ciclo Operativo", "ciclo_operativo")`
- [X] T009 [US1] Agregar celda de renderizado para `ciclo_operativo` en el body de la tabla en `src/presentacion_reflex/pages/recaudos.py` — renderizar como texto normal, con color gris muted si el valor es "-"

**Checkpoint**: User Story 1 funcional. La columna es visible y muestra valores correctos.

---

## Phase 3: User Story 2 - Comportamiento ante recaudos sin liquidación (Priority: P2)

**Goal**: Recaudos sin liquidación asociada muestran "-" sin errores visuales ni funcionales.

**Independent Test**: Identificar recaudo sin liquidación → verificar columna muestra "-" → verificar tabla opera normalmente (ordenar, filtrar, paginar).

### Implementation for User Story 2

- [X] T010 [US2] Verificar que el formato `"-"` para valores nulos/0 está correctamente implementado en el mapeo del repositorio (T005) y que la UI renderiza "-" con estilo gris en `src/presentacion_reflex/pages/recaudos.py`
- [X] T011 [US2] Verificar que el ordenamiento de la columna maneja correctamente el valor "-" (se ordena al final tanto en asc como en desc) en el repositorio `src/infraestructura/persistencia/repositorio_recaudo.py`

**Checkpoint**: User Story 2 funcional. Casos edge manejados correctamente.

---

## Phase 4: User Story 3 - Consistencia del dato (Priority: P3)

**Goal**: El ciclo operativo en Recaudos es idéntico al de la Liquidación de Propietarios correspondiente.

**Independent Test**: Comparar ciclo operativo en Recaudos con el de Liquidaciones para la misma propiedad → verificar coincidencia exacta.

### Implementation for User Story 3

- [X] T012 [US3] Ejecutar caso de validación: buscar propiedad "BRR BOSQUES DE PINARES MZ 4 CS 144 PI 1" en tabla Recaudos → verificar "Grupo 1" → abrir Liquidación de Propietarios correspondiente → verificar coincidencia
- [X] T013 [US3] Validar que al menos 3 recaudos de diferentes grupos operativos muestran valores consistentes entre módulo Recaudos y módulo Liquidaciones

**Checkpoint**: Consistencia verificada entre módulos.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validación integral y verificación de regresiones.

- [X] T014 Ejecutar escenarios de validación V1-V7 del `specs/045-ciclo-operativo-recaudos/quickstart.md`
- [X] T015 Verificar que exportación de datos incluye columna "Ciclo Operativo" en `src/presentacion_reflex/pages/recaudos.py`
- [X] T016 Verificar que no hay errores en consola del navegador ni en logs del servidor
- [X] T017 Verificar tiempos de carga de la tabla de Recaudos no incrementan más de 10%

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: Sin dependencias — puede iniciar inmediatamente. **BLOQUEA** todas las user stories.
- **Phase 2 (US1)**: Depende de Phase 1 completa.
- **Phase 3 (US2)**: Depende de Phase 1 completa. Puede ejecutarse en paralelo con US1.
- **Phase 4 (US3)**: Depende de Phase 1 completa. Puede ejecutarse en paralelo con US1 y US2.
- **Phase 5 (Polish)**: Depende de todas las user stories completas.

### User Story Dependencies

- **US1 (P1)**: Depende de Phase 1. Sin dependencias de otras stories.
- **US2 (P2)**: Depende de Phase 1. Puede ejecutarse en paralelo con US1.
- **US3 (P3)**: Depende de Phase 1. Puede ejecutarse en paralelo con US1 y US2.

### Within Each Phase

- En Phase 1: T001 y T002 son paralelos (diferentes partes del mismo archivo). T003-T007 son secuenciales (mismo archivo).
- En Phase 2: T008 y T009 son secuenciales (mismo archivo, header antes que body).
- En Phase 3: T010 y T011 son verificaciones, no implementación.

### Parallel Opportunities

```bash
# Phase 1 - Paralelo:
Task T001: "Agregar campo a RecaudoDTO"
Task T002: "Agregar mapeo en RecaudoMapper"
# Luego secuencial:
Task T003-T007: Modificaciones en repositorio (secuenciales)

# Phase 2+3+4 - Paralelo (si hay capacidad):
Task T008-T009: US1 - Columna UI
Task T010-T011: US2 - Verificación edge cases
Task T012-T013: US3 - Validación de consistencia
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Backend + DTO
2. Completar Phase 2: US1 - Columna visible
3. **PARAR Y VALIDAR**: Verificar columna aparece con valores correctos
4. Desplegar si está listo

### Incremental Delivery

1. Phase 1 completa → Backend retorna ciclo operativo
2. US1 → Columna visible → Validar → Desplegar (MVP!)
3. US2 → Edge cases manejados → Validar → Desplegar
4. US3 → Consistencia verificada → Validar → Desplegar

---

## Notes

- [P] tasks = diferentes archivos, sin dependencias entre sí
- [Story] label mapea cada tarea a su user story para trazabilidad
- Cada user story es independientemente completable y testeable
- Commit después de cada tarea o grupo lógico
- Verificar quickstart.md al final de cada phase
- El cambio es de display puro — no se modifica lógica de negocio ni esquemas de BD

## Phase 6: Convergence

- [X] T018 Cambiar INNER JOIN a LEFT JOIN en `listar_paginado` y `contar_con_filtros` (`repositorio_recaudo.py`) para no ocultar recaudos sin mandato activo per FR-006 (contradicts)
- [X] T019 Refinar la lógica de JOIN hacia CONTRATOS_MANDATOS para seleccionar el contrato activo más reciente dentro del periodo del recaudo, previniendo duplicados si hay múltiples contratos activos per FR-010 (partial)
