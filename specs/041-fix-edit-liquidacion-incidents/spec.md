# Feature Specification: Fix Edit Liquidación Incidents Loading

**Feature Branch**: `[041-fix-edit-liquidacion-incidents]`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "Ingeniería inversa y corrección del flujo de carga de datos del modal Editar Liquidación, donde los campos Incidentes y Observaciones no se recuperan ni muestran correctamente al abrir el modal de edición."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar Incidentes Asociados al Editar una Liquidación (Priority: P1)

Como usuario del sistema (administrador o propietario), quiero que al abrir el modal de edición de una liquidación, los campos "Incidentes" y "Observaciones" se carguen automáticamente con la información previamente almacenada, para poder visualizar y verificar la información asociada a la liquidación.

**Why this priority**: Es un flujo crítico para el negocio, ya que la pérdida de visibilidad de los incidentes asociados genera inconsistencias entre los datos almacenados y la información presentada, afectando la integridad de las liquidaciones y la capacidad de los usuarios para auditar y gestionar cobros adicionales.

**Independent Test**: Can be fully tested by accessing a liquidation with associated incidents in the system, opening the edit modal, and verifying that both the Incidents and Observations fields display the previously stored information.

**Acceptance Scenarios**:

1. **Given** un usuario abre el modal de edición de una liquidación que tiene uno o más incidentes asociados en la base de datos, **When** el modal carga completamente, **Then** el campo "Incidentes" muestra automáticamente todos los incidentes previamente asociados a esa liquidación.
2. **Given** un usuario abre el modal de edición de una liquidación que tiene observaciones almacenadas, **When** el modal carga completamente, **Then** el campo "Observaciones" muestra el contenido previamente registrado.
3. **Given** un usuario tiene una liquidación con múltiples incidentes asociados, **When** abre el modal de edición, **Then** todos los incidentes se visualizan correctamente en el campo correspondiente.
4. **Given** un usuario modifica la información de incidentes u observaciones y guarda los cambios, **When** vuelve a abrir el modal de edición, **Then** la información se muestra correctamente según lo guardado.
5. **Given** una liquidación sin incidentes asociados es editada, **When** se abre el modal, **Then** los campos "Incidentes" y "Observaciones" aparecen vacíos o con un indicador de "Sin incidentes asociados".

---

### Edge Cases

- What happens when la liquidación tiene incidentes asociados pero la consulta SQL o el ORM no devuelve la relación correctamente? El sistema debe mostrar los datos completos sin truncar ni omitir registros.
- How does system handle un error de conexión al cargar los datos del modal? El sistema debe capturar el error y mostrar un toast de notificación con el error y un botón de "Reintentar". El modal permanece abierto para que el usuario pueda reintentar sin perder el contexto.
- What happens when la liquidación tiene un solo incidente asociado? El campo debe mostrar ese único incidente correctamente.
- How does system handle incidentes con diferentes estados (Pendiente, Parcialmente Pagado, Pagado)? Todos los incidentes asociados deben mostrarse independientemente de su estado, ya que la edición es para visualizar lo que ya se persistió.
- What happens when los datos en PostgreSQL están corruptos o incompletos? El sistema debe manejar el error de forma graceful y no crashear.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST recuperar todos los incidentes asociados a una liquidación al abrir el modal de edición, consultando la información completa desde PostgreSQL.
- **FR-002**: El sistema MUST exponer los datos de incidentes y observaciones a través de la API del backend de forma completa y sin transformaciones que pierdan información.
- **FR-003**: El sistema MUST inicializar el estado del formulario del modal de edición con la información recuperada del backend, incluyendo el campo Incidentes y el campo Observaciones.
- **FR-004**: El sistema MUST mostrar automáticamente los incidentes previamente asociados en el campo correspondiente al abrir el modal de edición, sin requerir acción adicional del usuario.
- **FR-005**: El sistema MUST cargar y mostrar el contenido de Observaciones almacenado en la base de datos al abrir el modal de edición.
- **FR-006**: El sistema MUST soportar la visualización correcta tanto de una única liquidación con un solo incidente como de liquidaciones con múltiples incidentes.
- **FR-007**: El sistema MUST preservar la integridad de los datos durante todo el flujo: persistencia en PostgreSQL, exposición por API, consumo en frontend y renderizado en UI.
- **FR-008**: El sistema MUST mantener la funcionalidad existente de creación, edición y gestión de liquidaciones e incidentes sin introducir regresiones.
- **FR-009**: El sistema MUST mostrar un toast de notificación con un botón de "Reintentar" cuando ocurra un error al cargar los datos del modal, manteniendo el modal abierto.
- **FR-010**: El sistema MUST permitir la edición libre de los campos Incidentes y Observaciones en el modal de edición, sin restricciones adicionales más allá de la validación básica de campos.

