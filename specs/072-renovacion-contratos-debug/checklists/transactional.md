# Transactional Robustness Checklist: renovacion-contratos-debug

**Purpose**: Validar la calidad, claridad y completitud de los requisitos de robustez transaccional de la renovación de contratos: atomicidad, ROLLBACK, idempotencia, cast seguro de fechas vacías y consistencia de la invalidación de caché de canon.
**Created**: 2026-09-13
**Feature**: [spec.md](../spec.md) | [research.md](../research.md) | [plan.md](../plan.md)

**Depth**: Release Gate | **Audience**: QA / Release | **Focus**: Transaccionalidad atómica, idempotencia (FR-011), cast seguro de fechas (FR-007), invalidación de caché (excluye tuning de performance)

## Completitud de Requisitos

- [x] CHK001 - ¿Define el spec el límite exacto de la transacción atómica de la renovación (qué operaciones se incluyen: actualizar contrato, insertar log `RENOVACIONES_CONTRATOS`, sincronizar mandato, actualizar propiedad, propagar líquidos, registrar auditoría)? [Completeness, Spec §FR-003]
- [x] CHK002 - ¿Está especificado si el INSERT en `RENOVACIONES_CONTRATOS` forma parte de la misma transacción que la propagación, o si tiene un punto de commit propio? [Completeness, Ambiguity]
- [x] CHK003 - ¿Está documentado cuáles campos de cada tabla mutan dentro de la transacción (`canon_arrendamiento`, `canon_mandato`, `fecha_fin_contrato_m`, `canon_arrendamiento_estimado`, `canon_bruto`, `valor_total`) y cuáles se actualizan fuera de ella? [Completeness, Spec §FR-002, FR-009, FR-010]
- [x] CHK004 - ¿Está definido el requisito de invalidación de la caché de canon tras un commit exitoso para que la UI refleje el nuevo canon? [Completeness, Gap]
- [x] CHK005 - ¿Está especificado el requisito de idempotencia para el flujo de mandato (`renovar_mandato`), no solo para el de arrendamiento? [Completeness, Spec §FR-011]
- [x] CHK006 - ¿Está documentado que TODAS las comparaciones de fecha dentro de la transacción usan cast seguro (`NULLIF(campo,'')::date`), incluidas las consultas de verificación heredadas del contrato 063? [Completeness, Spec §FR-007]

## Claridad de Requisitos

- [x] CHK007 - ¿Está definido sin ambigüedad qué sucede con las filas de fecha vacía dentro de la transacción (¿se ignoran, se excluyen o se marcan para revisión)? [Ambiguity, Spec §FR-007]
- [x] CHK008 - ¿Está cuantificado qué significa "commit exitoso" para disparar la invalidación de caché (¿éxito = commit en BD, o éxito = commit + invalidación confirmada)? [Ambiguity, Gap]
- [x] CHK009 - ¿Está claro el alcance del ROLLBACK (¿se revierte la transacción completa, o existen operaciones fuera de la transacción que permanecen aunque falle)? [Clarity, Spec §FR-003]
- [x] CHK010 - ¿Está especificada la semántica de reintento tras un ROLLBACK (¿se puede re-ejecutar el servicio y producir el mismo resultado sin efectos parciales)? [Clarity, Gap]
- [x] CHK011 - ¿Está definido el comportamiento si la invalidación de caché falla pero el commit de BD tuvo éxito (¿requisito de consistencia caché-BD, o se acepta data obsoleta temporal)? [Ambiguity, Gap]

## Consistencia de Requisitos

- [x] CHK012 - ¿Son consistentes los requisitos de transaccionalidad de FR-003 con la propagación de FR-002 (¿misma transacción única, o transacciones separadas por tabla)? [Consistency, Spec §FR-002, FR-003]
- [x] CHK013 - ¿Son consistentes los requisitos de idempotencia entre el flujo de arrendamiento y el de mandato (mismo decorador, mismas claves y misma semántica)? [Consistency, Spec §FR-011]
- [x] CHK014 - ¿Es consistente el requisito de cast seguro (`NULLIF`) con las queries de verificación heredadas de `063-fix-canon-propagation` (Q5/Q6) que aún usan `>` sin `NULLIF`? [Conflict, Spec §FR-007]
- [x] CHK015 - ¿Son consistentes los requisitos de invalidación de caché con la renovación (la caché no debe bloquear ni impedir la transacción de BD)? [Consistency, Gap]

