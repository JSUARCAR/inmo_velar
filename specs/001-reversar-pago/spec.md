# Feature Specification: Reversar Pago de Liquidación de Propietario

**Feature Branch**: `001-reversar-pago`

**Created**: 2026-06-30

**Status**: Draft

**Input**: User description: "Incorporar una nueva acción denominada Reversar Pago en el módulo de Liquidaciones de Propietarios, que permita reversar un pago previamente aplicado a una liquidación, garantizando consistencia transaccional, trazabilidad, auditoría, seguridad e idempotencia."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reversar Pago Individual (Priority: P1)

Como usuario autorizado (Administrador o usuario con permiso REVERSAR_PAGO), necesito poder reversar el pago de una liquidación que fue marcada como "Pagada", para corregir errores de registro de pago o atender solicitudes del propietario, garantizando que la operación sea completamente trazable y no afecte la integridad financiera del sistema.

**Why this priority**: Es la funcionalidad principal y más crítica. Sin ella no existe la feature.

**Independent Test**: Puede ser probada completamente al registrar una liquidación como pagada y luego ejecutar la reversión, verificando que el estado vuelve a "Aprobada" y que queda registro de auditoría.

**Acceptance Scenarios**:

1. **Given** una liquidación en estado "Pagada" con datos de pago registrados, **When** el usuario hace clic en "Reversar Pago" y confirma la operación, **Then** la liquidación retorna al estado "Aprobada", los campos de pago se limpian (fecha_pago, metodo_pago, referencia_pago), y se genera un registro de auditoría completo.

2. **Given** una liquidación en estado "Pagada", **When** el usuario intenta reversar el pago, **Then** se muestra un cuadro de confirmación que informa: monto a reversar, propietario, período, y consecuencias de la operación.

3. **Given** una liquidación que ya fue reversada previamente (estado "Aprobada"), **When** el usuario intenta reversar el pago nuevamente, **Then** la operación es un no-op silencioso: no se generan cambios, no se muestra error, y se retorna éxito.

4. **Given** una liquidación en estado "Aprobada" o "En Proceso", **When** el usuario observa la liquidación, **Then** el botón "Reversar Pago" NO está visible (solo aplica para estado "Pagada").

5. **Given** una reversión de pago ejecutada exitosamente, **When** se consulta el historial de auditoría, **Then** se muestra el registro con: usuario, fecha/hora, motivo, estado anterior ("Pagada"), estado posterior ("Aprobada"), e identificador único de la operación.

---

### User Story 2 - Confirmación con Impacto (Priority: P1)

Como usuario, antes de ejecutar una reversión de pago, necesito ver un resumen claro del impacto de la operación para tomar una decisión informada.

**Why this priority**: Es esencial para prevenir errores y garantizar que el usuario comprenda las consecuencias antes de ejecutar una operación financiera crítica.

**Independent Test**: Puede ser probada al abrir el diálogo de confirmación y verificar que muestra toda la información relevante.

**Acceptance Scenarios**:

1. **Given** una liquidación pagada seleccionada, **When** el usuario activa la acción "Reversar Pago", **Then** se muestra un diálogo de confirmación con: propietario, dirección de propiedad, período, monto neto a pagar, fecha de pago original, y un campo obligatorio de motivo (mínimo 10 caracteres). El diálogo NO incluye historial de la liquidación ni alertas de impacto en otros procesos.

2. **Given** el diálogo de confirmación abierto, **When** el usuario ingresa un motivo válido y confirma, **Then** la reversión se ejecuta.

3. **Given** el diálogo de confirmación abierto, **When** el usuario cancela, **Then** no se ejecuta ningún cambio y el diálogo se cierra.

---

### User Story 3 - Auditoría Completa (Priority: P2)

Como auditor o administrador, necesito que cada reversión de pago quede registrada permanentemente con información completa para consultas futuras y cumplimiento normativo.

**Why this priority**: Es requisito de cumplimiento financiero y trazabilidad. Sin auditoría completa la feature no cumple estándares empresariales.

**Independent Test**: Puede ser probada ejecutando una reversión y consultando la tabla de auditoría o el módulo de auditoría del sistema.

**Acceptance Scenarios**:

1. **Given** una reversión ejecutada, **When** se consulta la tabla AUDITORIA_CAMBIOS, **Then** existe un registro con tabla="LIQUIDACIONES", tipo_operacion="UPDATE", y los campos modificados (ESTADO_LIQUIDACION, FECHA_PAGO, METODO_PAGO, REFERENCIA_PAGO, PAGADA_POR, PAGADA_EN) con valores anteriores y nuevos.

2. **Given** una reversión ejecutada, **When** se consulta el registro de auditoría, **Then** incluye: usuario que realizó la reversión, fecha/hora exacta, motivo de la reversión (almacenado como registro adicional con CAMPO_MODIFICADO='MOTIVO_REVERSION'), e ID de la liquidación.

