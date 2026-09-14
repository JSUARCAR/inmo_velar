# Coherencia y Calidad de Requisitos Checklist: renovacion-contratos-debug

**Purpose**: Validar la calidad de los requisitos (completitud, claridad, consistencia, trazabilidad y cobertura) entre `spec.md`, `plan.md`, `tasks.md` y `quickstart.md` antes de la implementación (Unit Tests for English).
**Created**: 2026-09-13
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 ¿Está garantizada la población de TODOS los campos obligatorios de la entidad `RenovacionContrato` (FR-001) con tareas explícitas en ambos flujos (arrendamiento y mandato)? [Completeness, Spec §FR-001, tasks T004/T005]
- [x] CHK002 ¿La regeneración/actualización del documento PDF post-renovación está documentada como requisito (FR-004) y trazada a tareas de implementación y verificación? [Gap, Spec §FR-004, §SC-004]
- [x] CHK003 ¿La validación de rangos de fechas (fecha_fin > fecha_inicio, prevención de inconsistencias) está especificada como requisito y reflejada en tareas o escenarios? [Gap, Spec §FR-005]
- [x] CHK004 ¿La actualización de `canon_arrendamiento_estimado` en la propiedad asociada (FR-010) está trazada a tareas para renovación de arrendamiento Y de mandato? [Gap, Spec §FR-010]
- [x] CHK005 ¿Los requisitos especifican el comportamiento de invalidación de caché post-commit (FR-012) en términos de no-bloqueo y tolerancia a data obsoleta? [Completeness, Spec §FR-012]

## Requirement Clarity

- [x] CHK006 ¿El cálculo de `fecha_inicio_renovacion` está definido de forma inequívoca y NO contradictoria entre spec.md (§FR-001+1 día), tasks.md (T004/T005) y quickstart.md (E5: 2027-01-01)? [Conflict, Spec §FR-001, tasks T004/T005, quickstart §E5]
- [x] CHK007 ¿La regla de "valor IPC vigente" (FR-002) especifica su fuente, definición de vigencia, y representación (decimal) sin ambigüedad? [Clarity, Spec §FR-002]
- [x] CHK008 ¿La condición temporal de propagación (`>= date_trunc('month', fecha_renovacion)`) está redactada de forma idéntica y comprensible para `LIQUIDACIONES.canon_bruto` y `RECAUDOS.valor_total`? [Clarity/Consistency, Spec §FR-002]
- [x] CHK009 ¿El criterio "mandato activo más reciente (mayor `id_contrato_m`)" está definido sin ambigüedad y de forma consistente en spec, plan y tasks? [Clarity, Spec §FR-009]
- [x] CHK010 ¿El término "documento PDF asociado" (US1-S3) tiene criterios de verificación de contenido o queda explícitamente fuera de alcance? [Clarity, Spec §User Story 1-S3]

## Requirement Consistency

- [x] CHK011 ¿El cast seguro `NULLIF(campo,'')::date >= date_trunc('month', ...)` se exige de forma consistente en las 6 queries Q1–Q6 sin excepciones ni redacciones divergentes? [Consistency, Spec §FR-007]
- [x] CHK012 ¿La rama del feature está declarada de forma coherente en spec.md (L3), plan.md (L3) y tasks.md (L185) sin contradicción con el entorno real? [Consistency, spec.md:3, plan.md:3, tasks.md:185]
- [x] CHK013 ¿La regla de auditoría "solo filas realmente modificadas" es idéntica entre FR-002, los edge cases (spec L81-84) y los escenarios E10/E11 del quickstart? [Consistency, Spec §FR-002, §Edge Cases, quickstart §E10/E11]
- [x] CHK014 ¿La atomicidad está definida con la misma semántica en el bullet de clarificación (L26), SC-001 (L114) y el escenario E11 (rollback total + reintento idempotente)? [Consistency, Spec §SC-001, quickstart §E11]
- [x] CHK015 ¿La clasificación del test de concurrencia es coherente (supuesto CHK032) y NO se afirma como parte de SC-001 en ningún artefacto? [Consistency, plan.md Summary, Spec §SC-001, Assumptions L131]

