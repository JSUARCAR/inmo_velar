# Feature Specification: Ingeniería Inversa y Corrección - Eliminar Liquidación

**Feature Branch**: `[fix-delete-liquidation]`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre la funcionalidad Eliminar del módulo Liquidaciones de Propietarios, con el objetivo de comprender en profundidad su arquitectura, flujo de ejecución, lógica de negocio, integración entre frontend y backend, y proceso de eliminación antes de realizar cualquier modificación.
Durante las pruebas funcionales identifiqué una incidencia crítica: al hacer clic sobre la acción Eliminar, no se ejecuta ninguna operación. La interfaz no muestra mensajes de confirmación, errores, notificaciones ni realiza la eliminación del registro, lo que indica que existe una falla en el flujo de ejecución que debe ser diagnosticada y corregida."

## Clarifications

### Session 2026-07-02

- Q: Tipo de Eliminación → A: Eliminación lógica (soft delete) cambiando el estado a "Eliminada" o inactivo
- Q: Cuadro de Confirmación → A: Sí, mostrar un cuadro de diálogo/modal de confirmación antes de proceder con la acción

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Eliminar Liquidación Correctamente (Priority: P1)

Como usuario del módulo de Liquidaciones de Propietarios, quiero poder eliminar una liquidación (que cumpla con las reglas de negocio para ser eliminada) desde la interfaz de usuario, para mantener la información correcta y actualizada.

**Why this priority**: Es la funcionalidad core que reporta el usuario como no funcional. Un usuario debe poder eliminar registros erróneos o inválidos.

**Independent Test**: Can be fully tested by clicking the "Eliminar" button on a valid record in the UI, confirming the action in the modal dialog, and verifying the record is removed from the database and UI.

**Acceptance Scenarios**:

1. **Given** que el usuario se encuentra en la pantalla de Liquidaciones de Propietarios y existe una liquidación en estado "Pendiente" o válido para eliminar, **When** el usuario hace clic en "Eliminar", **Then** el sistema presenta un cuadro de confirmación modal.
2. **Given** que se presenta la confirmación de eliminación, **When** el usuario confirma la acción en el modal, **Then** el sistema realiza la eliminación en el backend, actualiza la interfaz eliminando el registro de la vista, y muestra un mensaje de éxito.

### Edge Cases

- What happens when el usuario intenta eliminar una liquidación que se encuentra en un estado protegido (e.g. "Pagada")?
- How does system handle una pérdida de conexión de red justo al momento de enviar la petición de eliminación al backend?
- What happens when la API retorna un error no esperado o un HTTP 500? (Debe mostrarse notificación de error).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST registrar de forma precisa y trazar la ruta de ejecución desde el clic en la UI hasta la eliminación de la base de datos (Ingeniería Inversa documentada).
- **FR-002**: System MUST requerir y mostrar un cuadro de confirmación modal explícito antes de proceder a realizar la eliminación lógica.
- **FR-003**: System MUST prevenir que los usuarios eliminen liquidaciones con estados protegidos (ej. Pagada).
- **FR-004**: System MUST comunicar al backend la solicitud de eliminación con la identificación correcta de la liquidación y las validaciones de seguridad o token necesarias.
- **FR-005**: System MUST reflejar inmediatamente el estado actualizado de la tabla de liquidaciones en la UI una vez la petición de eliminación haya retornado exitosamente.
- **FR-006**: System MUST notificar al usuario de forma visible (mediante toast o alert) sobre el éxito o fracaso de la operación.

### Key Entities *(include if feature involves data)*

- **Liquidacion**: Representa la liquidación financiera del propietario que será sometida al proceso de eliminación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- SC-001: 100% de las veces que se haga clic en "Eliminar", el sistema responde (ya sea con un error o procediendo al flujo de eliminación).
- SC-002: Los registros eliminados son marcados lógicamente como inactivos o "Eliminada" en la base de datos (soft delete), preservando la integridad referencial.
- SC-003: La UI de liquidaciones actualiza el listado visible en menos de 2 segundos tras una eliminación exitosa, sin requerir recarga manual de la página completa.

## Assumptions

- La eliminación se maneja lógicamente (`estado='Eliminada'` o inactivo) para preservar el historial financiero.
- Asumimos que los usuarios que ejecutan esta acción tienen los permisos (RBAC) necesarios para hacerlo.
- El módulo ya está migrado o se encuentra en proceso de estandarización sobre PostgreSQL/Reflex según la arquitectura élite de Velar.
