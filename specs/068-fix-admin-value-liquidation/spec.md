# Feature Specification: fix-admin-value-liquidation

**Feature Branch**: `[###-feature-name]`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa profundo y exhaustivo sobre el módulo de Liquidación de Propietarios, con un nivel Senior Experto de Élite, enfocado específicamente en validar la correcta captura y persistencia del valor de administración asociado a cada propiedad.
El cliente reporta que, al actualizar en el módulo de Propiedades el valor correspondiente a la administración, dicho cambio no se está reflejando correctamente en la Liquidación de Propietarios..."

## Context *(mandatory)*
El cliente reporta que al actualizar el valor de administración en una Propiedad, este cambio no se refleja en las Liquidaciones de Propietarios que están "En Proceso" ni se recalcula el total a pagar, generando inconsistencias financieras.

## Clarifications
### Session 2026-09-02
- Q: Concurrencia de Edición: ¿Qué pasa si un usuario actualiza la propiedad mientras otro guarda la liquidación en UI? → A: Último en escribir gana (El guardado de la liquidación prevalece).
- Q: Notificación de actualización en cascada -> A: Mostrar notificación tipo toast indicando el éxito y el número de liquidaciones actualizadas automáticamente.
- Q: Trazabilidad y Auditoría de Cambios -> A: Actualizar los campos de auditoría de cada liquidación afectada y registrar el cambio en cascada.
- Q: Valor 0 como override manual vs. valor por defecto -> A: Tratar el 0 como un valor manual explícito válido que no debe ser sobrescrito en cascada ni en la UI, a menos que el original fuera 0.
- Q: Múltiples Liquidaciones "En Proceso": ¿Actualizar todas o solo la del periodo actual? → A: Actualizar SOLO la liquidación del periodo/mes actual (las anteriores mantienen el valor antiguo).
- Q: Definición de "Periodo Actual": ¿Mes calendario o ciclo de facturación? → A: El ciclo de facturación activo (Usar la regla de negocio centralizada).
- Q: Fórmula de Recálculo → A: NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS (Estándar contable básico).
- Q: Condiciones de Rollback Transaccional → A: Strict Rollback (Cualquier error aborta ambas actualizaciones para proteger la integridad financiera).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Actualización de Administración Reflejada en Liquidaciones en Proceso (Priority: P1)

Como usuario administrador o financiero, quiero que al actualizar el "Valor de Administración" de una propiedad, este nuevo valor se refleje automáticamente en cualquier liquidación de propietario que se encuentre en estado "En Proceso" para esa misma propiedad, para garantizar que los cálculos de NETO A PAGAR sean precisos y evitar descuentos incorrectos al propietario.

**Why this priority**: Es el core del reporte del cliente. Garantiza la consistencia e integridad financiera entre el módulo de Propiedades y las Liquidaciones mensuales que aún no se han aprobado ni pagado.

**Independent Test**: Se puede probar independientemente actualizando el valor de administración en la vista de Propiedades y luego verificando que la liquidación correspondiente en estado "En Proceso" se haya recalculado correctamente con el nuevo valor en la vista de Liquidaciones.

**Acceptance Scenarios**:

1. **Given** una propiedad con un valor de administración de $100,000 y una liquidación asociada en estado "En Proceso", **When** el usuario cambia el valor de administración a $120,000 en el módulo de Propiedades, **Then** la liquidación "En Proceso" se actualiza automáticamente, su rubro de gastos de administración cambia a $120,000 y el "Neto a Pagar" se recalcula restando este nuevo valor.
2. **Given** una propiedad con una liquidación en estado "Aprobada" o "Pagada", **When** el usuario cambia el valor de administración en la propiedad, **Then** las liquidaciones aprobadas/pagadas permanecen inmutables con su valor original, preservando la historia financiera.
3. **Given** una liquidación "En Proceso" en la que el usuario editó manualmente el rubro de administración a un valor diferente al de la propiedad (override manual), **When** el valor de la propiedad se actualiza, **Then** el sistema respeta y mantiene el valor manual en la liquidación (no lo sobrescribe), protegiendo el ajuste intencional realizado para ese mes específico. Solo se sobrescribe automáticamente si la liquidación conservaba el mismo valor base anterior de la propiedad.

---

### User Story 2 - Precisión en la creación y edición de nuevas Liquidaciones (Priority: P2)