---

### User Story 4 - Permisos y Seguridad (Priority: P2)

Como administrador del sistema, necesito que la acción de reversar pago esté controlada por permisos, de modo que solo usuarios autorizados puedan ejecutarla.

**Why this priority**: Es esencial para la seguridad y control de acceso a operaciones financieras sensibles.

**Independent Test**: Puede ser probada iniciando sesión con un usuario sin permiso REVERSAR_PAGO y verificando que el botón no está visible.

**Acceptance Scenarios**:

1. **Given** un usuario con permiso "REVERSAR_PAGO" en el módulo "Liquidaciones", **When** visualiza una liquidación pagada, **Then** el botón "Reversar Pago" está visible y habilitado.

2. **Given** un usuario SIN permiso "REVERSAR_PAGO", **When** visualiza una liquidación pagada, **Then** el botón "Reversar Pago" NO está visible.

3. **Given** un usuario Administrador, **When** visualiza una liquidación pagada, **Then** el botón "Reversar Pago" SIEMPRE está visible (los administradores tienen todos los permisos).

---

### User Story 5 - Reversión Masiva por Propietario (Priority: P3)

Como usuario autorizado, necesito poder reversar los pagos de TODAS las liquidaciones de un propietario para un período específico, cuando sea necesario corregir un pago masivo incorrectly registrado.

**Why this priority**: Es una funcionalidad de conveniencia para casos donde se registró un pago masivo por error. Es menos frecuente que la reversión individual.

**Independent Test**: Puede ser probada al registrar pagos masivos para un propietario y luego ejecutar la reversión masiva.

**Acceptance Scenarios**:

1. **Given** un propietario con múltiples liquidaciones pagadas para un período, **When** el usuario ejecuta la reversión masiva, **Then** todas las liquidaciones pagadas de ese propietario en ese período retornan al estado "Aprobada" en una sola operación transaccional.

2. **Given** un propietario con liquidaciones en mixto de estados para un período (algunas "Pagada", otras "Aprobada" o "En Proceso"), **When** el usuario ejecuta la reversión masiva, **Then** solo se revierten las liquidaciones en estado "Pagada", las demás se ignoran, y se informa: cantidad reversadas, cantidad ignoradas, y IDs de cada grupo.

---

### Edge Cases

- ¿Qué sucede si se intenta reversar una liquidación que está siendo editada concurrentemente por otro usuario? → El sistema debe detectar el conflicto y rechazar la operación con un mensaje claro.

- ¿Qué sucede si la conexión a la base de datos se pierde durante la reversión? → La transacción debe hacer rollback automáticamente y mantener el estado original.

- ¿Qué sucede si se reversa una liquidación que tiene documentos adjuntos? → Los documentos NO se eliminan; la reversión solo afecta el estado financiero.

- ¿Qué sucede si se intenta reversar una liquidación en estado "Cancelada"? → El sistema debe rechazar la operación con un mensaje indicando que liquidaciones canceladas no pueden reversarse.

- ¿Qué sucede si el usuario intenta reversar el mismo pago dos veces rápidamente? → La operación debe ser idempotente; la segunda ejecución no debe generar cambios ni errores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow reversing a payment only for liquidations in "Pagada" state.
- **FR-002**: System MUST change liquidation state from "Pagada" to "Aprobada" upon payment reversal.
- **FR-003**: System MUST clear payment fields (fecha_pago, metodo_pago, referencia_pago, pagada_por, pagada_en) upon reversal.
- **FR-004**: System MUST require a minimum 10-character justification/motivo for each reversal.
- **FR-005**: System MUST display a confirmation dialog with impact summary before executing reversal.
- **FR-006**: System MUST execute reversal as an atomic transaction (rollback on any failure).
- **FR-007**: System MUST create a complete audit trail in AUDITORIA_CAMBIOS for every reversal.
- **FR-008**: System MUST enforce permission "REVERSAR_PAGO" on module "Liquidaciones" for non-admin users.
- **FR-009**: System MUST be idempotent - if a payment has already been reversed (liquidation not in "Pagada" state), the operation must be a silent no-op returning success, with no error messages or side effects.
- **FR-010**: System MUST update all derived financial data (consolidated states, reports) immediately after reversal.
- **FR-011**: System MUST NOT delete any historical data; reversal must be fully reversible via audit trail.
- **FR-012**: System MUST support bulk reversal for all liquidations of a owner in a specific period.
- **FR-013**: System MUST NOT affect other financial processes during reversal. Specifically: collections from tenants (recaudos), bank reconciliations, and previously generated reports remain untouched. Only the liquidation state and audit trail are modified.
- **FR-014**: System MUST generate a unique operation ID for each reversal for traceability.

## Out of Scope

The following are explicitly OUT OF SCOPE for this feature:

- Reversal of tenant collections (recaudos) associated with the payment
- Automatic generation of accounting entries or journal entries
- Modification of bank reconciliations
- Regeneration or invalidation of previously generated PDF reports
- Notifications to external parties (proprietors, accountants) upon reversal
- Webhook or API event emission for integration with external systems

### Key Entities

- **Liquidacion**: Represents the monthly account statement for a property owner. Key states: 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada'. Payment reversal transitions from 'Pagada' → 'Aprobada'.

- **AuditoriaCambio**: Immutable audit record stored in AUDITORIA_CAMBIOS table. Captures every state change with before/after values, user, timestamp, and motivation.

- **Usuario/Sesion**: The authenticated user performing the reversal. Used for permission checks and audit trail.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a payment reversal in under 30 seconds (including confirmation).
- **SC-002**: 100% of payment reversals generate a complete audit trail with all required fields.
- **SC-003**: Zero data inconsistencies after reversal - all financial balances, states, and reports reflect the new state immediately.
- **SC-004**: Idempotency is maintained - 100% of repeated reversal attempts are safely handled without errors or data corruption.
- **SC-005**: Only authorized users can see and execute the reversal action (permission enforcement at UI and backend levels).
- **SC-006**: Transaction atomicity is maintained - zero partial reversals in case of system failures.

## Clarifications

### Session 2026-06-30

- Q: Idempotencia vs. Mensaje de Error — ¿Qué comportamiento al intentar reversar un pago ya reversado? → A: Idempotente silencioso — si la liquidación ya está en "Aprobada", la operación es un no-op que retorna éxito sin cambios ni errores.
- Q: Reversión Masiva — ¿Qué comportamiento cuando algunas liquidaciones del propietario no están en "Pagada"? → A: Selectivo — revierte solo las que están en "Pagada", ignora las demás, informa el resultado.
- Q: Almacenamiento del Motivo — ¿Dónde se guarda el motivo obligatorio de la reversión? → A: Registro adicional en AUDITORIA_CAMBIOS con CAMPO_MODIFICADO='MOTIVO_REVERSION' y VALOR_NUEVO con el texto del motivo.
- Q: Fuera de Alcance — ¿Qué procesos NO deben ser afectados por la reversión? → A: La reversión solo modifica el estado de la liquidación. NO afecta recaudos de inquilinos, conciliaciones bancarias, ni reportes ya generados.
- Q: Contenido del Diálogo de Confirmación — ¿Qué información mostrar al usuario antes de confirmar? → A: Solo estado actual: propietario, dirección de propiedad, período, monto neto a pagar, y fecha de pago original. Sin historial ni alertas de impacto.

## Assumptions

- The existing AUDITORIA_CAMBIOS table and triggers will capture reversal operations automatically (existing trigger on LIQUIDACIONES table handles UPDATE operations).
- The permission system already supports per-module action checks via `AuthState.check_action()`.
- The current user authentication system provides the `usuario_sistema` value for audit trails.
- The existing UI component library (neuro_elements) will be used for consistent styling of the new confirmation dialog.
- The database transaction mechanism (commit/rollback) is already properly implemented in the repository layer.
- No changes to the database schema are required - the existing LIQUIDACIONES table and AUDITORIA_CAMBIOS table have all necessary columns.

## Dependencies

- **Existing Module**: Liquidaciones de Propietarios (fully implemented with CRUD, approval, payment, cancellation, and reversal-for-approval workflows)
- **Permission System**: Module "Liquidaciones" with action "REVERSAR_PAGO" must be registered in the permissions configuration
- **Audit System**: AUDITORIA_CAMBIOS table with triggers on LIQUIDACIONES table must be active
- **UI Framework**: Reflex framework with neuro_elements component library

## Technical Justification

The implementation follows the existing architecture patterns:

1. **Repository Pattern**: New `reversar_pago()` method in `RepositorioLiquidacionPostgres` following the same pattern as existing `reversar()` and `marcar_como_pagada()` methods.

2. **Service Layer**: New `reversar_pago_liquidacion()` method in `ServicioFinanciero` that orchestrates the business logic, validation, and repository calls.

3. **State Management**: New event handlers in `LiquidacionesState` following the existing pattern of `open_reverse_confirm()` → `confirmar_reversar()`.

4. **UI Components**: New confirmation dialog component following the existing `reverse_confirm_dialog.py` pattern, with enhanced impact information.

5. **Permission Integration**: Using existing `AuthState.check_action()` mechanism with new action type "REVERSAR_PAGO".

6. **Transaction Safety**: Using existing database connection/transaction management with explicit commit/rollback.

7. **Idempotency**: Implemented via state check - if state is already "Aprobada" (not "Pagada"), the operation is a no-op rather than an error.

8. **Audit Trail**: Leveraging existing AUDITORIA_CAMBIOS trigger on LIQUIDACIONES table - no custom audit code needed.
