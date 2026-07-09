# Feature Specification: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Feature Branch**: `038-liquidacion-asesores-actions`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Implementar una nueva lógica de disponibilidad de acciones basada en el estado de cada liquidación en el módulo Liquidacion Asesores. La acción Eliminar solo debe estar disponible para liquidaciones en estado Pendiente. La acción Reversar solo debe estar disponible para liquidaciones en estados diferentes de Pendiente (Aprobada, Pagada, Anulada). Las reglas deben aplicarse de forma consistente en frontend, backend y base de datos."

## Clarifications

### Session 2026-07-08

- Q: Alcance del módulo → A: Solo Liquidacion Asesores (NO Liquidaciones de Propietarios)
- Q: Estados del módulo → A: Pendiente, Aprobada, Pagada, Anulada (definidos en la entidad)
- Q: Comportamiento de Reversar para Pagada → A: Pagada → Aprobada (reversión de pago, mantiene estado de aprobación)
- Q: Justificación para reversión de Anulada → A: Requerir motivo obligatorio (mínimo 10 caracteres) para reversión de Anulada→Pendiente

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización de Acciones según Estado (Priority: P1)

Como usuario del módulo Liquidacion Asesores, quiero que las acciones disponibles en cada liquidación cambien dinámicamente según su estado, para ejecutar únicamente las operaciones permitidas y evitar errores de negocio.

**Why this priority**: Es la funcionalidad core de esta feature. Garantiza que la UI refleje fielmente las reglas de negocio, evitando que usuarios intenten acciones inválidas.

**Independent Test**: Can be fully tested by navigating to the liquidaciones asesores list, verifying that a "Pendiente" record shows only "Eliminar" and records in other states show only "Reversar".

**Acceptance Scenarios**:

1. **Given** que existe una liquidación en estado "Pendiente", **When** el usuario observa las acciones disponibles para ese registro, **Then** únicamente se muestra la acción "Eliminar".
2. **Given** que existe una liquidación en estado "Aprobada", **When** el usuario observa las acciones disponibles para ese registro, **Then** únicamente se muestra la acción "Reversar".
3. **Given** que existe una liquidación en estado "Pagada", **When** el usuario observa las acciones disponibles para ese registro, **Then** únicamente se muestra la acción "Reversar".
4. **Given** que existe una liquidación en estado "Anulada", **When** el usuario observa las acciones disponibles para ese registro, **Then** únicamente se muestra la acción "Reversar".

---

### User Story 2 - Ejecución Segura de Eliminar (Priority: P1)

Como usuario, quiero que al intentar eliminar una liquidación en estado Pendiente, el sistema solicite confirmación y ejecute la eliminación lógica validando integridad referencial.

**Why this priority**: La eliminación es una operación destructiva que requiere validación en capa servidor. No debe ejecutarse si la liquidación tiene relaciones que lo impidan.

**Independent Test**: Can be tested by clicking "Eliminar" on a Pendiente record, confirming in modal, and verifying the record is soft-deleted and no orphan data remains.

**Acceptance Scenarios**:

1. **Given** que una liquidación está en estado "Pendiente" y el usuario hace clic en "Eliminar", **When** el sistema procesa la solicitud, **Then** se muestra un modal de confirmación antes de ejecutar.
2. **Given** que el usuario confirma la eliminación, **When** el backend procesa la solicitud, **Then** la liquidación se marca como eliminada lógicamente (soft delete) y no quedan registros huérfanos.
3. **Given** que la liquidación tiene entidades relacionadas que impiden su eliminación, **When** el backend valida la solicitud, **Then** el sistema retorna un mensaje claro al usuario indicando el motivo del fallo.

---

### User Story 3 - Ejecución Segura de Reversar (Priority: P1)

Como usuario, quiero que al intentar reversar una liquidación en estado Aprobada/Pagada/Anulada, el sistema valide el estado y ejecute la reversión manteniendo integridad histórica.

**Why this priority**: La reversión es una operación que deshace efectos financieros. Debe validarse estrictamente en capa servidor.

**Independent Test**: Can be tested by clicking "Reversar" on an Aprobada record, confirming, and verifying the state changes correctly and related entities are updated.

**Acceptance Scenarios**:

1. **Given** que una liquidación está en estado "Aprobada" y el usuario hace clic en "Reversar", **When** el sistema procesa la solicitud, **Then** se muestra un modal de confirmación antes de ejecutar.
2. **Given** que el usuario confirma la reversión, **When** el backend procesa la solicitud, **Then** la liquidación retrocede de "Aprobada" a "Pendiente" y los efectos generados se deshacen correctamente.
3. **Given** que una liquidación está en estado "Pagada" o "Anulada" y el usuario hace clic en "Reversar", **When** se muestra el modal de confirmación, **Then** el sistema incluye un campo "motivo" obligatorio (mínimo 10 caracteres) que debe completarse antes de ejecutar.
4. **Given** que la liquidación está en un estado que no permite reversión, **When** el backend valida la solicitud, **Then** el sistema retorna un error claro y no modifica ningún registro.

---

### User Story 4 - Validación Backend Reforzada (Priority: P2)

Como administrador del sistema, quiero que las APIs validen el estado de la liquidación antes de ejecutar cualquier acción, incluso si la petición se invoca manualmente (curl, script), para garantizar integridad de datos.

**Why this priority**: Protección contra manipulación directa de APIs. Asegura que las reglas de negocio se apliquen independientemente del cliente.

