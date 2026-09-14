# Data Integrity Checklist: renovacion-contratos-debug

**Purpose**: Validar la calidad, completitud y claridad de los requisitos relacionados con la integridad de datos PostgreSQL, el casting de fechas y la propagación de canon durante la renovación de contratos.
**Created**: 2026-09-13
**Feature**: [spec.md](../spec.md) | [research.md](../research.md) | [plan.md](../plan.md)

**Depth**: Standard | **Audience**: Reviewer (PR) | **Focus**: PostgreSQL data integrity, date casting safety, renewal log completeness

## Completitud de Requisitos

- [x] CHK001 - ¿Están documentados todos los campos de la entidad `RenovacionContrato` que deben ser poblados durante la renovación, incluyendo `fecha_inicio_renovacion`? [Completeness, Gap]
- [x] CHK002 - ¿Están especificados los requisitos de propagación de canon a `LIQUIDACIONES` para registros futuros? [Completeness, Spec §FR-002]
- [x] CHK003 - ¿Están especificados los requisitos de propagación de canon a `RECAUDOS` para registros futuros? [Completeness, Spec §FR-002]
- [x] CHK004 - ¿Están documentados los requisitos de auditoría (`AUDITORIA_PROPAGACION_CANON`) para registrar los cambios de canon propagados? [Completeness, Gap]
- [x] CHK005 - ¿Están especificados los requisitos de sincronización del mandato activo asociado cuando se renueva un arrendamiento? [Completeness, Gap]
- [x] CHK006 - ¿Están documentados los requisitos para actualizar el `canon_arrendamiento_estimado` en la propiedad tras la renovación? [Completeness, Gap]

## Claridad de Requisitos

- [x] CHK007 - ¿Está cuantificado qué constituye un "registro futuro" para `LIQUIDACIONES` (criterio exacto de fecha: `fecha_generacion::date >= date_trunc(...)`)? [Clarity, Spec §FR-007]
- [x] CHK008 - ¿Está cuantificado qué constituye un "registro futuro" para `RECAUDOS` (criterio exacto de fecha: `fecha_pago::date >= date_trunc(...)`)? [Clarity, Spec §FR-007]
- [x] CHK009 - ¿Está definido de forma inequívoca cómo se calcula `fecha_inicio_renovacion` (¿fecha fin original + 1 día, o fecha fin original misma)? [Ambiguity, Gap]
- [x] CHK010 - ¿Está especificado el comportamiento cuando `duracion_contrato_a < 12 meses` respecto al incremento IPC (actualmente: no aplica IPC)? [Clarity, Spec §FR-002]
- [x] CHK011 - ¿Está definido qué significa "condiciones económicas actualizadas" más allá del canon (comisión, IVA, neto a pagar)? [Ambiguity, Spec §FR-002]

## Consistencia de Requisitos

- [x] CHK012 - ¿Son consistentes los requisitos de renovación entre arrendamientos (`_ejecutar_renovacion_arrendamiento`) y mandatos (`renovar_mandato`) respecto al cálculo de `fecha_inicio_renovacion`? [Consistency]
- [x] CHK013 - ¿Son consistentes los requisitos de la entidad `RenovacionContrato` (schema `NOT NULL` para `FECHA_INICIO_RENOVACION`) con la lógica de negocio que actualmente deja el campo vacío? [Conflict, Spec §FR-001]
- [x] CHK014 - ¿Son consistentes los requisitos de tipo de dato entre SQLite (`TEXT`) y PostgreSQL (`TEXT` pero con casting `::date`) para campos de fecha en `RECAUDOS` y `LIQUIDACIONES`? [Consistency, Gap]

## Cobertura de Escenarios

- [x] CHK015 - ¿Están definidos los requisitos para el caso en que `fecha_pago` en `RECAUDOS` sea una cadena vacía `""` al momento de ejecutar la propagación? [Coverage, Edge Case]
- [x] CHK016 - ¿Están definidos los requisitos para el caso en que `fecha_generacion` en `LIQUIDACIONES` sea `NULL` o vacía al momento de ejecutar la propagación? [Coverage, Edge Case]
- [x] CHK017 - ¿Están definidos los requisitos para renovar un contrato que NO tiene recaudos ni liquidaciones futuras asociadas? [Coverage, Edge Case]
- [x] CHK018 - ¿Están definidos los requisitos para el caso en que no exista un mandato activo asociado a la propiedad del arrendamiento renovado? [Coverage, Edge Case]
- [x] CHK019 - ¿Están definidos los requisitos para el caso en que no exista un valor IPC registrado en la base de datos al momento de calcular el incremento? [Coverage, Edge Case]
- [x] CHK020 - ¿Están especificados los requisitos de rollback si la propagación de canon a recaudos/liquidaciones falla parcialmente después de actualizar el contrato? [Coverage, Recovery Flow]

## Criterios de Aceptación Medibles

- [x] CHK021 - ¿Se puede verificar objetivamente el criterio SC-001 ("100% de intentos de renovación se completan exitosamente")? ¿Está definido el set de prueba mínimo? [Measurability, Spec §SC-001]
- [x] CHK022 - ¿Se puede verificar objetivamente el criterio SC-003 ("cero regresiones en Liquidaciones, Recaudos y Creación/Edición")? ¿Están definidos los tests de regresión? [Measurability, Spec §SC-003]
- [x] CHK023 - ¿Son verificables los criterios de "precisión matemática" del cálculo de fechas en SC-002? ¿Están definidos los casos de borde (28-Feb, 31-Dic, año bisiesto)? [Measurability, Spec §SC-002]

## Requisitos No Funcionales

- [x] CHK024 - ¿Están documentados los requisitos de consistencia transaccional para la operación completa de renovación (contrato + renovación log + propagación canon + sincronización mandato)? [Completeness, Spec §FR-003]
- [x] CHK025 - ¿Están especificados los requisitos de manejo de errores específicos de dominio (excepciones tipadas vs. `ValueError` genérico) durante la renovación? [Gap, Constitution §2.2]
- [x] CHK026 - ¿Están documentados los requisitos de idempotencia para evitar renovaciones duplicadas accidentales (decorador `@idempotent` existente)? [Gap]

## Dependencias y Supuestos

- [x] CHK027 - ¿Está documentada la dependencia con la feature `063-fix-canon-propagation` que introdujo la propagación de canon y el bug de casting? [Dependency]
- [x] CHK028 - ¿Está documentado el supuesto de que PostgreSQL es el único motor de base de datos en producción (eliminando la necesidad de compatibilidad SQLite)? [Assumption, Spec §Assumptions]
- [x] CHK029 - ¿Está validado el supuesto de que el schema `RENOVACIONES_CONTRATOS` ya existe en producción con la columna `FECHA_INICIO_RENOVACION TEXT NOT NULL`? [Assumption]
- [x] CHK030 - ¿Está documentada la dependencia con `CalculadoraContratos.sumar_meses()` y su comportamiento en fechas de borde? [Dependency, Spec §FR-005]

## Notes

- Check items off as completed: `[x]`
- Add comments or findings inline
- Link to relevant resources or documentation
- Items are numbered sequentially for easy reference
