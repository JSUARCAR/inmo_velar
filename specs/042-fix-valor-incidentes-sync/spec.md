# Feature Specification: Fix Valor Incidentes Auto-Sync

**Feature Branch**: `[042-fix-valor-incidentes-sync]`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "Corregir la sincronización automática del campo valor_incidentes en liquidaciones. Actualmente, cuando se asocia un incidente a una liquidación, el campo valor_incidentes no se actualiza automáticamente con el total de los descuentos, permaneciendo en $0 a pesar de que la tabla de incidentes asociados muestra el registro correctamente."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sincronización Automática del Valor de Incidentes (Priority: P1)

Como usuario del sistema (administrador o asesor), quiero que cuando se asocie un incidente a una liquidación en estado "En Proceso", el campo `valor_incidentes` de la liquidación se actualice automáticamente con el total de los descuentos de todos los incidentes asociados, para que el cálculo del neto a pagar sea correcto y consistente.

**Why this priority**: Es un problema crítico que afecta la integridad financiera de las liquidaciones. Si el campo `valor_incidentes` no se sincroniza, el cálculo del neto a pagar será incorrecto, generando errores en los pagos a propietarios.

**Independent Test**: Can be fully tested by associating an incident to a liquidation and verifying that the `valor_incidentes` field is automatically updated with the total discount amount.

**Acceptance Scenarios**:

1. **Given** un usuario asocia un incidente con descuento de $75.000 a una liquidación, **When** se guarda la asociación, **Then** el campo `valor_incidentes` de la liquidación se actualiza automáticamente a $75.000.
2. **Given** un usuario asocia múltiples incidentes a una liquidación (uno de $75.000 y otro de $50.000), **When** se guardan las asociaciones, **Then** el campo `valor_incidentes` se actualiza a $125.000 (suma de todos los descuentos).
3. **Given** un usuario elimina un incidente asociado a una liquidación, **When** se elimina la asociación, **Then** el campo `valor_incidentes` se recalcula automáticamente restando el descuento eliminado.
4. **Given** una liquidación con `valor_incidentes` actualizado, **When** se abre el modal de edición, **Then** el campo "Incidentes" muestra el valor correcto sincronizado.
5. **Given** una liquidación con incidentes asociados, **When** se calcula el neto a pagar, **Then** el cálculo incluye el `valor_incidentes` correctamente.

---

### Edge Cases

- What happens when se asocia un incidente con descuento $0? El campo `valor_incidentes` no debe cambiar (mantener el valor anterior o 0 si es el primero).
- How does system handle un error al actualizar el campo `valor_incidentes`? El sistema debe revertir la asociación del incidente y mostrar un toast de error.
- What happens when hay múltiples incidentes y uno falla al asociarse? El sistema debe associar los que sean posibles y reportar los errores.
- How does system handle concurrent updates? Si dos usuarios asocian incidentes simultáneamente, el sistema debe usar transacciones para evitar condiciones de carrera.
- What happens when se desasocia un incidente? El campo `valor_incidentes` debe recalcularse automáticamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST actualizar automáticamente el campo `valor_incidentes` de una liquidación en tiempo real (en la misma transacción) cuando se asocia un nuevo incidente, sumando el `VALOR_DESCUENTO` del incidente al valor actual. Esta operación solo está permitida para liquidaciones en estado "En Proceso".
- **FR-002**: El sistema MUST recalcular el campo `valor_incidentes` en tiempo real cuando se elimina una asociación incidente-liquidación, restando el descuento eliminado. Esta operación solo está permitida para liquidaciones en estado "En Proceso".
- **FR-003**: El sistema MUST garantizar que el campo `valor_incidentes` siempre sea igual a la suma de todos los `VALOR_DESCUENTO` de los incidentes asociados en la tabla `INCIDENTE_LIQUIDACION`.
- **FR-004**: El sistema MUST usar transacciones de base de datos para asegurar la atomicidad de las operaciones de asociación/desasociación y actualización del campo `valor_incidentes`.
- **FR-005**: El sistema MUST recalcular el neto a pagar de la liquidación después de actualizar el campo `valor_incidentes`.
- **FR-006**: El sistema MUST mostrar el valor actualizado de `valor_incidentes` en el modal de edición de liquidaciones.
- **FR-007**: El sistema MUST manejar errores de sincronización mostrando un toast de notificación con un botón de "Reintentar".
- **FR-008**: El sistema MUST mantener la integridad referencial entre las tablas `LIQUIDACIONES`, `INCIDENTES` e `INCIDENTE_LIQUIDACION`.
- **FR-009**: El sistema MUST soportar la associación y desasociación de múltiples incidentes en una sola operación.
- **FR-010**: El sistema MUST preservar el valor de `valor_incidentes` existente si la asociación/desasociación resulta en un cambio neto de $0.
- **FR-011**: El sistema MUST restringir las operaciones de asociación/desasociación de incidentes a los roles de Administrador y Asesor únicamente.

