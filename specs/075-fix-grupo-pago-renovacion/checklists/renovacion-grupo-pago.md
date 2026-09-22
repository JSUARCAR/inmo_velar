# Requirements Quality Checklist: Renovación, grupo de pago e integridad transaccional (Feature 075)

**Purpose**: Validar la calidad, claridad, completitud y consistencia de los requisitos de la feature 075 (grupo de pago correcto y atómico en la renovación de contratos) como gate formal de release.
**Created**: 2026-09-21
**Feature**: [spec.md](../spec.md)

**Note**: Este checklist es una prueba unitaria de los requisitos (no de la implementación). Cada ítem evalúa lo escrito en spec.md; ninguna tarea se marca por comportamiento del sistema.

## Integridad Transaccional (Atomicidad, Rollback, Idempotencia)

- [x] CHK001 ¿Los requisitos exigen que la actualización del grupo de pago ocurra en la misma transacción que los demás cambios de la renovación? [Completeness, Spec §FR-004, §FR-006]
- [x] CHK002 ¿El alcance del rollback enumera de forma completa las entidades afectadas (contrato, grupo, mandato, propiedad, historial, liquidaciones, recaudos)? [Completeness, Spec §FR-008, §US3]
- [x] CHK003 ¿Se especifica el resultado observable ante un fallo (mensaje/estado de la operación) o solo se exige "rollback completo"? [Clarity, Spec §FR-008]
- [x] CHK004 ¿La idempotencia está cuantificada: qué se considera intento duplicado, en qué ventana temporal y con qué resultado esperado? [Clarity, Spec §US3-2, §FR-008]
- [x] CHK005 ¿Los requisitos cubren concurrencia (dos intentos simultáneos) y su resultado determinístico? [Coverage, Spec §US3-3]
- [x] CHK006 ¿"Sin estados parciales" es medible y se define cómo comprobarlo (p. ej. comparación antes/después de todos los campos afectados)? [Measurability, Spec §SC-003]
- [x] CHK007 ¿Se define el comportamiento si la invalidación de caché falla tras el commit, sin revertir la transacción confirmada? [Edge Case, Spec §FR-012]
- [x] CHK008 ¿Los requisitos distinguen con precisión "misma transacción" de "misma operación lógica" para evitar interpretaciones divergentes en implementación? [Ambiguity, Spec §FR-004]

## Reglas de Negocio del Grupo y Día de Pago

- [x] CHK009 ¿La fecha base para determinar grupo/día de pago está definida sin ambigüedad y distingue renovados de no renovados? [Clarity, Spec §FR-001, §Clarifications]
- [x] CHK010 ¿Se especifica cuál renovación se usa cuando existen múltiples (la más reciente) y cómo se identifica? [Clarity, Spec §FR-001, §US2-4]
- [x] CHK011 ¿La regla de tramos V2 está enunciada con límites completos (28-7, 8-17, 18-27) sin huecos ni solapes? [Completeness, Spec §FR-002, §FR-003]
- [x] CHK012 ¿Está documentada la diferencia intencional entre mandato (día 10/20/30) y arrendamiento (día exacto) y su consistencia con el grupo asignado? [Consistency, Spec §FR-002, §FR-003]
- [x] CHK013 ¿Los requisitos definen la regla para contratos sin renovaciones (fecha base = inicio original)? [Completeness, Spec §FR-001]
- [x] CHK014 ¿La sincronización arriendo↔mandato especifica qué campos se alinean y con qué valores tras renovar? [Clarity, Spec §FR-005]
- [x] CHK015 ¿Se define el resultado esperado del grupo cuando un arrendamiento no tiene mandato activo asociado? [Edge Case, Spec §Edge Cases]
- [x] CHK016 ¿Se define el resultado cuando el nuevo período cae en el mismo tramo (el grupo se mantiene y nunca queda en cero)? [Coverage, Spec §US1-2, §FR-007]
- [x] CHK017 ¿Los requisitos prohíben explícitamente persistir 0 o vacío cuando la regla produce un grupo válido? [Clarity, Spec §FR-007]
- [x] CHK018 ¿La definición de "fecha efectiva del período vigente" es única y consistente en todos los FR y escenarios? [Consistency, Spec §FR-001, §US2-4]
- [x] CHK019 ¿Se define el grupo esperado en bordes de mes/año (31-dic→01-ene, 28-feb→29-feb) sin ambigüedad de cálculo? [Edge Case, Spec §Edge Cases]
- [x] CHK020 ¿Se especifica si la regla aplica igual a mandatos y arrendamientos y en qué difiere exactamente cada uno? [Consistency, Spec §Clarifications, §FR-001]