### Key Entities *(include if feature involves data)*

- **Liquidación**: Registro financiero que agrupa pagos, deducciones y conceptos mensuales de una propiedad. Contiene campos como Observaciones y está vinculada a una propiedad y un periodo específico.
- **Incidente**: Cargo, reparación o eventualidad financiera que debe ser cobrada o descontada en la liquidación. Cada incidente tiene un estado de pago, monto, descripción y está vinculado a una propiedad específica.
- **Relación Liquidación-Incidente**: Asociación que vincula una liquidación con uno o más incidentes. Esta relación debe almacenarse correctamente en PostgreSQL y ser recuperable por el backend.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las liquidaciones con incidentes asociados muestran correctamente la información de incidentes y observaciones al abrir el modal de edición.
- **SC-002**: No existen diferencias entre los datos almacenados en PostgreSQL, los expuestos por el backend y los presentados en la interfaz de usuario.
- **SC-003**: El tiempo de carga del modal de edición con información de incidentes es inferior a 2 segundos en condiciones de red estándar.
- **SC-004**: Las pruebas de regresión confirman que la creación, edición y gestión de liquidaciones e incidentes funciona correctamente sin introducir nuevos defectos.
- **SC-005**: El usuario puede visualizar, consultar y editar la información de incidentes y observaciones en el modal de edición de forma consistente y confiable.

## Clarifications

### Session 2026-07-10

- Q: Alcance de la corrección — ¿limitarse al comportamiento de carga del modal o cubrir toda la tubería de datos? → A: Corregir solo el comportamiento de carga del modal (frontend + consumo de API). Si se encuentran problemas en API/BD, documentarlos como tareas de seguimiento separadas.
- Q: Diferenciación de roles — ¿el modal se comporta igual para todos los roles o hay diferencias de permisos? → A: El modal se comporta igual para todos los roles (sin diferencias de permisos).
- Q: Estados del ciclo de vida — ¿qué estados pueden tener los incidentes y cómo se filtran? → A: Estados de incidente: Pendiente, Parcialmente Pagado, Pagado. El modal muestra todos los estados al editar (solo se filtra al crear nueva liquidación).
- Q: Manejo de errores en la carga — ¿qué ve el usuario cuando falla la carga de datos? → A: Mostrar un toast de notificación con el error y un botón de "Reintentar". El modal permanece abierto.
- Q: Guardado de cambios en incidentes — ¿qué restricciones de validación se aplican al guardar? → A: Edición libre — el modal permite modificar incidentes y observaciones sin restricciones adicionales más allá de la validación básica de campos.

## Out of Scope

- Correcciones en la capa de persistencia (consultas SQL/ORM) que no estén directamente relacionadas con la carga del modal.
- Modificaciones al esquema de la base de datos.
- Cambios en la lógica de negocio de creación o gestión de incidentes.
- Optimizaciones de rendimiento en la API o la base de datos.

## Assumptions

- La base de datos PostgreSQL contiene correctamente la relación entre liquidaciones e incidentes (el problema no está en la persistencia inicial).
- La API backend tiene la capacidad de devolver los incidentes asociados a una liquidación, pero puede haber un mapeo incorrecto o una transformación de datos que esté perdiendo información.
- El componente del modal en Reflex está definido y funcional para otros campos, pero puede tener un error en la inicialización del estado para los campos Incidentes y Observaciones.
- El problema puede estar en múltiples capas: consulta SQL/ORM, mapeo de respuesta API, inicialización de estado en el frontend, o renderizado condicional del componente.
- No se requieren cambios en el esquema de la base de datos, solo en la lógica de recuperación y visualización de datos.
- La solución debe ser compatible con la versión actual de Reflex y con la arquitectura existente del módulo de liquidaciones.
