# Feature Specification: Eliminar Liquidación de Propietario

**Feature Branch**: `002-eliminar-liquidacion`

**Created**: 2026-06-30

**Status**: Draft

**Input**: User description: "Incorporar una nueva acción denominada Eliminar Liquidación en el módulo de Liquidaciones de Propietarios, que permita eliminar una liquidación que no se encuentre en estado Pagada, garantizando integridad de datos, auditoría, seguridad, trazabilidad y cumplimiento de reglas de negocio."

## Clarifications

### Session 2026-06-30

- Q: ¿Qué mecanismo de confirmación explícita se usa antes de ejecutar la eliminación? → A: Checkbox con etiqueta de advertencia que debe marcarse antes de habilitar el botón de confirmar.
- Q: ¿Qué sucede con los documentos adjuntos (soportes) de una liquidación eliminada? → A: Se marcan como huérfanos: se conservan en el sistema pero se desvinculan de la liquidación eliminada.
- Q: ¿Qué sucede en la vista agrupada si se eliminan todas las liquidaciones de un propietario en un período? → A: La fila del propietario desaparece de la vista agrupada (no hay liquidaciones para mostrar).
- Q: ¿Qué información muestra el cuadro de confirmación de eliminación? → A: Resumen (propietario, dirección, período, neto a pagar, estado) más desglose financiero detallado (ingresos, comisión, IVA, gastos, etc.).
- Q: ¿Qué retroalimentación recibe el usuario después de una eliminación exitosa o fallida? → A: Toast de notificación en posición bottom-right con mensaje de éxito o error, más recarga automática de la tabla de liquidaciones.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Eliminar Liquidación Individual (Priority: P1)

Como usuario autorizado (Administrador o usuario con permiso ELIMINAR en el módulo Liquidaciones), necesito poder eliminar una liquidación de propietario que no esté en estado "Pagada", para corregir errores de generación, eliminar registros duplicados o atender solicitudes de administración, garantizando que la operación sea completamente trazable y no afecte la integridad financiera del sistema.

**Why this priority**: Es la funcionalidad principal y más crítica. Sin ella no existe la feature.

**Independent Test**: Puede ser probada al crear una liquidación en estado "En Proceso" y luego ejecutar la eliminación, verificando que el registro desaparece de la vista y queda registro de auditoría.

**Acceptance Scenarios**:

1. **Given** una liquidación en estado "En Proceso", **When** el usuario selecciona la acción "Eliminar" y confirma la operación en el cuadro de diálogo, **Then** la liquidación es eliminada del sistema, se genera un registro de auditoría completo con los datos de la liquidación antes de la eliminación, se muestra un toast de éxito en posición bottom-right, y la tabla de liquidaciones se recarga automáticamente reflejando la ausencia del registro.

2. **Given** una liquidación en estado "Aprobada", **When** el usuario selecciona la acción "Eliminar" y confirma la operación, **Then** la liquidación es eliminada del sistema con registro de auditoría completo, se muestra un toast de éxito, y la tabla se recarga, dado que el estado "Aprobada" no representa un compromiso de pago ya ejecutado.

3. **Given** una liquidación en estado "Cancelada", **When** el usuario selecciona la acción "Eliminar" y confirma la operación, **Then** la liquidación es eliminada del sistema con registro de auditoría completo, se muestra un toast de éxito, y la tabla se recarga, dado que una liquidación cancelada no tiene impacto financiero activo.

4. **Given** una liquidación en estado "Pagada", **When** el usuario observa la liquidación en la tabla o en el modal de detalle, **Then** el botón o acción "Eliminar" NO está visible ni habilitado bajo ninguna circunstancia.

5. **Given** una liquidación en estado "Pagada", **When** un usuario intenta ejecutar la eliminación mediante cualquier mecanismo (URL directa, manipulación de estado, llamada API), **Then** el sistema rechaza la operación con un mensaje claro: "Las liquidaciones en estado Pagada forman parte del histórico financiero y no pueden eliminarse."

6. **Given** una liquidación eliminada exitosamente, **When** se consulta el historial de auditoría, **Then** se muestra el registro con: usuario que realizó la operación, fecha/hora exacta, identificador de la liquidación, estado de la liquidación antes de la eliminación, y tipo de eliminación realizada.

---

