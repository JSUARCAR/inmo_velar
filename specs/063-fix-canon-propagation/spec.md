# Feature Specification: Corrección de Propagación de Canon en Renovaciones

**Feature Branch**: `063-fix-canon-propagation`

**Created**: 2026-07-22

**Status**: Draft

**Scope**: Esta corrección aplica ÚNICAMENTE a los módulos de **Liquidación de Propietarios** y **Recaudos**. Los módulos de Mandatos y Propiedades ya propagan el canon correctamente durante la renovación (verificado en auditoría 062).

**Input**: User description: "Identifico que el Contrato de Arrendamiento con ID: 80 tiene actualmente un canon de arrendamiento de $893.350, cuya renovación fue aplicada durante el período de julio de 2026. Sin embargo, evidencio que esta actualización no se está reflejando correctamente en los módulos dependientes. Tanto la Liquidación de Propietarios como el Recaudo asociados a la propiedad vinculada al Contrato de Arrendamiento ID: 80 no se vieron afectados por la actualización realizada, por lo que continúan utilizando valores que no corresponden al canon vigente definido en el contrato. Se requiere validar el flujo completo de propagación de datos entre los módulos de Contratos, Liquidaciones de Propietarios y Recaudos, con el fin de identificar la causa raíz de la inconsistencia y garantizar que las actualizaciones de canon derivadas de una renovación contractual se reflejen correctamente a partir de su fecha efectiva de vigencia, sin afectar la información histórica generada en períodos anteriores."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Propagación Automática de Canon en Renovación (Priority: P1)

Cuando un contrato de arrendamiento se renueva con un nuevo canon, el sistema debe actualizar automáticamente el canon en los módulos de Liquidación de Propietarios y Recaudos asociados a ese contrato, asegurando que los registros futuros utilicen el nuevo valor while preservando la integridad de los registros históricos.

**Why this priority**: Esta es la funcionalidad core que garantiza la consistencia financiera entre módulos. Sin ella, los valores de liquidaciones y recaudos quedan desactualizados, generando errores en la gestión financiera del sistema.

**Independent Test**: Puede probarse completamente ejecutando una renovación de contrato con un nuevo canon y verificando que las liquidaciones y recaudos futuros generados después de la renovación utilizan el nuevo canon, mientras que los registros anteriores permanecen intactos.

**Acceptance Scenarios**:

1. **Given** un contrato con canon $1.000.000 vigente, **When** se renueva el contrato con canon $1.051.000, **Then** las liquidaciones futuras generadas para ese contrato deben utilizar el canon de $1.051.000.
2. **Given** un contrato con canon $1.000.000 vigente, **When** se renueva el contrato con canon $1.051.000, **Then** los recaudos futuros asociados a ese contrato deben reflejar el canon de $1.051.000.
3. **Given** un contrato con liquidaciones históricas generadas con canon $1.000.000, **When** se renueva el contrato con canon $1.051.000, **Then** las liquidaciones históricas deben permanecer sin modificaciones con el valor original de $1.000.000.
4. **Given** un contrato con recaudos históricos generados con canon $1.000.000, **When** se renueva el contrato con canon $1.051.000, **Then** los recaudos históricos deben permanecer sin modificaciones con el valor original de $1.000.000.

---

### User Story 2 - Verificación de Integridad Post-Renovación (Priority: P2)

El sistema debe提供 una capacidad de verificación que permita validar que la propagación del canon se realizó correctamente en todos los módulos dependientes después de una renovación, identificando cualquier inconsistencia entre el canon del contrato y los valores en liquidaciones y recaudos.

**Why this priority**: Esta funcionalidad permite detectar y diagnosticar problemas de sincronización de forma proactiva, asegurando que las inconsistencias sean identificadas y corregidas antes de que impacten en la operación financiera.

**Independent Test**: Puede probarse ejecutando el script de auditoría existente (062-audit-renewal-propagation) y verificando que detecta correctamente las inconsistencias entre contratos, liquidaciones y recaudos.

**Acceptance Scenarios**:

1. **Given** un contrato con renovación aplicada, **When** se ejecuta la verificación de integridad, **Then** el sistema debe reportar si el canon en liquidaciones y recaudos coincide con el canon vigente del contrato.
2. **Given** un contrato con inconsistencias entre canon de contrato y liquidaciones, **When** se ejecuta la verificación de integridad, **Then** el sistema debe identificar y reportar las inconsistencias encontradas con severidad y detalles del registro afectado.
3. **Given** un contrato con inconsistencias entre canon de contrato y recaudos, **When** se ejecuta la verificación de integridad, **Then** el sistema debe identificar y reportar las inconsistencias encontradas con severidad y detalles del registro afectado.

---

### User Story 3 - Corrección Manual de Canon en Registros Futuros (Priority: P3)

Cuando se detecta una inconsistencia entre el canon de un contrato y sus liquidaciones o recaudos futuros, el sistema debe provide una mecánica para corregir automáticamente los valores en los registros futuros sin modificar los históricos.

**Why this priority**: Esta funcionalidad permite la remediación de inconsistencias existentes sin necesidad de intervención manual directa en la base de datos, reduciendo el riesgo de errores humanos.

**Independent Test**: Puede probarse ejecutando una corrección sobre un conjunto de registros futuros y verificando que solo los registros futuros son actualizados mientras los históricos permanecen intactos.

**Acceptance Scenarios**:

1. **Given** un contrato con liquidaciones futuras que tienen un canon desactualizado, **When** se ejecuta la corrección de propagación, **Then** las liquidaciones futuras deben actualizarse con el canon vigente del contrato.
2. **Given** un contrato con recaudos futuros que tienen un canon desactualizado, **When** se ejecuta la corrección de propagación, **Then** los recaudos futuros deben actualizarse con el canon vigente del contrato.
3. **Given** un contrato con registros históricos y futuros, **When** se ejecuta la corrección de propagación, **Then** solo los registros futuros deben ser modificados, preservando la integridad de los registros históricos.