## Cobertura de Regresión y Módulos Dependientes

- [x] CHK021 ¿Están enumerados todos los módulos dependientes del grupo con expectativa de no-regresión por cada uno? [Completeness, Spec §FR-011]
- [x] CHK022 ¿"Cero regresiones" es medible (suites, criterio de verde, línea base declarada)? [Measurability, Spec §SC-004]
- [x] CHK023 ¿Se define el efecto esperado en los filtros por ciclo operativo y día de pago tras la corrección? [Coverage, Spec §FR-011]
- [x] CHK024 ¿Los requisitos preservan explícitamente los comportamientos existentes (cálculo de fechas, IPC, propagación de canon, idempotencia)? [Consistency, Spec §FR-012]
- [x] CHK025 ¿La no-modificación de historia financiera cerrada está definida como límite de alcance verificable? [Boundary, Spec §FR-010, §Assumptions]
- [x] CHK026 ¿Existe un criterio de estabilidad temporal posterior (ventana sin nuevos reportes) cuantificado? [Measurability, Spec §SC-006]

## Escenarios, Bordes y Ambigüedades Residuales

- [x] CHK027 ¿Todos los escenarios de aceptación son verificables de forma independiente con datos y pasos declarados? [Acceptance Criteria, Spec §US1-4]
- [x] CHK028 ¿Los criterios de éxito son medibles sin conocer la implementación y sin dependencias tecnológicas? [Measurability, Spec §SC-001..SC-006]
- [x] CHK029 ¿Términos como "correcto", "íntegro" y "determinístico" tienen criterio verificable asociado? [Ambiguity, Spec §SC-001]
- [x] CHK030 ¿Las suposiciones (PostgreSQL único, solo contratos activos, sin cambios de esquema) están validadas y no contradicen ningún requisito? [Assumption, Spec §Assumptions]
- [x] CHK031 ¿Se define el tratamiento de contratos finalizados/cancelados y cómo se garantiza su inmutabilidad? [Coverage, Spec §FR-010]
- [x] CHK032 ¿El escenario de recuperación para contratos activos con grupo/día corrupto o en cero está definido? [Recovery, Spec §Edge Cases]
- [x] CHK033 ¿Se define la evidencia mínima antes/después que acompaña cada corrección de grupo para trazabilidad? [Traceability, Spec §SC-002]
- [x] CHK034 ¿Los FR con MUST son atómicos (una sola obligación verificable cada uno) o mezclan varias obligaciones? [Clarity, Spec §FR-004, §FR-005, §FR-010]
- [x] CHK035 ¿Las renovaciones consecutivas y su efecto sobre fechas/grupo/canon están cubiertos como escenario explícito? [Coverage, Spec §Edge Cases, §FR-012]
- [x] CHK036 ¿El alcance excluye explícitamente el cambio de la regla de negocio y el recálculo histórico, evitando scope creep? [Boundary, Spec §Assumptions]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Items are numbered sequentially for easy reference
- Traceabilidad: 32/36 ítems (89%) referencian secciones del spec o marcadores de calidad.
- Fuera de foco por decisión del usuario en esta corrida: dominio de "Auditoría y datos TEST" (ver `requirements.md` para la validación de completitud general del spec).
- Evaluación 2026-09-21 (tras clarificación adicional): 36/36 ítems pasan contra el spec actualizado. Las 3 brechas detectadas (resultado observable ante fallo, cuantificación de idempotencia, fallo de invalidación de caché) se resolvieron en FR-008, FR-012, Edge Cases, Assumptions y Clarifications; los bordes de fecha ahora declaran grupo/día esperados. CHK034: cada obligación de FR-005/FR-010 se mantiene verificable de forma independiente; la granularidad fina se resolverá al desglosar tareas en el plan.
