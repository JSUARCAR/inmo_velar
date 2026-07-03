# Feature Specification: Sincronización Incidentes y Liquidaciones

**Feature Branch**: `[005-sync-incidentes-liquidaciones]`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre la integración entre los módulos Incidentes y Liquidaciones de Propietarios, ya que durante las pruebas funcionales identifiqué una inconsistencia que está afectando la correcta sincronización de la información entre ambos módulos. Incidencia identificada: Se evidencia que el Incidente no está mostrando el Plan de Pago asociado. Como consecuencia, la información financiera derivada de dicho plan no se está propagando correctamente hacia la Liquidación de Propietario."

## Clarifications

### Session 2026-07-02

- Q: ¿Cómo debe comportarse el sistema si un plan de pago se cancela o modifica después de que una de sus cuotas ya fue incluida en una liquidación en estado borrador? → A: Mantener la liquidación pero mostrar una advertencia visual.
- Q: Una vez que una cuota del plan de pago se descuenta en una liquidación finalizada, ¿qué cambio de estado debe tener la cuota? → A: Cambiar su estado a 'Pagada/Descontada' explícitamente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización del Plan de Pago en Incidentes (Priority: P1)

Como usuario del sistema, necesito ver el plan de pago asociado a un incidente aprobado directamente en el módulo de Incidentes, para poder validar la información financiera que afectará las liquidaciones.

**Why this priority**: Es la base del problema reportado. Si no se visualiza y persiste correctamente el plan de pago en el incidente, no puede propagarse a las liquidaciones.

**Independent Test**: Can be fully tested by approving an incident quotation and checking if the payment plan is generated and displayed on the incident's UI.

**Acceptance Scenarios**:

1. **Given** un incidente con una cotización aprobada, **When** se genera el plan de pago, **Then** el plan de pago debe asociarse al incidente y persistir en la base de datos.
2. **Given** un incidente con plan de pago existente, **When** el usuario visualiza el incidente en la UI, **Then** los detalles del plan de pago deben mostrarse correctamente.

---

### User Story 2 - Propagación de Cuotas a Liquidación de Propietario (Priority: P1)

Como gestor financiero, necesito que el valor de la cuota del plan de pago de un incidente se refleje automáticamente como un descuento (campo Incidentes) en la Liquidación del Propietario correspondiente, para asegurar cálculos exactos en los pagos.

**Why this priority**: Impacta directamente el dinero y los cálculos de las liquidaciones de propietarios.

**Independent Test**: Can be fully tested by generating a liquidation for a property that has an active incident with a payment plan, and verifying the discount value.

**Acceptance Scenarios**:

1. **Given** una liquidación en proceso para una propiedad, **When** existe un incidente con cuotas de plan de pago activas, **Then** el sistema debe recuperar correctamente dichas cuotas de la base de datos.
2. **Given** una cuota recuperada, **When** se calcula la liquidación, **Then** el valor de la cuota debe verse reflejado en el campo "Incidentes" y deducirse del total neto a pagar al propietario.

### Edge Cases

- What happens when el propietario tiene múltiples incidentes activos con planes de pago concurrentes? (El sistema debe sumar todas las cuotas aplicables).
- How does system handle un plan de pago que se cancela o modifica después de haber sido asociado a una liquidación en borrador? → El sistema mantendrá la liquidación intacta, pero mostrará una advertencia visual al usuario indicando que el plan de pago subyacente ha cambiado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generar y persistir un Plan de Pago (con sus respectivas cuotas) una vez se aprueba una cotización de un Incidente.
- **FR-002**: System MUST mantener una clave foránea o relación directa entre la entidad `Incidente` y la entidad `PlanPago`.
- **FR-003**: System MUST exponer los datos del Plan de Pago en la consulta de lectura del Incidente (Backend/Servicios) y presentarlos en la UI de Reflex.
- **FR-004**: System MUST recuperar todas las cuotas de incidentes pendientes asociadas a la propiedad/contrato durante la generación de una Liquidación de Propietario.
- **FR-005**: System MUST reflejar la sumatoria de las cuotas aplicables en el campo "Incidentes" de la Liquidación y afectar el neto a pagar.
- **FR-006**: System MUST cambiar explícitamente el estado de la cuota a "Pagada/Descontada" una vez que la liquidación a la que se asoció sea finalizada.

### Key Entities *(include if feature involves data)*

- **Incidente**: Representa el problema reportado. Debe tener o referenciar a un Plan de Pago.
- **PlanPago**: Representa el acuerdo financiero derivado de la cotización aprobada de un incidente.
- **Cuota**: Cada uno de los pagos fraccionados o únicos de un PlanPago.
- **LiquidacionPropietario**: Documento financiero donde se deben descontar las cuotas de incidentes correspondientes al periodo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los incidentes con cotización aprobada muestran su plan de pago en la interfaz de usuario.
- **SC-002**: 100% de las cuotas de incidentes correspondientes al mes se descuentan automáticamente en la Liquidación del Propietario en el campo "Incidentes".
- **SC-003**: Las consultas a base de datos de Incidentes retornan los datos del plan de pago en menos de 500ms.

## Assumptions

- Se asume que el esquema de base de datos actual ya cuenta con las tablas de Plan de Pago y Cuotas, y el problema radica en la relación, persistencia al aprobar, o las consultas SQL.
- Se asume que la interfaz de Reflex ya tiene componentes visuales para mostrar esta información o se pueden reutilizar los existentes.
