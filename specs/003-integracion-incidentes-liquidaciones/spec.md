# Feature Specification: Integración Incidentes y Liquidaciones de Propietarios

**Feature Branch**: `003-integracion-incidentes-liquidaciones`

**Created**: 2026-06-30

**Status**: Draft

**Input**: User description: "Implementar un flujo funcional que permita gestionar el pago de los incidentes mediante descuentos aplicados a una o varias Liquidaciones de Propietarios, garantizando trazabilidad completa entre incidentes, cotizaciones aprobadas, descuentos aplicados al canon de mandato y estado de pago."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Definir Plan de Pago del Incidente (Priority: P1)

Como Asesor o Administrador, necesito definir cómo se descontará el valor de la reparación de un incidente aprobado del canon de mandato del propietario, seleccionando entre diferentes modalidades de pago (1, 2, 3 o más cánones, o un número personalizado).

**Why this priority**: Es la funcionalidad fundamental que inicia el flujo de integración. Sin ella no existe la conexión entre incidentes y liquidaciones.

**Independent Test**: Puede ser probada al abrir el modal de un incidente en estado "Aprobado" con cotización aprobada, seleccionar una modalidad de pago y verificar que se genera el plan de cuotas correctamente.

**Acceptance Scenarios**:

1. **Given** un incidente en estado "Aprobado" con cotización aprobada, **When** el usuario (Asesor o Administrador) abre el modal del incidente, **Then** se muestra la sección "Plan de Pago del Incidente" con las opciones de modalidad de pago.

2. **Given** la sección de plan de pago visible, **When** el usuario selecciona "Descontar en 2 cánones de mandato", **Then** el sistema divide el valor aprobado de la cotización entre 2 y muestra el resumen del plan con 2 cuotas de $250.000 cada una (para un valor de $500.000).

3. **Given** el plan de pago calculado, **When** el usuario confirma el plan, **Then** el sistema almacena el plan y crea las cuotas pendientes de asociación a liquidaciones.

4. **Given** un incidente con plan de pago ya definido, **When** el usuario intenta modificar el plan, **Then** el sistema permite la modificación únicamente si no existen liquidaciones asociadas a ninguna cuota.

5. **Given** un incidente sin plan de pago, **When** el usuario visualiza el incidente, **Then** no se muestra información de estado de pago ni cuotas.

6. **Given** un Operador visualiza un incidente, **When** el usuario revisa la información, **Then** solo tiene permisos de lectura (visualización) pero NO puede definir ni modificar planes de pago.

---

### User Story 2 - Asociar Incidentes a Liquidación (Priority: P1)

Como Administrador, necesito asociar uno o varios incidentes con cuotas pendientes a una liquidación de propietario, para que los descuentos se reflejen en el estado de cuenta del propietario.

**Why this priority**: Es esencial para conectar los incidentes con las liquidaciones y permitir el flujo financiero integrado.

**Independent Test**: Puede ser probada al abrir el modal de una liquidación en estado "Aprobada" o "En Proceso", hacer clic en "Seleccionar Incidentes", elegir uno o varios incidentes y verificar que el campo "Valor de Incidentes" se actualiza correctamente.

**Acceptance Scenarios**:

1. **Given** una liquidación en estado "Aprobada" o "En Proceso", **When** el Administrador hace clic en el botón "Seleccionar Incidentes", **Then** se abre un modal que muestra únicamente incidentes cuyo estado de pago sea diferente de "Pagado".

2. **Given** el modal de selección de incidentes abierto, **When** el Administrador selecciona uno o varios incidentes mediante checkboxes, **Then** el sistema muestra la sumatoria de los descuentos seleccionados.

3. **Given** incidentes seleccionados, **When** el Administrador confirma la selección, **Then** se asocian los incidentes a la liquidación, se actualiza automáticamente el campo "Valor de Incidentes" de la liquidación, y se registra la relación entre la liquidación y cada incidente.