### Key Entities *(include if feature involves data)*

- **Liquidación**: Registro financiero con campo `valor_incidentes` que debe mantenerse sincronizado con el total de descuentos de incidentes asociados.
- **Incidente**: Registro con campo `VALOR_DESCUENTO` que representa el monto a descontar de la liquidación.
- **Relación Liquidación-Incidente**: Tabla `INCIDENTE_LIQUIDACION` con campo `VALOR_DESCUENTO` que vincula incidentes con liquidaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las asociaciones incidente-liquidación resultan en una actualización correcta del campo `valor_incidentes`.
- **SC-002**: El campo `valor_incidentes` siempre es igual a la suma de los `VALOR_DESCUENTO` de los incidentes asociados.
- **SC-003**: El cálculo del neto a pagar incluye correctamente el `valor_incidentes` en el 100% de los casos.
- **SC-004**: No existen inconsistencias entre el valor calculado de `valor_incidentes` y el valor almacenado en la base de datos.
- **SC-005**: Las operaciones de asociación/desasociación son atómicas (no dejan el sistema en un estado inconsistente).
- **SC-006**: El usuario puede ver el valor correcto de incidentes en el modal de edición inmediatamente después de asociar/desasociar incidentes.

## Clarifications

### Session 2026-07-10

- Q: ¿El campo `valor_incidentes` debe ser editable manualmente o solo calculado automáticamente? → A: Debe ser calculado automáticamente a partir de los incidentes asociados, pero mantener la posibilidad de edición manual para casos excepcionales (con advertencia al usuario).
- Q: ¿Qué pasa si el usuario edita manualmente `valor_incidentes` y luego se asocia un nuevo incidente? → A: El sistema debe advertir al usuario que el valor será recalculado automáticamente y preguntar si desea continuar.
- Q: ¿Se debe crear un botón de "Recalcular Incidentes" para sincronizar manualmente? → A: Sí, como opción de respaldo en caso de inconsistencias.

### Session 2026-07-11

- Q: ¿La sincronización debe ser en tiempo real o batch? → A: Tiempo real - actualizar `valor_incidentes` inmediatamente en la misma transacción al asociar/desasociar incidentes.
- Q: ¿Qué roles pueden asociar/desasociar incidentes? → A: Administradores y Asesores pueden realizar esta operación.
- Q: ¿En qué estados de liquidación se permite la actualización de `valor_incidentes`? → A: Solo en estado "En Proceso" (antes de aprobar).

## Out of Scope

- Modificaciones al esquema de la base de datos.
- Cambios en la lógica de creación de incidentes o liquidaciones.
- Optimizaciones de rendimiento en consultas SQL.
- Modificaciones al flujo de aprobación de liquidaciones.

## Assumptions

- La tabla `INCIDENTE_LIQUIDACION` almacena correctamente la relación entre incidentes y liquidaciones.
- El campo `VALOR_DESCUENTO` en `INCIDENTE_LIQUIDACION` contiene el monto correcto del descuento.
- El campo `valor_incidentes` en `LIQUIDACIONES` existe y está habilitado para escritura.
- Las transacciones de PostgreSQL están habilitadas y funcionan correctamente.
- El servicio `ServicioIncidenteLiquidacion` es el encargado de manejar las operaciones de asociación/desasociación.
- El cálculo del neto a pagar ya incluye `valor_incidentes` en su fórmula (ver `liquidacion.py:122`).
