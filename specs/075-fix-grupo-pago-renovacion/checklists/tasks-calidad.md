# Task & Test-Coverage Quality Checklist: Feature 075 (gate pre-implementación)

**Purpose**: Validar como gate pre-implementación la calidad, ejecutabilidad, trazabilidad y cobertura de pruebas de `tasks.md` antes de ejecutar la implementación.
**Created**: 2026-09-21
**Feature**: [spec.md](../spec.md) | Plan: [plan.md](../plan.md) | Tareas: [tasks.md](../tasks.md)

**Note**: Prueba unitaria de las tareas y requisitos (no de la implementación). Cada ítem evalúa lo escrito en los artefactos; ninguno ejecuta ni verifica comportamiento del sistema.

## Formato y Estructura de las Tareas

- [x] CHK001 ¿Todas las tareas usan el formato `- [ ] Tnnn [P?] [US?] descripción` con archivo o comando exacto? [Completeness, tasks.md §Format]
- [x] CHK002 ¿La numeración es secuencial en orden de ejecución, sin huecos ni duplicados? [Consistency, tasks.md T001–T026]
- [x] CHK003 ¿Cada fase declara propósito, y las fases de historia declaran Goal e Independent Test? [Completeness, tasks.md §Phases]
- [x] CHK004 ¿Las etiquetas [USn] corresponden a historias del spec y solo aparecen en fases de historia (no en Setup/Foundational/Polish)? [Consistency, Spec §US1-4, tasks.md]
- [x] CHK005 ¿Las tareas [P] operan sobre archivos distintos y no dependen de tareas incompletas? [Clarity, tasks.md §Parallel Opportunities]
- [x] CHK006 ¿Cada tarea referencia una ruta de archivo o comando verificable (no descripciones vagas)? [Clarity, tasks.md]
- [x] CHK007 ¿Los checkpoints declaran un resultado verificable antes de avanzar de fase? [Measurability, tasks.md]

## Ejecutabilidad y Granularidad

- [x] CHK008 ¿Cada tarea es ejecutable sin contexto adicional (acción, archivo y criterio explícitos)? [Completeness, tasks.md]
- [x] CHK009 ¿Las tareas que tocan el mismo archivo están en secuencia (sin [P] en conflicto)? [Consistency, tasks.md T008-T009, T014-T015, T011-T018]
- [x] CHK010 ¿Las tareas grandes están divididas por responsabilidad (auditoría vs `--commit`; recálculo vs transacción)? [Clarity, tasks.md T009-T010, T014-T015]
- [x] CHK011 ¿Se declaran criterios de entrada (baseline en verde y base de pruebas) antes de tocar código? [Dependency, tasks.md T001-T002]
- [x] CHK012 ¿La fase Foundational está marcada como bloqueante y justificada por la regla única de dominio? [Completeness, tasks.md §Phase 2]
- [x] CHK013 ¿Las tareas evitan incluir commits/push no solicitados? [Boundary, tasks.md §Notes]

## Dependencias, Orden y Paralelismo

- [x] CHK014 ¿El grafo de dependencias refleja el orden real (Foundational → US1/US2 en paralelo → US3 → US4 → Polish)? [Consistency, tasks.md §Dependencies]
- [x] CHK015 ¿US2 se declara independiente de US1 tras Foundational y sus tareas no dependen de artefactos de US1? [Consistency, tasks.md §User Story Dependencies, T013-T017]
- [x] CHK016 ¿US3 depende explícitamente de la transacción de mandato (T010) y esa dependencia está trazada? [Traceability, tasks.md T018-T021]
- [x] CHK017 ¿Las oportunidades de paralelismo están ejemplificadas con tareas de archivos distintos? [Clarity, tasks.md §Parallel Example]
- [x] CHK018 ¿Existe advertencia operativa de no ejecutar `--commit` contra producción sin revisar el dry-run? [Safety, tasks.md §Notes, contracts/cli-remediacion.md]

## Cobertura de Requisitos (FR/SC)