**Independent Test**: Can be tested by sending a direct API request to delete a liquidación in "Aprobada" state and verifying the server rejects it with an appropriate error.

**Acceptance Scenarios**:

1. **Given** que se envía una petición API para eliminar una liquidación en estado "Aprobada", **When** el backend procesa la solicitud, **Then** la petición es rechazada con un código de error y un mensaje descriptivo.
2. **Given** que se envía una petición API para reversar una liquidación en estado "Pendiente", **When** el backend procesa la solicitud, **Then** la petición es rechazada con un código de error y un mensaje descriptivo.

---

### Edge Cases

- ¿Qué sucede cuando una liquidación tiene descuentos, bonificaciones o comisiones asociadas y se intenta eliminar? → El backend debe verificar integridad referencial y rechazar si existen dependencias.
- ¿Qué sucede si la liquidación está en estado "Anulada" y se intenta reversar? → El sistema debe permitir reversión a "Pendiente" ya que "Anulada" es un estado diferente de "Pendiente".
- ¿Qué sucede si la liquidación está en estado "Pagada" y se intenta reversar? → El sistema ejecuta una reversión de pago: Pagada → Aprobada (consistente con la operación `reversar_pago_liquidacion` existente).
- ¿Cómo maneja el sistema una pérdida de conexión durante la ejecución de eliminar/reversar? → Debe mostrar mensaje de error y permitir reintentar.
- ¿Qué sucede si la API retorna un error inesperado (HTTP 500)? → Debe mostrarse notificación de error al usuario.
- ¿Qué pasa si se intenta eliminar una liquidación que ya fue eliminada previamente? → La operación debe ser idempotente, retornando éxito sin modificar nada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST mostrar la acción "Eliminar" ÚNICAMENTE cuando la liquidación esté en estado "Pendiente".
- **FR-002**: System MUST mostrar la acción "Reversar" ÚNICAMENTE cuando la liquidación esté en un estado diferente de "Pendiente" (Aprobada, Pagada, Anulada).
- **FR-003**: System MUST ocultar la acción "Reversar" cuando la liquidación esté en estado "Pendiente".
- **FR-004**: System MUST ocultar la acción "Eliminar" cuando la liquidación esté en cualquier estado que no sea "Pendiente".
- **FR-005**: System MUST ejecutar la eliminación lógica (soft delete) en capa servidor, nunca solo en frontend.
- **FR-006**: System MUST validar en backend que la liquidación esté en estado "Pendiente" antes de permitir eliminación.
- **FR-007**: System MUST validar en backend que la liquidación NO esté en estado "Pendiente" antes de permitir reversión.
- **FR-008**: System MUST revertir los efectos generados por la liquidación al ejecutar "Reversar" con las transiciones: Aprobada→Pendiente, Pagada→Aprobada, Anulada→Pendiente.
- **FR-008a**: System MUST requerir un campo "motivo" obligatorio (mínimo 10 caracteres) al reversar liquidaciones en estado "Pagada" o "Anulada".
- **FR-009**: System MUST rechazar acciones sobre liquidaciones con entidades relacionadas que impidan la operación, retornando un mensaje descriptivo.
- **FR-010**: System MUST mostrar modal de confirmación antes de ejecutar cualquier acción destructiva (eliminar o reversar).
- **FR-011**: System MUST actualizar inmediatamente la interfaz después de una operación exitosa sin recarga de página completa.
- **FR-012**: System MUST notificar al usuario sobre el éxito o fracaso de la operación mediante toast o alerta.
- **FR-013**: System MUST mantener consistencia entre las acciones visibles en la UI y las permitidas por la lógica del servidor.

### Key Entities

- **Liquidacion Asesor**: Representa la liquidación financiera de un asesor inmobiliario. Estados posibles: Pendiente, Aprobada, Pagada, Anulada.
- **Descuento**: Descuento aplicado a una liquidación de asesor. Relacionado con la liquidación padre.
- **Bonificacion**: Bonificación aplicada a una liquidación de asesor. Relacionado con la liquidación padre.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las liquidaciones en estado "Pendiente" muestran únicamente la acción "Eliminar" en la UI.
- **SC-002**: 100% de las liquidaciones en estados Aprobada/Pagada/Anulada muestran únicamente la acción "Reversar" en la UI.
- **SC-003**: 0% de las acciones ejecutadas desde la UI violan las reglas de negocio validadas en backend.
- **SC-004**: Las APIs rechazan el 100% de las peticiones que no cumplen las reglas de estado, incluso con invocación manual.
- **SC-005**: La interfaz se actualiza en menos de 2 segundos tras una operación exitosa.
- **SC-006**: No existen inconsistencias entre acciones visibles en UI y acciones permitidas por el servidor en 100% de los escenarios.

## Assumptions

- El módulo Liquidacion Asesores utiliza los estados definidos en la entidad: Pendiente, Aprobada, Pagada, Anulada.
- La eliminación es lógica (soft delete) para preservar el historial financiero.
- Los usuarios tienen los permisos RBAC necesarios para ejecutar estas acciones.
- El módulo utiliza PostgreSQL como base de datos.
- La reversión de una liquidación "Anulada" debe devolverla a "Pendiente" con motivo obligatorio (mínimo 10 caracteres).
- La reversión de una liquidación "Pagada" debe devolverla a "Aprobada" (reversión de pago) con motivo obligatorio.
- Las validaciones de integridad referencial deben verificarse antes de ejecutar la operación destructiva.