4. **Given** un incidente ya asociado a una liquidación, **When** se intenta asociar el mismo incidente nuevamente, **Then** el sistema rechaza la operación con un mensaje indicando que el incidente ya está asociado.

5. **Given** múltiples cuotas de un incidente, **When** se asocian a diferentes liquidaciones, **Then** cada cuota queda asociada a una liquidación distinta y el sistema mantiene la trazabilidad de cada descuento.

6. **Given** un Asesor intenta acceder al botón "Seleccionar Incidentes", **When** el usuario visualiza la liquidación, **Then** el botón NO está visible (solo Administradores pueden asociar incidentes a liquidaciones).

---

### User Story 3 - Visualización del Estado de Pago (Priority: P1)

Como usuario (cualquier rol), necesito visualizar el estado de pago de cada incidente en la interfaz, independientemente de su estado operativo, para conocer simultáneamente el estado financiero y operativo.

**Why this priority**: Es fundamental para la trazabilidad y toma de decisiones. Sin esta visualización, el usuario no puede conocer el estado financiero del incidente.

**Independent Test**: Puede ser probada al visualizar la lista de incidentes en estados "Aprobado", "En Reparación" o "Finalizado" y verificar que se muestra el estado de pago junto al estado operativo.

**Acceptance Scenarios**:

1. **Given** un incidente en estado "Aprobado", "En Reparación" o "Finalizado", **When** el usuario visualiza el incidente en la lista o kanban, **Then** se muestra tanto el estado operativo como el estado de pago (Pendiente, Parcialmente Pagado, Pagado).

2. **Given** un incidente con todas sus liquidaciones asociadas en estado "Pagada", **When** el sistema calcula el estado de pago, **Then** el estado se actualiza automáticamente a "Pagado".

3. **Given** un incidente con algunas liquidaciones pagadas y otras pendientes, **When** el sistema calcula el estado de pago, **Then** el estado se muestra como "Parcialmente Pagado".

4. **Given** un incidente sin liquidaciones asociadas o con todas las liquidaciones pendientes, **When** el sistema calcula el estado de pago, **Then** el estado se muestra como "Pendiente".

5. **Given** un incidente en estado "Reportado", "En Revision" o "Cotizado", **When** el usuario visualiza el incidente, **Then** NO se muestra el estado de pago (solo aplica para estados Aprobado, En Reparación, Finalizado).

---

### User Story 4 - Actualización Automática del Estado de Pago (Priority: P2)

Como sistema, necesito actualizar automáticamente el estado de pago de los incidentes cuando una liquidación cambia a estado "Pagada", para garantizar la consistencia financiera sin intervención manual.

**Why this priority**: Es esencial para mantener la integridad de la información y evitar inconsistencias entre liquidaciones e incidentes.

**Independent Test**: Puede ser probada al marcar como "Pagada" una liquidación que tiene incidentes asociados y verificar que el estado de pago de los incidentes se actualiza correctamente.

**Acceptance Scenarios**:

1. **Given** un incidente asociado a dos liquidaciones, **When** la primera liquidación cambia a estado "Pagada", **Then** el estado de pago del incidente se actualiza a "Parcialmente Pagado".

2. **Given** un incidente con estado "Parcialmente Pagado", **When** la segunda liquidación también cambia a estado "Pagada", **Then** el estado de pago del incidente se actualiza a "Pagado".

3. **Given** un incidente asociado a una única liquidación, **When** la liquidación cambia a estado "Pagada", **Then** el estado de pago del incidente se actualiza inmediatamente a "Pagado".

4. **Given** múltiples incidentes asociados a una liquidación, **When** la liquidación cambia a estado "Pagada", **Then** el sistema recalcula el estado de pago de TODOS los incidentes asociados.

5. **Given** un incidente ya en estado "Pagado", **When** se verifica su estado, **Then** el estado se mantiene "Pagado" sin cambios adicionales.

---