- [x] CHK019 ¿Cada FR-001..FR-013 tiene al menos una tarea que lo implementa o verifica? [Coverage, Spec §FR-001..FR-013, tasks.md]
- [x] CHK020 ¿Cada SC-001..SC-006 tiene una tarea de verificación explícita (incluido SC-006)? [Coverage, Spec §SC-001..SC-006, tasks.md T017-T026]
- [x] CHK021 ¿Los componentes del plan (calculadora, mapeo, renovaciones, script, UI) están cubiertos por tareas? [Traceability, plan.md §Project Structure, tasks.md]
- [x] CHK022 ¿La decisión R7 (consulta masiva sin método de repositorio) está reflejada en la tarea del script? [Consistency, research.md R7, tasks.md T014]
- [x] CHK023 ¿La herencia de período del mandato (R2) está asignada a una tarea concreta de la auditoría? [Traceability, research.md R2, tasks.md T014]
- [x] CHK024 ¿La limpieza obligatoria de datos TEST está cubierta por tareas de implementación y verificación? [Completeness, Spec §FR-013, tasks.md T016, T025]

## Cobertura de Pruebas y Regresión

- [x] CHK025 ¿Las tareas exigen escribir pruebas en rojo antes de implementar (TDD declarado)? [Process, tasks.md §Tests, constitution §5]
- [x] CHK026 ¿Las pruebas unitarias cubren regla de dominio (bordes), servicios y mapeo de persistencia? [Coverage, tasks.md T003, T005, T006, T019]
- [x] CHK027 ¿Las pruebas de integración cubren persistencia, atomicidad/rollback, auditoría y limpieza? [Coverage, tasks.md T011, T013, T016, T018]
- [x] CHK028 ¿La verificación de rollback es objetiva (cero estado parcial) y exige reintento sin duplicados? [Measurability, Spec §SC-003, tasks.md T018]
- [x] CHK029 ¿La idempotencia de la remediación se verifica con una segunda corrida en 0 discrepancias? [Measurability, Spec §SC-002, tasks.md T017]
- [x] CHK030 ¿La regresión de Contratos/Liquidaciones/Recaudos tiene tarea y criterio de verde (100%)? [Coverage, Spec §SC-004, tasks.md T022]
- [x] CHK031 ¿La validación de runtime/UI (badge de grupo y filtros por ciclo/día) está cubierta por una tarea? [Coverage, Spec §FR-011, tasks.md T023]
- [x] CHK032 ¿La verificación de limpieza distingue datos TEST y exige conteos 0 en todas las tablas afectadas? [Measurability, Spec §SC-005, tasks.md T016, T025]
- [x] CHK033 ¿Se incluyen los controles de calidad pre-commit (sintaxis, tipado, lint, formato)? [Completeness, constitution §5, tasks.md T024]

## Estrategia MVP y Riesgos

- [x] CHK034 ¿El MVP está acotado a US1 con criterio de parada y validación independiente? [Clarity, tasks.md §Implementation Strategy]
- [x] CHK035 ¿La entrega incremental describe el valor de cada historia sin romper las anteriores? [Consistency, tasks.md §Incremental Delivery]
- [x] CHK036 ¿La estrategia de equipo paralelo respeta la dependencia de US3 respecto de US1? [Consistency, tasks.md §Parallel Team Strategy]
- [x] CHK037 ¿Las notas finales delimitan el alcance (sin cambios de esquema ni de historia financiera)? [Boundary, tasks.md §Notes, Spec §Assumptions]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Items are numbered sequentially for easy reference
- Traceabilidad: 37/37 ítems referencian tareas, secciones del spec/plan o marcadores de calidad.
- Complementa (no reemplaza) los gates previos: `requirements.md`, `renovacion-grupo-pago.md` y `plan-auditoria.md`.
- Evaluación 2026-09-21 (gate pre-implementación): 37/37 ítems pasan contra `tasks.md` (28 tareas), spec y plan. Brecha detectada y resuelta durante la evaluación: CHK020 (SC-006 no tenía verificación asignada) → se amplió T026 para cubrir el baseline de SC-006 y su seguimiento a 30 días. Refinamientos posteriores del análisis: T017 cualificada con filas omitidas, T024 con medición de cobertura, T027 añadida para cobertura unitaria del script y T023 con criterio de aceptación explícito.