## Acceptance Criteria Quality

- [x] CHK016 ¿Los criterios de aceptación de US1, US2 y US3 son verificables objetivamente y se reflejan en escenarios E1–E12 del quickstart? [Acceptance Criteria, Spec §User Stories, quickstart.md]
- [x] CHK017 ¿SC-001 enumera sus 7 casos de manera no ambigua y estos corresponden 1:1 con escenarios del quickstart? [Acceptance Criteria, Spec §SC-001]
- [x] CHK018 ¿SC-003 define "regresión cero" con un conjunto de tests concreto y un criterio de verde objetivo (0 fallos)? [Acceptance Criteria, Spec §SC-003]
- [x] CHK019 ¿SC-004 (PDF correcto) define QUÉ datos deben reflejarse y cómo verificarlos, o se declara medible de otro modo? [Gap, Spec §SC-004]

## Scenario Coverage

- [x] CHK020 ¿El flujo de recuperación (fallo inducido en cualquier paso → sin estado parcial → reintento sin duplicados) está especificado como requisito, no solo como expectativa de test? [Coverage, Spec §SC-001]
- [x] CHK021 ¿Están especificados los escenarios "sin mandato activo" y "múltiples mandatos activos" como requisitos de comportamiento (FR-009) y como casos de prueba puros? [Coverage, Spec §FR-009]
- [x] CHK022 ¿El escenario "sin recaudos/liquidaciones futuras" especifica el resultado (propagación no-op, sin auditoría) de forma explícita en requisitos? [Coverage, Spec §Edge Cases L81]
- [x] CHK023 ¿Están cubiertos los flujos alternos de renovación con historial previo (FR-006) como requisito y como story US2 independiente? [Coverage, Spec §FR-006, §User Story 2]

## Edge Case Coverage

- [x] CHK024 ¿Los bordes de fechas (28-Feb bisiesto → 29-Feb, 31-Dic → 01-Ene, 31-Ene → 28/29-Feb, 30-Nov → 31-Dic) están especificados en requisitos y en quickstart §E5? [Edge Case, Spec Assumptions L127, quickstart §E5]
- [x] CHK025 ¿El edge case de fechas vacías `""` en `fecha_pago`/`fecha_generacion` está especificado como requisito (FR-007) y su manejo (NULLIF→NULL) documentado? [Edge Case, Spec §FR-007, §Edge Cases L83]
- [x] CHK026 ¿El incremento 0% (canon_nuevo == canon_anterior) tiene definido explícitamente el comportamiento de auditoría (ningún insert) en requisitos? [Edge Case, Spec §Edge Cases L82]

## Non-Functional Requirements

- [x] CHK027 ¿Los gates de calidad de la constitución §5 (check_syntax.py, mypy, ruff, black, render Reflex, cobertura dominio 100% / aplicación >90%) están reflejados como requisitos de validación en tasks o plan? [Gap, Constitution §5, tasks T021]
- [x] CHK028 ¿El performance/tuning de la propagación queda explícitamente fuera de alcance (sin metas de latencia) evitando ambigüedad sobre NFR de rendimiento? [Non-Functional, Spec Assumptions L128]

## Dependencies & Assumptions

- [x] CHK029 ¿La dependencia de la tabla PostgreSQL `IDEMPOTENCY_KEYS` (FR-011, CHK031) está documentada como requisito de despliegue en el spec? [Assumption, Spec Assumptions L130]
- [x] CHK030 ¿La dependencia de `CalculadoraContratos.sumar_meses()` como único punto de verdad para fechas está documentada y su comportamiento de bordes es un requisito? [Dependency, Spec Assumptions L127]
- [x] CHK031 ¿El prerequisito de que `RENOVACIONES_CONTRATOS.FECHA_INICIO_RENOVACION TEXT NOT NULL` existe en producción se declara como validación previa a implementar? [Assumption, Spec Assumptions L126]
- [x] CHK032 ¿El supuesto de transacción única sin deadlocks está documentado como "a validar con test de concurrencia" (criterio de release), no como verdad asumida? [Assumption, Spec Assumptions L131]