### User Story 2 - Confirmación con Impacto (Priority: P1)

Como usuario, antes de ejecutar una eliminación, necesito ver un cuadro de confirmación que informe claramente las consecuencias de la operación y solicite confirmación explícita.

**Why this priority**: Es esencial para prevenir eliminaciones accidentales y garantizar que el usuario comprenda las consecuencias antes de ejecutar una operación destructiva e irreversible.

**Independent Test**: Puede ser probada al abrir el diálogo de confirmación y verificar que muestra toda la información relevante y requiere confirmación explícita.

**Acceptance Scenarios**:

1. **Given** una liquidación elegible para eliminación (estado diferente de "Pagada"), **When** el usuario activa la acción "Eliminar", **Then** se muestra un cuadro de diálogo de confirmación que incluye: propietario, dirección de propiedad, período, monto neto a pagar, estado actual, y un mensaje claro que indique que la operación es irreversible.

2. **Given** el cuadro de confirmación abierto, **When** el usuario confirma la eliminación, **Then** la operación se ejecuta.

3. **Given** el cuadro de confirmación abierto, **When** el usuario cancela, **Then** no se ejecuta ningún cambio y el cuadro se cierra.

4. **Given** el cuadro de confirmación abierto, **When** el usuario intenta confirmar sin haber leído el mensaje, **Then** el sistema requiere marcar un checkbox de confirmación con etiqueta de advertencia antes de habilitar el botón de confirmar.

---

### User Story 3 - Auditoría Completa (Priority: P2)

Como auditor o administrador, necesito que cada eliminación quede registrada permanentemente con información completa para consultas futuras y cumplimiento normativo.

**Why this priority**: Es requisito de cumplimiento financiero y trazabilidad. Sin auditoría completa la feature no cumple estándares empresariales.

**Independent Test**: Puede ser probada ejecutando una eliminación y consultando la tabla de auditoría o el módulo de auditoría del sistema.

**Acceptance Scenarios**:

1. **Given** una eliminación ejecutada, **When** se consulta la tabla de auditoría, **Then** existe un registro que incluye como mínimo: usuario que realizó la operación, fecha/hora de la eliminación, identificador de la liquidación, estado de la liquidación antes de la eliminación, y tipo de eliminación realizada (lógica o física).

2. **Given** una eliminación ejecutada, **When** se consulta el registro de auditoría, **Then** los datos son consistentes e inmutables (no pueden ser modificados posteriormente).

---

### User Story 4 - Permisos y Seguridad (Priority: P2)

Como administrador del sistema, necesito que la acción de eliminar esté controlada por permisos, de modo que solo usuarios autorizados puedan ejecutarla.

**Why this priority**: Es esencial para la seguridad y control de acceso a operaciones destructivas.

**Independent Test**: Puede ser probada iniciando sesión con un usuario sin permiso ELIMINAR y verificando que el botón no está visible.

**Acceptance Scenarios**:

1. **Given** un usuario con permiso "ELIMINAR" en el módulo "Liquidaciones", **When** visualiza una liquidación elegible (estado != "Pagada"), **Then** la acción "Eliminar" está visible y habilitada.

2. **Given** un usuario SIN permiso "ELIMINAR", **When** visualiza una liquidación elegible, **Then** la acción "Eliminar" NO está visible.

3. **Given** un usuario Administrador, **When** visualiza una liquidación elegible, **Then** la acción "Eliminar" SIEMPRE está visible (los administradores tienen todos los permisos).

---

### User Story 5 - Eliminación en Vista Agrupada (Priority: P3)

Como usuario autorizado, necesito poder eliminar liquidaciones individuales desde la vista agrupada por propietario, cuando una liquidación específica dentro del consolidado requiere ser eliminada.

**Why this priority**: Es una funcionalidad de conveniencia para la vista consolidada. La eliminación individual desde la vista detallada es la primaria.

**Independent Test**: Puede ser probada al abrir el detalle consolidado de un propietario y ejecutar la eliminación de una liquidación individual.

**Acceptance Scenarios**:

1. **Given** un propietario con múltiples liquidaciones para un período, donde al menos una no está en estado "Pagada", **When** el usuario abre el detalle consolidado y selecciona eliminar una liquidación individual, **Then** solo esa liquidación se elimina, las demás permanecen intactas, y el consolidado se recalcula. Si se eliminan todas las liquidaciones del propietario para ese período, la fila del propietario desaparece de la vista agrupada.

