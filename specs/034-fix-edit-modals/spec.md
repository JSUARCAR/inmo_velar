# Feature Specification: fix-edit-modals

**Feature Branch**: `[034-fix-edit-modals]`

**Created**: 2026-07-07

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre los siguientes módulos, ya que identifiqué una incidencia crítica que impide la edición de los registros. Modales Editar Liquidación y Editar Recaudo no permiten ser modificados (disabled/readonly)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Editar un registro de Liquidación existente (Priority: P1)

Como usuario del sistema, quiero poder modificar los campos de un registro de Liquidación desde el modal "Editar Liquidación" para corregir o actualizar la información.

**Why this priority**: Es una funcionalidad crítica de negocio (CRUD básico) que actualmente está bloqueada, impidiendo la actualización de datos financieros.

**Independent Test**: Can be fully tested by abriendo un registro de liquidación existente y modificando un campo, para luego guardar y verificar que el cambio se refleje en la tabla y en la base de datos PostgreSQL.

**Acceptance Scenarios**:

1. **Given** un registro de liquidación en un estado que permita edición, **When** el usuario abre el modal de edición, **Then** todos los campos editables del formulario deben estar habilitados (no bloqueados, ni disabled, ni readonly).
2. **Given** un formulario de edición de liquidación con campos modificados, **When** el usuario guarda los cambios, **Then** la información debe actualizarse exitosamente en PostgreSQL y reflejarse de inmediato en la UI.

---

### User Story 2 - Editar un registro de Recaudo existente (Priority: P1)

Como usuario del sistema, quiero poder modificar los campos de un registro de Recaudo desde el modal "Editar Recaudo" para corregir o actualizar detalles del pago.

**Why this priority**: Al igual que las liquidaciones, la gestión de recaudos es un proceso core del sistema. No poder editar un recaudo genera inconsistencias en la información de pagos.

**Independent Test**: Can be fully tested by modificando un campo de un recaudo existente, guardando los cambios y validando la persistencia y la actualización de la UI.

**Acceptance Scenarios**:

1. **Given** un registro de recaudo válido para edición, **When** el usuario abre el modal de edición, **Then** los campos del formulario deben ser accesibles y modificables.
2. **Given** un formulario de edición de recaudo modificado, **When** el usuario envía el formulario, **Then** los datos se persisten en PostgreSQL y la tabla de recaudos se actualiza inmediatamente en el frontend.

### Edge Cases

- What happens when el registro se encuentra en un estado que por reglas de negocio NO debe ser editable (ej. ya contabilizado, anulado)? El sistema debe reflejar el estado readonly adecuadamente, pero solo para esos casos justificados.
- How does system handle fallos de validación (ej. campos obligatorios vacíos o formatos incorrectos) durante la edición?
- How does system handle problemas de concurrencia o de conexión con PostgreSQL al momento de guardar los cambios?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST enable user interaction (remove unintended `disabled` or `readonly` properties) for all applicable input controls (inputs, ComboBox, Select, DatePicker, TextArea, Checkbox) in the "Editar Liquidación" modal.
- **FR-002**: System MUST enable user interaction for all applicable input controls in the "Editar Recaudo" modal.
- **FR-003**: System MUST correctly load the existing record data from the backend into the forms when opening the edit modals.
- **FR-004**: System MUST apply business rules and RBAC permissions to determine if a record should truly be editable or locked.
- **FR-005**: System MUST successfully persist the edited data to the PostgreSQL database when the user saves the changes.
- **FR-006**: System MUST update the UI state immediately after a successful edit, ensuring synchronization between frontend and backend.

### Key Entities *(include if feature involves data)*

- **Liquidacion**: Represents a financial liquidation record that needs its fields updated.
- **Recaudo**: Represents a payment collection record that needs its fields updated.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the input fields intended to be editable in the "Editar Liquidación" and "Editar Recaudo" modals allow user input and modification.
- **SC-002**: Edited records are saved and reflected in the UI within 1 second of submission.
- **SC-003**: 0 regressions introduced in the creation and deletion flows for both Liquidaciones and Recaudos.

## Assumptions

- PostgreSQL database schema supports the necessary update operations and is accessible.
- Business rules governing the editability of records (e.g. states like "Pagado" or "Pendiente") are already defined and just need to be correctly evaluated by the UI/backend.
- RBAC permissions are correctly configured and the issue lies in frontend state management or a bug in how data is bound to the form controls.