### User Story 5 - Reversión de Pago con Impacto en Incidentes (Priority: P2)

Como Administrador, necesito que cuando se revierta el pago de una liquidación, el sistema actualice automáticamente el estado de pago de los incidentes asociados, manteniendo la consistencia financiera.

**Why this priority**: Es esencial para mantener la integridad cuando se corrigen errores de pago. La funcionalidad de reversión ya existe y debe integrarse con el nuevo flujo.

**Independent Test**: Puede ser probada al revertir el pago de una liquidación que tiene incidentes asociados y verificar que el estado de pago de los incidentes se recalcula correctamente.

**Acceptance Scenarios**:

1. **Given** un incidente en estado "Pagado" asociado a dos liquidaciones pagadas, **When** se revierte el pago de una liquidación, **Then** el estado de pago del incidente se actualiza a "Parcialmente Pagado".

2. **Given** un incidente en estado "Parcialmente Pagado", **When** se revierte el pago de la única liquidación pagada, **Then** el estado de pago del incidente se actualiza a "Pendiente".

3. **Given** un incidente con múltiples cuotas, **When** se revierte una liquidación, **Then** solo la cuota asociada a esa liquidación queda pendiente, las demás cuotas mantienen su estado.

---

### User Roles

| Rol | Definir Plan de Pago | Asociar Incidentes a Liquidación | Visualizar Estado de Pago | Revertir Pago |
|-----|---------------------|----------------------------------|--------------------------|---------------|
| Administrador | Sí | Sí | Sí | Sí |
| Asesor | Sí | No | Sí | No |
| Operador | No (solo lectura) | No | Sí | No |

---

### Edge Cases

- ¿Qué sucede si se intenta definir un plan de pago para un incidente que no tiene cotización aprobada? → El sistema debe rechazar la operación con un mensaje claro indicando que se requiere una cotización aprobada.

- ¿Qué sucede si se intenta asociar un incidente cuya cuota ya fue asociada a otra liquidación? → El sistema debe rechazar la operación con un mensaje indicando que la cuota ya está asociada.

- ¿Qué sucede si se cancela una liquidación que tiene incidentes asociados? → El sistema debe recalcular el estado de pago de todos los incidentes afectados, cambiándolos a "Pendiente" si era la única liquidación pagada.

- ¿Qué sucede si se intenta modificar el plan de pago de un incidente que ya tiene liquidaciones asociadas? → El sistema debe bloquear la modificación con un mensaje indicando que existen liquidaciones asociadas.

- ¿Qué sucede si la conexión a la base de datos se pierde durante una operación de asociación? → La transacción debe hacer rollback automáticamente y mantener el estado original.

- ¿Qué sucede si se intenta asociar un incidente en estado "Cancelado"? → El sistema debe rechazar la operación, ya que solo se deben asociar incidentes con estado de pago diferente de "Pagado".

- ¿Qué sucede si el valor de la liquidación es menor al valor de la cuota del incidente? → El sistema debe permitir la asociación pero mostrar una advertencia sobre el impacto en el neto a pagar.

- ¿Qué sucede si dos usuarios intentan modificar el mismo incidente simultáneamente? → El sistema implementa bloqueo pesimista: cuando un usuario abre un incidente para definir plan de pago, otros usuarios ven "En edición por [usuario]" y no pueden modificar hasta que se cierre. Al cerrar el modal, se libera el bloqueo automáticamente.

---

### Out of Scope

Las siguientes funcionalidades están EXPLÍCITAMENTE excluidas de esta feature:

- Notificaciones automáticas al propietario sobre descuentos aplicados
- Generación de reportes PDF específicos de liquidación con incidentes (los PDFs existentes se mantienen sin cambios)
- Integración con sistemas contables externos
- Gestión de recaudos de inquilinos (funcionalidad independiente)
- Generación automática de asientos contables o pólizas contables
- Webhooks o eventos API para integración con sistemas externos

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow defining a payment plan for incidents in "Aprobado" state with approved quotation.
- **FR-002**: System MUST support payment plan modalities: 1 mandate, 2 mandates, 3+ mandates, or custom number of installments.
- **FR-003**: System MUST automatically divide the approved quotation value by the number of installments defined.
- **FR-004**: System MUST display a payment plan summary before confirmation.
- **FR-005**: System MUST allow payment plan modification only when no liquidations are associated.
- **FR-006**: System MUST associate one or multiple incident installments to a owner liquidation.
- **FR-007**: System MUST display only incidents with payment status different from "Pagado" in the selection modal.
- **FR-008**: System MUST support multiple incident selection via checkboxes.
- **FR-009**: System MUST automatically calculate the sum of all selected discounts.
- **FR-010**: System MUST automatically update the "Valor de Incidentes" field of the liquidation.
- **FR-011**: System MUST prevent associating the same installment to multiple liquidations.
- **FR-012**: System MUST automatically calculate payment status based on associated liquidation states.
- **FR-013**: System MUST display payment status (Pendiente, Parcialmente Pagado, Pagado) alongside operational status.
- **FR-014**: System MUST automatically update payment status when liquidation state changes to "Pagada".
- **FR-015**: System MUST recalculate payment status for all associated incidents when a liquidation payment is reversed.
- **FR-016**: System MUST implement all operations as atomic transactions with rollback support.
- **FR-017**: System MUST guarantee idempotency for all association operations.
- **FR-018**: System MUST maintain complete audit trail for all payment plan and association operations.
- **FR-019**: System MUST enforce that all business rules are implemented in the backend layer.
- **FR-020**: System MUST ensure that UI displays only data from the database through backend services.
- **FR-021**: System MUST implement pessimistic locking for concurrent edit prevention - when a user opens an incident for payment plan editing, other users see "En edición por [usuario]" and cannot modify until the modal is closed.
- **FR-022**: System MUST support up to 15 concurrent users, ~200 liquidations per period, and ~500 active incidents without performance degradation.
- **FR-023**: System MUST capture user IP address and session ID in audit trail for all payment plan and association operations.
- **FR-024**: System MUST require mandatory justification text for all association and payment plan modification operations in the audit trail.

### Key Entities

- **Incidente**: Represents a maintenance incident. Key states: Reportado, En Revision, Cotizado, Aprobado, En Reparacion, Finalizado, Cancelado. New attribute: estado_pago (Pendiente, Parcialmente Pagado, Pagado).

- **Cotizacion**: Represents a quotation for an incident. Key states: Pendiente, Aprobada, Rechazada. The approved quotation value is used for payment plan calculation.

- **Liquidacion**: Represents the monthly account statement for a property owner. Key states: En Proceso, Aprobada, Pagada, Cancelada. New field: valor_incidentes (total discounts from incidents).

- **PlanPagoIncidente**: New entity representing the payment plan for an incident. Contains: number of installments, installment value, total amount, and status. Unique constraint: one active plan per incident.

- **CuotaIncidente**: New entity representing each installment of the payment plan. Contains: installment number, value, associated liquidation, and payment status. Unique constraint: one installment per liquidation per incident.

- **IncidenteLiquidacion**: New relationship entity linking incidents to liquidations. Contains: incident ID, liquidation ID, installment number, and discount amount. Composite unique constraint: (id_incidente, id_liquidacion, numero_cuota).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can define a payment plan for an incident in under 1 minute.
- **SC-002**: Users can associate incidents to a liquidation in under 2 minutes.
- **SC-003**: 100% of payment status calculations are accurate and consistent with liquidation states.
- **SC-004**: Zero data inconsistencies between incident payment status and associated liquidation states.
- **SC-005**: All association operations are idempotent - 100% of repeated attempts are safely handled.
- **SC-006**: Transaction atomicity is maintained - zero partial associations in case of system failures.
- **SC-007**: Complete audit trail exists for 100% of payment plan and association operations.
- **SC-008**: System supports up to 15 concurrent users without degradation.
- **SC-009**: System handles ~200 liquidations per period and ~500 active incidents with response times under 3 seconds.
- **SC-010**: Pessimistic locking prevents 100% of concurrent edit conflicts.

