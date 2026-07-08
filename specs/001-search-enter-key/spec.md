# Feature Specification: Búsqueda con Tecla ENTER

**Feature Branch**: `001-search-enter-key`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Implementar ejecución de búsqueda con tecla ENTER en input Buscar, consistente en módulos: Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos e Incidentes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Búsqueda con ENTER en módulo individual (Priority: P1)

Un usuario ingresa un término de búsqueda en el campo "Buscar" de cualquier módulo y presiona la tecla ENTER. El sistema ejecuta automáticamente la búsqueda, produciendo exactamente el mismo resultado que si hubiera hecho clic en el botón "Buscar".

**Why this priority**: Es la funcionalidad core del feature. Sin ella, no hay valor entregado. Representa el MVP completo: un solo módulo con búsqueda por tecla.

**Independent Test**: Puede probarse ingresando un término en el input "Buscar" de cualquier módulo, presionando ENTER, y verificando que se ejecuta la búsqueda con los mismos resultados que el botón.

**Acceptance Scenarios**:

1. **Given** el usuario está en la página de Personas con el campo "Buscar" vacío, **When** escribe "Juan" y presiona ENTER, **Then** se ejecuta la búsqueda y se muestran los resultados filtrados por "Juan".
2. **Given** el usuario tiene filtros avanzados activos (ej. estado "Activo"), **When** escribe "María" en "Buscar" y presiona ENTER, **Then** la búsqueda se ejecuta combinando el término "María" con el filtro avanzado "Activo".
3. **Given** el usuario está en la página de Propiedades, **When** presiona ENTER sin haber ingresado ningún término, **Then** la búsqueda se ejecuta igualmente (mostrando todos los registros o aplicando solo los filtros avanzados).
4. **Given** el usuario presiona ENTER repetidamente de forma rápida, **When** se ejecuta la primera búsqueda, **Then** las pulsaciones subsecuentes no generan búsquedas duplicadas ni sobrecarga el sistema.

---

### User Story 2 - Consistencia transversal en todos los módulos (Priority: P2)

El comportamiento de búsqueda con tecla ENTER funciona de manera idéntica en los 7 módulos del sistema: Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos e Incidentes.

**Why this priority**: La consistencia es crítica para la experiencia de usuario. Un usuario que aprende a buscar con ENTER en un módulo espera el mismo comportamiento en todos los demás.

**Independent Test**: Puede probarse navegando a cada uno de los 7 módulos, ingresando un término y presionando ENTER, verificando que la búsqueda se ejecuta correctamente en cada uno.

**Acceptance Scenarios**:

1. **Given** el usuario está en el módulo de Contratos, **When** escribe "001" en "Buscar" y presiona ENTER, **Then** se ejecuta la búsqueda con los mismos resultados que el botón "Buscar".
2. **Given** el usuario está en el módulo de Liquidaciones, **When** escribe un criterio y presiona ENTER, **Then** la búsqueda se ejecuta y respeta los filtros avanzados seleccionados.
3. **Given** el usuario está en el módulo de Liquidación de Asesores, **When** presiona ENTER en "Buscar", **Then** la búsqueda se ejecuta con la misma lógica del botón.
4. **Given** el usuario está en el módulo de Recaudos, **When** ingresa un término y presiona ENTER, **Then** la búsqueda se ejecuta correctamente.
5. **Given** el usuario está en el módulo de Incidentes, **When** ingresa un término y presiona ENTER, **Then** la búsqueda se ejecuta correctamente.

---

### User Story 3 - Compatibilidad con filtros avanzados (Priority: P3)

La búsqueda con tecla ENTER respeta y combina correctamente con todos los filtros avanzados activos al momento de ejecutarse.

**Why this priority**: Asegura que la búsqueda por tecla no cree un flujo paralelo sino que reutilice la lógica existente, incluyendo filtros avanzados.

**Independent Test**: Puede probarse activando filtros avanzados en cualquier módulo, ingresando un término en "Buscar", presionando ENTER, y verificando que los resultados reflejan tanto el término como los filtros.

