# Feature Specification: bugfix-liquidaciones-incidentes

**Feature Branch**: `[###-bugfix-liquidaciones-incidentes]`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "Realiza un proceso de ingeniería inversa clínica y exhaustiva sobre el módulo de Liquidaciones, enfocado en identificar la causa raíz de una posible regresión funcional..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Diagnóstico y Visualización de Incidentes en Edición de Liquidación (Priority: P1)

Como administrador del sistema o liquidador, quiero visualizar correctamente los incidentes asociados a una liquidación cuando accedo al modal de edición, para poder conocer y gestionar el valor deducido o sumado correspondiente a dichos incidentes.

**Why this priority**: Es el core de la regresión funcional reportada; la invisibilidad de los incidentes en el modal de edición impide a los usuarios validar la composición del valor de la liquidación y ocasiona confusión operativa.

**Independent Test**: Can be fully tested by abriendo una liquidación existente que posea incidentes asociados y verificando que el modal de edición liste el incidente con su respectivo valor y que permita visualizar el detalle completo de este mediante el botón correspondiente.

**Acceptance Scenarios**:

1. **Given** una liquidación que tiene uno o más incidentes registrados en base de datos con un valor asociado, **When** el usuario hace clic en el botón o acción para editar dicha liquidación, **Then** el modal de edición debe renderizar correctamente la lista de incidentes y el valor asociado sin omitir información.
2. **Given** que el usuario se encuentra visualizando la sección de incidentes dentro de la edición de la liquidación, **When** hace clic en la opción para ver el detalle de los incidentes, **Then** el sistema debe abrir exitosamente el modal secundario con los detalles del incidente sin errores de UI o bloqueos.

### Edge Cases

- ¿Qué sucede si la liquidación no tiene incidentes asociados? El sistema debe mostrar un mensaje claro de que no hay incidentes.
- ¿Qué pasa si el valor de los incidentes supera el valor de la liquidación? El sistema debe seguir mostrando la lista y reflejar la información total verazmente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST recuperar correctamente los incidentes asociados a una liquidación desde la base de datos, asegurando que las relaciones traigan los registros esperados.
- **FR-002**: El sistema MUST cargar y mapear apropiadamente la información de los incidentes consultados al estado del Frontend, sin pérdida de datos en el paso de backend a cliente.
- **FR-003**: El componente visual del modal de edición MUST recibir y renderizar la información cargada en el estado, iterando sobre los incidentes para mostrarlos en la UI.
- **FR-004**: El evento encargado de abrir el modal de detalles de incidentes MUST estar activable y responder al clic del usuario mostrando la información en una nueva ventana/modal.
- **FR-005**: La corrección MUST atacar la causa raíz (datos, estado o UI), y no generar efectos colaterales en la lógica de creación o guardado de incidentes o liquidaciones.

### Key Entities *(include if feature involves data)*

- **Liquidacion**: Registro principal que agrupa el valor a pagar o deducir, e incluye una colección de incidentes.
- **Incidente**: Registro asociado a una liquidación que representa cobros o deducciones adicionales con un valor específico.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las liquidaciones que tienen incidentes en base de datos muestran dichos incidentes visiblemente en el modal de edición en la interfaz de usuario.
- **SC-002**: El clic sobre la opción de ver detalles de incidentes abre el modal secundario exitosamente el 100% de las veces en un entorno de pruebas, sin bloqueos ni errores silenciosos.
- **SC-003**: El flujo de edición y guardado de una liquidación (con y sin incidentes) se completa con un 100% de éxito, garantizando la ausencia de regresiones.

## Assumptions

- Los datos históricos en la base de datos de producción/pruebas sobre la propiedad reportada no están corruptos; el problema radica en la extracción, mapeo o presentación visual.
- El problema reportado es consistente y reproducible para todas las liquidaciones que poseen incidentes (o en un subconjunto claro de casos), no un fallo aleatorio de red.