---

### Edge Cases

- ¿Qué sucede si se intenta eliminar una liquidación que está siendo editada concurrentemente por otro usuario? → El sistema debe detectar el conflicto y rechazar la operación con un mensaje claro.

- ¿Qué sucede si la conexión a la base de datos se pierde durante la eliminación? → La transacción debe hacer rollback automáticamente y mantener el estado original.

- ¿Qué sucede si se elimina una liquidación que tiene documentos adjuntos? → Los documentos adjuntos se marcan como huérfanos: se conservan en el sistema pero se desvinculan de la liquidación eliminada, evitando referencias rotas.

- ¿Qué sucede si se intenta eliminar una liquidación que es la única de un propietario en un período? → La eliminación se ejecuta normalmente; el propietario queda sin liquidaciones para ese período.

- ¿Qué sucede si el usuario intenta eliminar la misma liquidación dos veces rápidamente? → La operación debe ser idempotente; la segunda ejecución debe detectar que la liquidación ya no existe y retornar éxito sin errores.

- ¿Qué sucede si se elimina una liquidación y luego se genera una nueva para el mismo contrato y período? → Debe permitirse, ya que el período queda libre tras la eliminación.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow deletion only for liquidations NOT in "Pagada" state. Liquidations in "Pagada" state MUST be permanently protected from deletion.

- **FR-002**: System MUST implement soft delete (logical deletion) rather than physical deletion. Soft-deleted liquidations MUST be excluded from all listing, reporting, and financial calculation queries while preserving the original record for audit trail purposes.

- **FR-003**: System MUST display a confirmation dialog before executing deletion, showing: owner name, property address, period, net amount, current state, and a clear warning that the operation is irreversible.

- **FR-004**: System MUST require the user to check a confirmation checkbox with a warning label before enabling the delete confirmation button.

- **FR-005**: System MUST execute deletion as an atomic transaction (rollback on any failure).

- **FR-006**: System MUST create a complete audit record for every deletion, including: user, timestamp, liquidation ID, state before deletion, and deletion type (soft delete).

- **FR-007**: System MUST enforce permission "ELIMINAR" on module "Liquidaciones" for non-admin users.

- **FR-008**: System MUST be idempotent - if a liquidation has already been deleted, a subsequent deletion attempt must be a silent no-op returning success.

- **FR-009**: System MUST exclude soft-deleted liquidations from all listing, pagination, filtering, reporting, and financial calculation queries.

- **FR-010**: System MUST NOT affect other financial processes during deletion. Specifically: tenant collections (recaudos), bank reconciliations, previously generated reports, and other liquidations remain untouched.

- **FR-011**: System MUST update all derived financial data (consolidated states, owner balances, reports) immediately after deletion.

- **FR-012**: System MUST NOT allow editing, approving, paying, or performing any state transition on a soft-deleted liquidation.

- **FR-013**: System MUST hide the "Eliminar" action button for liquidations in "Pagada" state in both individual and grouped views.

- **FR-014**: System MUST generate a unique operation ID for each deletion attempt for traceability.

- **FR-015**: System MUST allow re-generation of a liquidation for the same contract and period after the previous one has been deleted.

- **FR-016**: System MUST display a success toast notification (bottom-right position) after a successful deletion and automatically reload the liquidation table.

- **FR-017**: System MUST mark associated document attachments (soportes) as orphans upon liquidation deletion: preserve them in the system but unlink them from the deleted liquidation.

### Key Entities

- **Liquidacion**: Represents the monthly account statement for a property owner. Key states: 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada'. Deletion is only allowed for non-'Pagada' states. Soft-deleted records are marked as deleted but retained for audit purposes.

- **AuditoriaCambio**: Audit record capturing every deletion with before/after values, user, timestamp, and operation type.

- **Usuario/Sesion**: The authenticated user performing the deletion. Used for permission checks and audit trail.

## Out of Scope

The following are explicitly OUT OF SCOPE for this feature:

- Hard/physical deletion of liquidation records from the database
- Automatic regeneration of PDF reports after deletion
- Notifications to external parties (owners, accountants) upon deletion
- Webhook or API event emission for integration with external systems
- Deletion of associated tenant collections (recaudos)
- Bulk deletion of multiple liquidations in a single operation
- Recovery or undelete functionality for soft-deleted liquidations
- Modification of historical audit trail records

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a liquidation deletion in under 30 seconds (including confirmation dialog interaction).

- **SC-002**: 100% of deletions generate a complete audit trail with all required fields (user, timestamp, liquidation ID, previous state, deletion type).

- **SC-003**: Zero data inconsistencies after deletion - all financial balances, states, consolidated views, and reports reflect the deletion immediately.

- **SC-004**: 100% of deletion attempts on "Pagada" state liquidations are blocked with a clear error message, regardless of the access method.

- **SC-005**: Only authorized users can see and execute the deletion action (permission enforcement at UI and backend levels).

- **SC-006**: Transaction atomicity is maintained - zero partial deletions in case of system failures.

- **SC-007**: Idempotency is maintained - 100% of repeated deletion attempts on already-deleted liquidations are safely handled without errors or data corruption.

- **SC-008**: Deleted liquidations are excluded from 100% of listing, filtering, reporting, and financial calculation operations.

## Assumptions

- The existing permission system supports per-module action checks via `AuthState.check_action()`. A new action "ELIMINAR" will be registered for the "Liquidaciones" module.
- The current user authentication system provides the `usuario_sistema` value for audit trails.
- The existing UI component library (neuro_elements) will be used for consistent styling of the new confirmation dialog.
- The database transaction mechanism (commit/rollback) is already properly implemented in the repository layer.
- Soft delete is the appropriate strategy given the financial nature of the data, the audit requirements, and the existing architecture patterns in the system (other entities like usuarios, personas, propiedades already use soft delete).
- The audit system (AUDITORIA_CAMBIOS table and triggers) will capture deletion operations, or application-level audit code will be implemented if triggers are not available.
- The database schema will be extended to support soft deletion without requiring a separate audit/log table.
- Document attachments (soportes) associated with a deleted liquidation will be marked as orphans: preserved in the system but unlinked from the deleted liquidation to avoid broken references.

## Dependencies

- **Existing Module**: Liquidaciones de Propietarios (fully implemented with CRUD, approval, payment, cancellation, and reversal workflows)
- **Permission System**: Module "Liquidaciones" with action "ELIMINAR" must be registered in the permissions configuration
- **Audit System**: AUDITORIA_CAMBIOS table with triggers on LIQUIDACIONES table must be active, or application-level audit code must be implemented
- **UI Framework**: Reflex framework with neuro_elements component library
- **Database**: Schema migration to support soft deletion of liquidation records

## Technical Justification

The implementation follows the existing architecture patterns:

1. **Repository Pattern**: New `eliminar()` method in `RepositorioLiquidacionPostgres` following the same pattern as existing `cancelar()` and `reversar()` methods. Uses soft delete (UPDATE SET ELIMINADA=TRUE) rather than physical DELETE.

2. **Service Layer**: New `eliminar_liquidacion()` method in `ServicioFinanciero` that orchestrates the business logic (state validation, permission check), repository call, and audit logging.

3. **State Management**: New event handlers in `LiquidacionesState` following the existing pattern of `open_cancel_modal()` → `cancelar_liquidacion()`. New state variables: `show_delete_confirm`, `liquidacion_id_for_delete`.

4. **UI Components**: New confirmation dialog component following the existing `cancel_modal.py` pattern, with enhanced safety confirmation (require typing "ELIMINAR" or checkbox).

5. **Permission Integration**: Using existing `AuthState.check_action()` mechanism with new action type "ELIMINAR".

6. **Soft Delete Strategy**: Chosen over hard delete because: (a) financial data requires permanent retention for audit purposes, (b) existing system patterns already use soft delete for similar entities, (c) soft delete allows potential recovery and preserves referential integrity, (d) the deleted flag provides clean separation between active and deleted records without data loss.

7. **Query Filtering**: All existing queries in the repository will be updated to exclude soft-deleted records from all operations.

8. **Idempotency**: Implemented via existence check - if the liquidation is already soft-deleted, the operation is a no-op rather than an error.

9. **Audit Trail**: Leveraging existing AUDITORIA_CAMBIOS infrastructure. A new audit entry with operation type "DELETE" (soft) will be created for each deletion.
