# Feature Specification: Filtro Estado Pago Incidentes

**Feature Branch**: `[031-filtro-estado-pago-incidentes]`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User description: "Identifico una inconsistencia en la implementación del filtro **Estado de Pago del Incidente** dentro de la sección **Filtros Avanzados** del módulo **Incidentes**. Actualmente, el **ComboBox** únicamente muestra la opción **"Todos"**, cuando debería cargar dinámicamente los estados definidos en la lógica de negocio del sistema..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtrar incidentes por Estado de Pago (Priority: P1)

Como usuario del sistema, quiero poder filtrar la lista de incidentes según su estado de pago, seleccionando entre "Pendiente", "Asociada", "Pagada" o "Todos", para localizar rápidamente los incidentes que requieren atención financiera.

**Why this priority**: Es la funcionalidad principal solicitada, necesaria para gestionar adecuadamente las obligaciones financieras derivadas de los incidentes y auditar pagos pendientes o realizados.

**Independent Test**: Puede ser probado completamente seleccionando cada estado en el desplegable de "Estado de Pago" y verificando que la lista de incidentes desplegada se actualice para mostrar únicamente los registros cuyo estado de pago concuerda con la selección.

**Acceptance Scenarios**:

1. **Given** la lista de incidentes cargada, **When** el usuario selecciona el estado "Pendiente", **Then** la lista muestra únicamente los incidentes cuyo estado de pago es "Pendiente".
2. **Given** la lista de incidentes filtrada por "Pendiente", **When** el usuario selecciona "Todos", **Then** la lista vuelve a mostrar todos los incidentes sin aplicar filtro de pago.
3. **Given** el usuario aplica el filtro "Asociada" junto con un filtro de "Fecha", **Then** el sistema muestra los incidentes que cumplen ambas condiciones de manera combinada.

### Edge Cases

- ¿Qué sucede si no existen incidentes con el estado seleccionado? El sistema debe mostrar el mensaje estándar de "No se encontraron resultados" u "hoja vacía", sin arrojar excepciones.
- ¿Qué sucede si la estructura de `cuota_incidente.py` cambia y añade un nuevo estado en el futuro? El UI debe reflejar el nuevo estado automáticamente, ya que se alimenta de la fuente de verdad.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El filtro "Estado de Pago del Incidente" DEBE cargar dinámicamente sus opciones desde la definición del dominio (`src/dominio/entidades/cuota_incidente.py`), sin depender de listas quemadas en el Frontend.
- **FR-002**: El componente ComboBox DEBE mostrar exactamente las opciones del dominio: "Pendiente", "Asociada", "Pagada", junto a la opción adicional por defecto "Todos".
- **FR-003**: Al seleccionar una opción distinta de "Todos", el sistema DEBE filtrar los registros del frontend y la consulta base de datos para recuperar únicamente incidentes con dicho estado.
- **FR-004**: El estado inicial del filtro DEBE ser "Todos".
- **FR-005**: El filtro de Estado de Pago DEBE funcionar correctamente en combinación con los demás filtros avanzados (ej. fecha, estado de gestión, proveedor, etc.).

### Key Entities

- **CuotaIncidente (Dominio)**: Contiene la definición de los estados válidos (Pendiente, Asociada, Pagada).
- **Incidentes / Filtro de Búsqueda**: La entidad/estado de la vista en la interfaz que mantiene los valores de selección actual para realizar las consultas de filtrado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los estados mostrados en el filtro provienen de la lógica de dominio (Cero valores hardcodeados para estos estados en los componentes UI).
- **SC-002**: Las consultas combinando "Estado de Pago" con al menos un filtro extra devuelven los resultados correctos en el 100% de las pruebas funcionales.
- **SC-003**: El tiempo de resolución y filtrado visual no se degrada perceptiblemente al utilizar la nueva lógica dinámica del combo box.

## Assumptions

- Se asume que el backend ya soporta el filtrado a través de las consultas de repositorios enviándole el estado, y si no, se deberá corregir para soportar este parámetro.
- Se asume que el mapeo entre los valores visualizados y el enumerador del dominio (ej. `.value`) es directo y no requiere transformaciones de idioma.