## Assumptions

- The existing AUDITORIA_CAMBIOS table and triggers will capture all new operations automatically.
- The permission system already supports per-module action checks via `AuthState.check_action()`.
- The current user authentication system provides the `usuario_sistema` value for audit trails.
- The existing UI component library (neuro_elements) will be used for consistent styling.
- The database transaction mechanism (commit/rollback) is already properly implemented in the repository layer.
- The existing liquidation payment reversal functionality will be extended to recalculate incident payment status.
- The existing incident entity can be extended with new attributes without breaking backward compatibility.
- The system can implement pessimistic locking using database-level locks or application-level flags.

## Dependencies

- **Existing Module**: Incidentes (fully implemented with CRUD, state management, and quotation handling)
- **Existing Module**: Liquidaciones de Propietarios (fully implemented with CRUD, approval, payment, cancellation, and reversal workflows)
- **Permission System**: Module "Liquidaciones" with action "SELECCIONAR_INCIDENTES" must be registered
- **Permission System**: Module "Incidentes" with action "DEFINIR_PLAN_PAGO" must be registered
- **Audit System**: AUDITORIA_CAMBIOS table with triggers must be active
- **UI Framework**: Reflex framework with neuro_elements component library

## Technical Justification

The implementation follows the existing architecture patterns:

1. **Repository Pattern**: New repositories for PlanPagoIncidente, CuotaIncidente, and IncidenteLiquidacion following the same pattern as existing repositories.

2. **Service Layer**: Extension of ServicioIncidentes and ServicioFinanciero with new methods for payment plan management and association logic.

3. **State Management**: Extension of IncidentesState and LiquidacionesState with new event handlers for payment plan and association workflows.

4. **UI Components**: New modal components for payment plan definition and incident selection, following existing patterns.

5. **Transaction Safety**: Using existing database connection/transaction management with explicit commit/rollback.

6. **Idempotency**: Implemented via state checks and unique constraints to prevent duplicate associations.

7. **Audit Trail**: Leveraging existing AUDITORIA_CAMBIOS trigger mechanism with additional fields for IP address, session ID, and mandatory justification.

8. **Automatic State Calculation**: Payment status will be calculated using SQL queries that check the state of all associated liquidations, ensuring consistency.

9. **Concurrency Control**: Pessimistic locking via database flags or application-level state to prevent edit conflicts.

## Clarifications

### Session 2026-06-30

- Q: ¿Qué funcionalidades deben estar EXPLÍCITAMENTE excluidas de esta feature? → A: Excluir: Notificaciones automáticas al propietario, generación de reportes PDF específicos de liquidación con incidentes, integración con sistemas contables externos, gestión de recaudos de inquilinos.

- Q: ¿Qué roles del sistema deben poder ejecutar las acciones principales? → A: Administradores pueden todo; Asesores pueden definir planes de pago pero NO asociar incidentes a liquidaciones; Operadores solo visualizan.

- Q: ¿Cómo debe manejar el sistema las ediciones concurrentes? → A: Bloqueo pesimista: cuando un usuario abre un incidente para definir plan de pago, otros usuarios ven "En edición por [usuario]" y no pueden modificar hasta que se cierre.

- Q: ¿Cuál es el volumen máximo esperado de operaciones simultáneas? → A: Hasta 15 usuarios simultáneos, ~200 liquidaciones por período, ~500 incidentes activos.

- Q: ¿Qué información adicional debe capturar la auditoría para esta funcionalidad? → A: Registrar usuario, fecha, acción realizada, valores anterior/nuevo + dirección IP del usuario, ID de sesión, y justificación obligatoria para asociaciones y modificaciones de plan.