## Cobertura de Escenarios

- [x] CHK016 - ¿Está definido el requisito para el fallo a mitad de propagación (algunas `LIQUIDACIONES`/`RECAUDOS` actualizados y luego un error): se garantiza ROLLBACK total? [Coverage, Recovery Flow]
- [x] CHK017 - ¿Está definido el requisito de comportamiento ante un doble envío de "Renovar" (doble clic, reintento de red) y su relación con la idempotencia? [Coverage, Gap]
- [x] CHK018 - ¿Está definido el requisito de recuperación cuando la transacción falla después de insertar el log de renovación pero antes de propagar el canon? [Coverage, Exception Flow]
- [x] CHK019 - ¿Están especificados los requisitos de reintentos (retry) por timeout de PostgreSQL y cómo la idempotencia evita duplicados en esos reintentos? [Coverage, Gap]
- [x] CHK020 - ¿Está definido qué ocurre con la caché de canon cuando la transacción hace ROLLBACK (¿debe permanecer intacta o invalidarse igualmente)? [Coverage, Edge Case]

## Cobertura de Casos Borde

- [x] CHK021 - ¿Está definido el requisito cuando el conjunto de filas a propagar es vacío (0 filas afectadas) y cómo se comporta la auditoría en ese caso? [Edge Case, Gap]
- [x] CHK022 - ¿Está tratado el caso en que `canon_nuevo == canon_anterior` (incremento 0% por IPC ausente o duración < 12 meses) en la propagación y la auditoría de cambios? [Edge Case, Spec §FR-002]
- [x] CHK023 - ¿Está especificado el tratamiento de la fila del propio mes de la renovación (`>= date_trunc('month', ...)`): si un recaudo/liquidación del mismo mes debe actualizarse o se excluye intencionalmente? [Clarity, Edge Case, Spec §FR-007]
- [x] CHK024 - ¿Está definido el comportamiento cuando el contrato tiene múltiples mandatos asociados (¿cuál se sincroniza: el activo, el último, o se rechaza la renovación)? [Coverage, Edge Case, Spec §FR-009]

## Criterios de Aceptación Medibles

- [x] CHK025 - ¿Están definidos criterios de aceptación que verifiquen la atomicidad (ausencia de estado parcial tras un fallo inducido), o se asume tácitamente el comportamiento transaccional? [Measurability, Spec §SC-001]
- [x] CHK026 - ¿Están especificados los umbrales de cobertura de tests para los flujos transaccionales exigidos (constitución: dominio 100%, aplicación >90%)? [Measurability, Constitution §5]
- [x] CHK027 - ¿Está definido en spec/plan qué evidencia de QA constituye el release gate (criterio de aceptación de release), o queda implícito? [Acceptance Criteria, Gap]
- [x] CHK028 - ¿Es objetivamente verificable SC-001 ("100% de intentos de renovación completados exitosamente") en términos de integridad post-rollback, o requiere un criterio adicional de no-particialidad? [Measurability, Spec §SC-001]

## Requisitos No Funcionales

- [x] CHK029 - ¿Está documentado el requisito de consistencia entre BD y caché de canon (estricta o eventual), diferenciándolo del tuning de performance que está fuera de alcance? [Completeness, Gap]
- [x] CHK030 - ¿Está declarado explícitamente que el tuning/optimización de performance queda fuera del alcance de esta feature (exclusión documentada)? [Completeness, Gap]

## Dependencias y Supuestos

- [x] CHK031 - ¿Está documentada la dependencia del decorador `@idempotent` con su almacén de respaldo para garantizar idempotencia real entre sesiones/instancias (no solo en memoria)? [Dependency, Gap]
- [x] CHK032 - ¿Está validado el supuesto de que la propagación puede ejecutarse en una única transacción PostgreSQL sin deadlocks con otros procesos concurrentes (escrituras de recaudos/liquidaciones)? [Assumption, Gap]
- [x] CHK033 - ¿Está documentada la dependencia de que `NULLIF` y `date_trunc` existen en la versión de PostgreSQL de producción (sin feature flags especiales)? [Dependency, Assumption]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Link to relevant resources or documentation
- Items are numbered sequentially for easy reference
