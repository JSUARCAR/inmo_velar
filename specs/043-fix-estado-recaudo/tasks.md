# Tasks: Corrección del Estado Recaudo

**Input**: Design documents from `/specs/043-fix-estado-recaudo/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: No se solicitan tests automatizados. Validación manual según quickstart.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar el entorno de desarrollo

- [x] T001 Crear rama `bugfix/043-fix-estado-recaudo` desde `develop`
- [ ] T002 Verificar que la aplicación compile sin errores (`reflex run --env dev`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entender el estado actual antes de modificar

**⚠️ CRITICAL**: No se puede corregir sin entender el comportamiento actual

- [x] T003 Ejecutar query de diagnóstico para identificar recaudos con estado inconsistente en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
- [x] T004 Documentar el comportamiento actual de la subquery en `listar_paginado()` (líneas 1640-1657)
- [x] T005 Documentar el comportamiento actual de `_obtener_estados_recaudo_por_grupos()` (líneas 1126-1186)

**Checkpoint**: Entendimiento completo del comportamiento actual

---

## Phase 3: User Story 1 - Corrección del Estado Recaudo (Priority: P1) 🎯 MVP

**Goal**: Garantizar que la columna Estado Recaudo muestre exclusivamente el estado del recaudo vigente (más reciente, no reversado) para el mismo período

**Independent Test**: Verificar los 6 escenarios de quickstart.md

### Implementation for User Story 1

- [x] T006 [P] [US1] Corregir subquery en `listar_paginado()` para filtrar recaudos reversados y ordenar por fecha en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
- [x] T007 [P] [US1] Corregir batch query en `_obtener_estados_recaudo_por_grupos()` para filtrar recaudos reversados y ordenar por fecha en `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`
- [x] T008 [US1] Verificar consistencia en `obtener_estado_pago_actual()` en `src/infraestructura/persistencia/repositorio_recaudo.py`
- [x] T009 [US1] Ejecutar validación CP-001: Liquidación sin Recaudo
- [x] T010 [US1] Ejecutar validación CP-002: Liquidación con Recaudo Reversado Único
- [x] T011 [US1] Ejecutar validación CP-003: Recaudo Reversado + Nuevo Válido
- [x] T012 [US1] Ejecutar validación CP-004: Múltiples Recaudos Válidos
- [x] T013 [US1] Ejecutar validación CP-005: Recaudo de Período Diferente
- [x] T014 [US1] Ejecutar validación CP-006: Consistencia UI vs PostgreSQL

**Checkpoint**: Estado Recaudo funciona correctamente para todos los escenarios

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Verificación final y documentación

- [ ] T015 Ejecutar pruebas de regresión en módulos relacionados (Recaudos, Contratos)
- [ ] T016 Verificar que no hay errores en consola del navegador
- [ ] T017 Verificar que no hay errores en logs de la aplicación
- [ ] T018 Documentar cambios realizados en commit con mensaje `fix(liquidaciones): corregir estado recaudo para mostrar solo recaudo vigente`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS user story
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1 completion

### Within User Story 1

- T006 y T007 son independientes (diferentes métodos) → pueden ejecutarse en paralelo
- T008 es independiente de T006/T007 → puede ejecutarse en paralelo
- T009-T014 son validaciones secuenciales (dependen de la implementación)

### Parallel Opportunities

- T006 + T007 + T008: Correcciones en archivos diferentes → paralelo
- T009-T014: Validaciones pueden ejecutarse en cualquier orden después de la implementación

---

## Parallel Example: User Story 1

```bash
# Ejecutar correcciones en paralelo (diferentes archivos/métodos):
Task: "Corregir subquery en listar_paginado() en repositorio_liquidacion_postgres.py"
Task: "Corregir batch query en _obtener_estados_recaudo_por_grupos() en repositorio_liquidacion_postgres.py"
Task: "Verificar consistencia en obtener_estado_pago_actual() en repositorio_recaudo.py"

# Ejecutar validaciones (secuencial o paralelo):
Task: "Ejecutar validación CP-001 a CP-006"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (crear rama, verificar compilación)
2. Complete Phase 2: Foundational (entender comportamiento actual)
3. Complete Phase 3: User Story 1 (corregir queries + validar)
4. **STOP y VALIDAR**: Probar los 6 escenarios en la UI
5. Commit y push si todo está correcto

### Cambios Esperados

**Archivo principal**: `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

**Cambio en subquery** (listar_paginado y _obtener_estados_recaudo_por_grupos):
```sql
-- ANTES:
(SELECT rrec_sub.ESTADO_RECAUDO
 FROM RECAUDOS rrec_sub
 JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
 JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
 WHERE ca_sub.ID_PROPIEDAD = p.ID_PROPIEDAD
   AND rconc_sub.PERIODO = l.PERIODO
 LIMIT 1) AS ESTADO_RECAUDO

-- DESPUÉS:
(SELECT rrec_sub.ESTADO_RECAUDO
 FROM RECAUDOS rrec_sub
 JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
 JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
 WHERE ca_sub.ID_PROPIEDAD = p.ID_PROPIEDAD
   AND rconc_sub.PERIODO = l.PERIODO
   AND rrec_sub.ESTADO_RECAUDO != 'Reversado'
 ORDER BY rrec_sub.FECHA_PAGO DESC
 LIMIT 1) AS ESTADO_RECAUDO
```

---

## Notes

- [P] tasks = diferentes archivos/métodos, sin dependencias entre sí
- [US1] = User Story 1: Corrección del Estado Recaudo
- Cada validación (T009-T014) corresponde a un escenario de quickstart.md
- No se requieren tests automatizados (validación manual)
- Commit después de cada fase completa
- Detenerse en el checkpoint de User Story 1 para validar antes de continuar
