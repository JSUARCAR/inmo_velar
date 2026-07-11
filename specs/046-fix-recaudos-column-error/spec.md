# Feature Specification: Fix Recaudos Column Name Error

**Feature Branch**: `bugfix/046-fix-recaudos-column-error`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Diagnosticar y corregir el error 'column fecha_inicio does not exist' que aparece al cargar la pagina de Recaudos - Pagos de Arrendatarios"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carga exitosa de la pagina de Recaudos (Priority: P1)

Como usuario del sistema de gestion inmobiliaria, necesito que la pagina "Recaudos - Pagos de Arrendatarios" cargue correctamente para poder visualizar y gestionar los pagos recibidos de los contratos de arrendamiento.

**Why this priority**: Es la funcionalidad core de la pagina. Sin carga exitosa, la pagina es completamente inutilizable.

**Independent Test**: Puede ser probada independentemente navegando a la pagina de Recaudos y verificando que no aparece ningun mensaje de error y que la tabla muestra registros.

**Acceptance Scenarios**:

1. **Given** el usuario esta autenticado en el sistema, **When** navega a la pagina "Recaudos - Pagos de Arrendatarios", **Then** la pagina carga sin errores y muestra la tabla de recaudos
2. **Given** existen recaudos registrados en la base de datos, **When** la pagina carga exitosamente, **Then** la tabla muestra los registros con sus columnas: ID, Fecha Pago, Pago Contrato, Ciclo Operativo, Propiedad, Arrendatario, Habitante, Valor, Metodo, Estado, Acciones
3. **Given** la pagina carga con error actualmente, **When** se aplica la correccion, **Then** el mensaje de error "column fecha_inicio does not exist" ya no aparece

---

### User Story 2 - Paginacion funcional de recaudos (Priority: P1)

Como usuario, necesito que la paginacion de la tabla de recaudos funcione correctamente para poder navegar entre los registros cuando hay muchos pagos registrados.

**Why this priority**: La paginacion depende del conteo total de registros, que tambien falla por el mismo error de columna. Ambas funcionalidades se corrigen con el mismo cambio.

**Independent Test**: Puede ser probada verificando que el contador "Mostrando X-Y de Z" muestra valores correctos y que los botones Anterior/Siguiente funcionan.

**Acceptance Scenarios**:

1. **Given** existen mas de 20 recaudos registrados, **When** el usuario carga la pagina, **Then** el contador muestra el total real de registros (ej: "Mostrando 1-20 de 45")
2. **Given** el usuario esta en la primera pagina, **When** observa los controles de paginacion, **Then** el boton "Anterior" esta deshabilitado y "Siguiente" esta habilitado
3. **Given** el usuario esta en la ultima pagina, **When** observa los controles de paginacion, **Then** el boton "Siguiente" esta deshabilitado

---

### User Story 3 - Filtrado de recaudos (Priority: P2)

Como usuario, necesito poder filtrar los recaudos por estado, fechas y texto de busqueda para encontrar pagos especificos rapidamente.

**Why this priority**: Los filtros son una funcionalidad importante pero la pagina ya tiene los componentes de filtro implementados; solo necesitan funcionar con la consulta corregida.

**Independent Test**: Puede ser probada aplicando filtros y verificando que la tabla se actualiza con los resultados correctos.

**Acceptance Scenarios**:

1. **Given** el usuario esta en la pagina de recaudos, **When** selecciona un estado especifico en el filtro "Estado", **Then** la tabla solo muestra recaudos con ese estado
2. **Given** el usuario ingresa fechas en los campos "Desde" y "Hasta", **When** aplica el filtro, **Then** la tabla solo muestra recaudos dentro del rango de fechas
3. **Given** el usuario escribe un termino en el campo "Buscar", **When** presiona Enter o hace clic en buscar, **Then** la tabla muestra recaudos que coinciden con el termino en propiedad, arrendatario o matricula

---

### Edge Cases

- Que sucede cuando no existen recaudos registrados en la base de datos? -> La tabla debe mostrar un mensaje indicando "No se encontraron recaudos" o similar, sin errores
- Que sucede cuando el contrato de mandato asociado a una propiedad esta inactivo? -> El campo "Ciclo Operativo" debe mostrar un valor por defecto o vacio, sin errores
- Que sucede cuando un recaudo no tiene contrato de mandato activo asociado? -> El LEFT JOIN lateral debe retornar NULL para GRUPO_OPERATIVO, y la interfaz debe manejar ese caso

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load the "Recaudos - Pagos de Arrendatarios" page without database errors
- **FR-002**: System MUST correctly query the CONTRATOS_MANDATOS table using the actual column name FECHA_INICIO_CONTRATO_M instead of the non-existent FECHA_INICIO
- **FR-003**: System MUST display the total count of recaudos matching current filters for accurate pagination
- **FR-004**: System MUST maintain existing filter functionality (search, status, date range) after the fix
- **FR-005**: System MUST display the GRUPO_OPERATIVO field correctly for each recaudo row

### Key Entities

- **Recaudo**: Represents a payment received from a tenant. Key attributes: ID, payment date, amount, payment method, status, associated contract
- **ContratoMandato**: Represents a management contract between the company and a property owner. Key attributes: start date (FECHA_INICIO_CONTRATO_M), operational group, status
- **ContratoArrendamiento**: Represents a lease agreement between the company and a tenant. Links recaudos to properties and tenants

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The page "Recaudos - Pagos de Arrendatarios" loads without errors 100% of the time
- **SC-002**: The pagination counter displays accurate totals matching the database record count
- **SC-003**: Filter operations (search, status, date range) return correct results within 2 seconds
- **SC-004**: The GRUPO_OPERATIVO column displays correctly for all recaudo rows that have an active management contract
- **SC-005**: Zero database errors related to column references in the recaudos module

## Assumptions

- The database schema is correct and the column FECHA_INICIO_CONTRATO_M exists in the CONTRATOS_MANDATOS table
- The error is isolated to two SQL queries in the recaudos repository (lines 405 and 615)
- No other queries in the system reference the non-existent FECHA_INICIO column on CONTRATOS_MANDATOS
- The fix is a straightforward column name correction with no side effects on other functionality
- The existing test infrastructure can validate the fix through manual UI testing