**Acceptance Scenarios**:

1. **Given** el usuario tiene filtros avanzados de fecha y estado activos, **When** escribe "test" en "Buscar" y presiona ENTER, **Then** los resultados incluyen solo registros que cumplen con el término "test" Y los filtros de fecha y estado.
2. **Given** el usuario tiene un filtro avanzado de tipo "Propiedad" activo, **When** presiona ENTER sin ingresar término, **Then** se muestran todos los registros que cumplen con el filtro avanzado.

---

### Edge Cases

- ¿Qué sucede cuando el usuario presiona ENTER con el campo "Buscar" vacío? → Se ejecuta la búsqueda con criterio vacío (misma lógica que el botón).
- ¿Cómo maneja el sistema pulsaciones repetidas rapidas de ENTER? → Se previene la ejecución múltiple; solo se ejecuta una búsqueda.
- ¿Qué sucede si el usuario presiona ENTER mientras una búsqueda anterior aún está cargando? → Se espera a que termine o se cancela la anterior (comportamiento estándar del botón).
- ¿Qué sucede si el sistema detecta un error de validación al presionar ENTER? → Se muestra el mismo error que mostraría el botón "Buscar".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST detectar la pulsación de la tecla ENTER en el campo de entrada "Buscar" y ejecutar la búsqueda asociada.
- **FR-002**: La búsqueda ejecutada por ENTER MUST producir exactamente el mismo resultado que la búsqueda ejecutada por clic en el botón "Buscar".
- **FR-003**: El comportamiento MUST ser consistente en los 7 módulos: Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos e Incidentes.
- **FR-004**: La búsqueda por ENTER MUST respetar y combinar con todos los filtros avanzados activos al momento de la ejecución.
- **FR-005**: El sistema MUST prevenir ejecuciones múltiples cuando el usuario presiona ENTER de forma repetitiva o mantiene la tecla presionada.
- **FR-006**: La implementación MUST reutilizar la lógica existente del botón "Buscar", sin duplicar código ni crear flujos paralelos.
- **FR-007**: La búsqueda por ENTER MUST funcionar correctamente tanto con términos de búsqueda como sin ellos (campo vacío).

### Key Entities

- **Campo de Búsqueda (Input Buscar)**: Componente de entrada de texto presente en la cabecera de cada módulo. Acepta criterios de búsqueda libres (nombre, documento, número, etc.).
- **Botón Buscar**: Componente existente que ejecuta la búsqueda al hacer clic. La funcionalidad ENTER debe reutilizar exactamente esta lógica.
- **Filtros Avanzados**: Controles de filtrado adicionales disponibles en cada módulo que se combinan con el criterio de búsqueda.
- **Módulos del Sistema**: Las 7 secciones funcionales (Personas, Propiedades, Contratos, Liquidaciones, Liquidación de Asesores, Recaudos, Incidentes) que contienen el componente de búsqueda.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los módulos indicados permite ejecutar la búsqueda presionando ENTER.
- **SC-002**: Los resultados de búsqueda por ENTER son idénticos a los del botón "Buscar" en el 100% de los casos de prueba.
- **SC-003**: No se producen búsquedas duplicadas en pruebas de pulsación repetida (0% de ejecuciones múltiples no intencionales).
- **SC-004**: La funcionalidad opera correctamente con filtros avanzados activos (100% de compatibilidad).
- **SC-005**: No se reportan regresiones funcionales en el comportamiento existente del botón "Buscar".

## Assumptions

- El campo "Buscar" es un componente Reflex (`rx.input`) estandarizado presente en todos los módulos indicados.
- El botón "Buscar" ya tiene una lógica de búsqueda implementada y funcional en todos los módulos.
- Los módulos comparten una arquitectura de UI consistente (patrón de componente repetido).
- La tecla ENTER no tiene actualmente ningún handler asignado en el campo "Buscar".
- No se requieren cambios en el backend; la lógica de búsqueda existente es suficiente.
- El sistema utiliza el framework Reflex para la interfaz de usuario.
