# Feature Specification: fix-filtro-pago-contrato

**Feature Branch**: `[###-feature-name]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Quiero que realices un proceso de ingeniería inversa de nivel Senior/Principal sobre el filtro avanzado Pago Contrato del módulo Recaudos, ya que identifiqué una inconsistencia entre la información utilizada por el filtro y los datos que realmente se muestran en la tabla. Actualmente, el filtro Pago Contrato no está utilizando el criterio correcto. El valor que se muestra en la tabla corresponde al día de inicio del contrato, cuando debería utilizar el día de pago del contrato, que es el dato que representa el criterio funcional esperado para este filtro."

## Clarifications

### Session 2026-07-05
- Q: ¿Cómo debe comportarse el filtro "Pago Contrato" si el registro del contrato no tiene un día de pago asignado? → A: Utilizar el "día de inicio" como respaldo (fallback) si el día de pago está vacío.

## User Scenarios & Testing *(mandatory)*


### User Story 1 - Filtrar Recaudos por Día de Pago del Contrato (Priority: P1)

Como usuario del módulo de Recaudos, quiero poder utilizar el filtro avanzado "Pago Contrato" basándome en el "día de pago del contrato" real y no en el "día de inicio del contrato", para poder buscar y visualizar los datos correctamente según las reglas de negocio establecidas.

**Why this priority**: Es un error funcional crítico que impide la correcta operación y búsqueda de datos en el módulo de Recaudos, afectando la operatividad del sistema.

**Independent Test**: Can be fully tested by applying the "Pago Contrato" filter and verifying that the displayed records in the table match the exact payment day (día de pago) and not the start day (día de inicio).

**Acceptance Scenarios**:

1. **Given** un conjunto de recaudos con contratos que tienen días de inicio y días de pago distintos, **When** aplico el filtro "Pago Contrato" seleccionando un día específico, **Then** la tabla debe mostrar únicamente los registros cuyo "día de pago del contrato" coincida con el valor filtrado.
2. **Given** el módulo de Recaudos con registros filtrados por "Pago Contrato", **When** reviso la columna correspondiente en la tabla de resultados, **Then** el valor mostrado debe ser el "día de pago del contrato" (y no el día de inicio).

---

### Edge Cases

- **Contratos sin día de pago definido**: Si un contrato no tiene el día de pago asignado en la base de datos, el sistema debe utilizar el "día de inicio del contrato" como respaldo (fallback) para las búsquedas del filtro "Pago Contrato".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El filtro avanzado "Pago Contrato" MUST basar su criterio de búsqueda en el campo correspondiente al "día de pago del contrato" en el backend y la base de datos.
- **FR-002**: La columna o dato visualizado en la tabla de Recaudos referente al "Pago Contrato" MUST reflejar el "día de pago del contrato" (y no el día de inicio).
- **FR-003**: La consulta de datos a la base de datos PostgreSQL MUST estar alineada con este criterio, utilizando las columnas correctas en la tabla/vista subyacente.
- **FR-004**: Los cambios realizados MUST NO afectar otros filtros ni el comportamiento general del módulo de Recaudos.

### Key Entities *(include if feature involves data)*

- **Recaudo**: Registro principal que se lista en la tabla.
- **Contrato**: Entidad asociada al recaudo, de la cual se debe extraer el "día de pago" en lugar del "día de inicio".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los resultados filtrados por "Pago Contrato" coinciden exactamente con el "día de pago" registrado en la base de datos.
- **SC-002**: La tabla de resultados muestra el campo de "día de pago" correctamente para todos los registros.
- **SC-003**: Pruebas de regresión ejecutadas sobre el módulo de Recaudos no muestran degradación o errores en otras funcionalidades.

## Assumptions

- Existe una diferenciación clara a nivel de esquema de base de datos entre "día de inicio del contrato" y "día de pago del contrato".
- El cambio afecta principalmente consultas de solo lectura (filtros y visualización) y no modifica la estructura fundamental de la base de datos ni los procesos de creación de contratos.