Como asesor financiero, quiero que al generar o editar una liquidación, la interfaz y el sistema backend consulten y utilicen de forma confiable la fuente oficial del valor de administración, para no propagar datos desactualizados en el momento de la confirmación.

**Why this priority**: Previene que la UI inyecte valores stale (caducos) durante la edición manual de las liquidaciones, garantizando que el origen de la verdad sea siempre la Propiedad.

**Independent Test**: Se puede probar editando una liquidación en la UI para asegurar que muestra el valor correcto actual.

**Acceptance Scenarios**:

1. **Given** una liquidación "En Proceso", **When** el usuario abre el modal de edición, **Then** el formulario precarga el valor de administración actual, que debe corresponder al valor vigente de la propiedad y no a un valor en caché.

### Edge Cases

- What happens when el valor de administración se actualiza a 0 o vacío? El sistema debe propagar este valor (0) y eliminar el cobro de la liquidación en proceso (a menos que haya un override manual).
- **Valor 0 como Override:** Si una liquidación tiene el campo `gastos_administracion` en 0 y el valor original de la propiedad era > 0, se considera un override manual legítimo. Este valor 0 NO debe ser sobrescrito por la interfaz (UI) ni por la actualización en cascada.
- **Concurrencia (Ediciones Simultáneas):** En caso de que un usuario guarde una liquidación mientras otro usuario actualiza la propiedad en background, se aplicará el patrón "Último en escribir gana" (*Last Write Wins*). El guardado explícito de la liquidación prevalecerá como un override manual.
- **Manejo de Errores y Rollback:** El proceso aplica *Strict Rollback*. Si ocurre cualquier falla técnica (restricción de base de datos, pérdida de conexión, error de cómputo) al actualizar las liquidaciones en cascada, la actualización de la propiedad MUST abortarse y revertirse enteramente, informando del error al usuario. No se permiten commits parciales.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST propagar cualquier cambio en el "Valor de Administración" de una Propiedad a la Liquidación de Propietario asociada que se encuentre en estado "En Proceso" y que corresponda al periodo/mes actual (definido como el ciclo de facturación activo del sistema, no necesariamente el mes calendario). Liquidaciones "En Proceso" de periodos anteriores no se modifican.
- **FR-002**: El sistema MUST recalcular los totales y el `NETO_A_PAGAR` de las liquidaciones afectadas (fórmula explícita: `NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS`, donde `TOTAL_EGRESOS` incorpora el nuevo valor).
- **FR-003**: El sistema MUST NO modificar el valor de administración en liquidaciones cuyo estado sea "Aprobada", "Pagada" o "Cancelada", garantizando la inmutabilidad de los registros históricos.
- **FR-004**: La interfaz de edición de Liquidaciones MUST precargar los datos asegurando que el valor mostrado al abrir el modal coincide con el valor persistido tras la sincronización, evitando inconsistencias visuales.
- **FR-005**: Todo el proceso de actualización (Propiedad + Propagación a Liquidaciones) MUST ejecutarse de manera atómica (dentro de una transacción de base de datos) para asegurar la integridad referencial.
- **FR-006**: El sistema MUST mostrar una notificación (tipo toast) en la interfaz informando al usuario la cantidad exacta de liquidaciones "En Proceso" que fueron actualizadas automáticamente.
- **FR-007**: El sistema MUST actualizar los metadatos de auditoría (`updated_at`, `updated_by`) de cada liquidación modificada durante la cascada, garantizando la trazabilidad financiera del origen del cambio.

### Key Entities *(include if feature involves data)*

- **Propiedad**: Entidad fuente (Master). Campo `valor_administracion`.
- **Liquidacion**: Entidad dependiente. Campo `gastos_administracion` y cálculo de `neto_a_pagar`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las actualizaciones del valor de administración en una propiedad se reflejan instantáneamente en sus liquidaciones "En Proceso".
- **SC-002**: 0% de regresiones financieras o modificaciones no deseadas en liquidaciones con estado distinto a "En Proceso".
- **SC-003**: El Neto a Pagar de las liquidaciones actualizadas refleja matemáticamente el nuevo descuento de administración.

## Assumptions

- Las liquidaciones obtienen su estado inicial (borrador) al momento de generarse, copiando los datos de la Propiedad en ese instante.
- Los estados que cierran financieramente una liquidación ("Aprobada", "Pagada", "Cancelada") son terminales para efectos de propagación en cascada.