---

### Edge Cases

- ¿Qué sucede cuando un contrato tiene múltiples renovaciones en el mismo mes? El sistema debe procesar solo la última renovación del período.
- ¿Cómo maneja el sistema cuando una liquidación o recaudo futuro ya fue generado con el canon correcto pero el contrato se renueva nuevamente? El sistema debe actualizar los valores existentes con el nuevo canon.
- ¿Qué sucede cuando un contrato tiene liquidaciones o recaudos en diferentes estados (pendiente, pagado, anulado)? El sistema solo debe actualizar registros en estado pendiente.
- ¿Cómo maneja el sistema cuando la fecha de renovación del contrato es anterior a la fecha de generación de una liquidación o recaudo? El sistema debe utilizar el canon vigente en la fecha de generación del registro.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST detectar automáticamente cuando un contrato de arrendamiento es renovado con un nuevo canon.
- **FR-002**: El sistema MUST identificar todos los módulos dependientes que requieren actualización del canon (Liquidación de Propietarios y Recaudos).
- **FR-003**: El sistema MUST actualizar el campo `canon_bruto` en los registros futuros de Liquidación de Propietarios asociados al contrato renovado.
- **FR-004**: El sistema MUST actualizar el campo `valor_total` en los registros futuros de Recaudo asociados al contrato renovado.
- **FR-005**: El sistema MUST preservar la integridad de los registros históricos de Liquidación de Propietarios (no modificar registros de períodos anteriores a la renovación).
- **FR-006**: El sistema MUST preservar la integridad de los registros históricos de Recaudo (no modificar registros de períodos anteriores a la renovación).
- **FR-007**: El sistema MUST definir un "registro futuro" como aquel cuyo campo `fecha_generacion` es posterior a la fecha de renovación del contrato, y solo estos registros deben ser actualizados.
- **FR-008**: El sistema MUST proporcionar un mecanismo de verificación que permita validar la integridad de la propagación del canon entre contratos, liquidaciones y recaudos.
- **FR-009**: El sistema MUST registrar todas las actualizaciones realizadas en un log de auditoría para trazabilidad.
- **FR-010**: El sistema MUST ejecutar la corrección de múltiples registros en una transacción atómica con rollback completo si falla alguna operación para garantizar la consistencia.

### Key Entities

- **Contrato de Arrendamiento**: Representa el contrato entre propietario y arrendatario. Contiene el canon de arrendamiento vigente, fechas de inicio y fin, y estado del contrato.
- **Renovación de Contrato**: Representa la actualización de un contrato existente con nuevo canon y fechas de vigencia. Contiene el canon anterior, canon nuevo, fecha de renovación y fecha de vigencia.
- **Liquidación de Propietarios**: Representa la liquidación financiera periódica para un propietario. Contiene el canon bruto, período de liquidación, estado y fecha de generación.
- **Recaudo**: Representa el registro de pago o cobro asociado a un contrato. Contiene el valor total, fecha de pago, estado y concepto.
- **Propiedad**: Representa la inmueble asociada al contrato. Contiene el canon de arrendamiento estimado que debe sincronizarse con el contrato.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Después de ejecutar una renovación de contrato, el 100% de las liquidaciones futuras generadas deben utilizar el canon vigente del contrato.
- **SC-002**: Después de ejecutar una renovación de contrato, el 100% de los recaudos futuros generados deben utilizar el canon vigente del contrato.
- **SC-003**: El 100% de los registros históricos de liquidaciones y recaudos deben permanecer sin modificaciones después de una renovación.
- **SC-004**: La verificación de integridad debe completarse en menos de 30 segundos para un contrato con hasta 100 registros asociados.
- **SC-005**: El sistema debe ser capaz de corregir hasta 500 registros futuros en una sola operación sin errores de transacción.
- **SC-006**: El script de auditoría debe detectar el 100% de las inconsistencias entre contratos, liquidaciones y recaudos.

## Assumptions

- La fecha de renovación del contrato se utiliza como la fecha efectiva de vigencia del nuevo canon.
- Los registros futuros son aquellos generados después de la fecha de renovación del contrato.
- El sistema actualmente solo propaga el canon a Mandatos y Propiedades durante la renovación, no a Liquidaciones ni Recaudos.
- La estructura de tablas de Liquidaciones y Recaudos permite la actualización del campo de canon sin afectar la integridad referencial.
- El script de auditoría existente (062-audit-renewal-propagation) proporciona la base para la verificación de integridad.
- El sistema utiliza PostgreSQL como base de datos y psycopg2 como driver de conexión.
- Los campos de fecha en Liquidaciones y Recaudos son de tipo texto con formato ISO 8601.

## Clarifications

### Session 2026-07-22

- Q: ¿Cuál es el alcance exacto de esta corrección? → A: Solo Liquidaciones y Recaudos (Mandatos/Propiedades excluidos)
- Q: ¿Qué campos específicos de la tabla LIQUIDACIONES deben actualizarse con el nuevo canon? → A: Solo `canon_bruto`
- Q: ¿Qué campo de la tabla RECAUDOS debe actualizarse con el nuevo canon del contrato? → A: `valor_total`
- Q: ¿Qué estrategia de recuperación debe aplicarse si la propagación falla? → A: Rollback completo (revertir todos los cambios de la transacción)
- Q: ¿Cómo se define un "registro futuro" para determinar qué registros actualizar? → A: Registros con `fecha_generacion` > fecha_renovacion del contrato
