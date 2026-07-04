# Feature Specification: debug-incident-selection

**Feature Branch**: `[010-debug-incident-selection]`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de **ingeniería inversa y validación funcional de nivel Senior/Principal** sobre el módulo **Liquidaciones de Propietarios**, ya que durante las pruebas identifiqué una inconsistencia en la funcionalidad de selección de incidentes.
Actualmente observo que, al editar una liquidación, **el botón "Seleccionar Incidentes" ya se visualiza correctamente**, lo que indica que parte de la implementación ya fue desplegada. Sin embargo, al hacer clic sobre dicho botón **no se abre el modal de selección de incidentes**, por lo que no es posible asociar uno o varios incidentes a la liquidación..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Diagnosticar y Reparar el Modal de Selección de Incidentes (Priority: P1)

Como usuario del sistema (administrador o propietario), quiero que al hacer clic en el botón "Seleccionar Incidentes" dentro del formulario de edición de una liquidación, se abra correctamente el modal de selección, para poder visualizar y asociar los incidentes pendientes de pago a dicha liquidación.

**Why this priority**: Es un flujo crítico para el negocio, ya que impide asociar cobros o descuentos adicionales (incidentes) en la liquidación de los propietarios, bloqueando la correcta facturación y liquidación del periodo.

**Independent Test**: Can be fully tested by entering the liquidation module in production, editing a liquidation, clicking the "Seleccionar Incidentes" button, and confirming the modal opens and lists correct incidents.

**Acceptance Scenarios**:

1. **Given** un usuario está en la vista de edición de una liquidación en el módulo de Liquidaciones de Propietarios, **When** hace clic en el botón "Seleccionar Incidentes", **Then** un modal se abre mostrando la lista de incidentes disponibles para asociar.
2. **Given** que el modal de selección de incidentes se ha abierto, **When** se consultan los incidentes disponibles, **Then** el sistema muestra únicamente aquellos incidentes cuyo estado de pago sea diferente de "Pagado".

---

### Edge Cases

- What happens when la liquidación no tiene incidentes pendientes en la base de datos? El modal debe abrirse pero mostrar un mensaje de "No hay incidentes pendientes disponibles".
- How does system handle un error de conexión al hacer clic en el botón? El sistema debe capturar el error y mostrar un toast o mensaje indicando que no se pudo cargar la lista.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST abrir el modal de selección de incidentes al hacer clic en el botón "Seleccionar Incidentes" dentro de la vista de edición de liquidación.
- **FR-002**: El sistema MUST consultar el backend para recuperar los incidentes vinculados a la propiedad/contrato actual.
- **FR-003**: El sistema MUST filtrar los incidentes devueltos para mostrar únicamente aquellos cuyo Estado de Pago no sea "Pagado".
- **FR-004**: El sistema MUST prevenir cualquier regla de renderizado condicional errónea en el frontend que esté ocultando o bloqueando la visualización del modal.
- **FR-005**: El sistema MUST mostrar un indicador de carga mientras se obtienen los incidentes del backend.

### Key Entities *(include if feature involves data)*

- **Liquidación**: Registro financiero que agrupa pagos, deducciones y conceptos mensuales de una propiedad.
- **Incidente**: Cargo, reparación o eventualidad financiera que debe ser cobrada o descontada en la liquidación, y cuyo estado dicta su elegibilidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los clics en el botón "Seleccionar Incidentes" resultan en la apertura del modal sin errores de consola (asumiendo conexión normal).
- **SC-002**: El modal de incidentes muestra únicamente los registros que cumplen la regla de negocio (Estado distinto a "Pagado").
- **SC-003**: El tiempo de apertura del modal y la carga de datos es inferior a 2 segundos en condiciones de red estándar.

## Assumptions

- La API backend para consultar incidentes ya existe y tiene la capacidad de filtrar por estado, o la lógica de negocio aplicará el filtro correctamente en el backend.
- El componente del modal en Reflex está definido, pero puede haber un error de estado (`rx.State`) o una variable de visibilidad (`is_open`) que no se está mutando correctamente.
- El problema está aislado en el componente de UI o en el manejador del evento de clic, y no es un fallo catastrófico del servicio completo.
