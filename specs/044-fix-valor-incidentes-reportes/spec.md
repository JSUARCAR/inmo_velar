# Feature Specification: Corrección Valor Incidentes en Reportes

**Feature Branch**: `044-fix-valor-incidentes-reportes`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Ingeniería inversa sobre el módulo Reportes para garantizar que el valor almacenado en la columna valor_incidentes de la tabla Liquidaciones sea recuperado, procesado y mostrado correctamente en todos los reportes donde esta información sea funcionalmente relevante, específicamente el Reporte de Liquidaciones y el Reporte Financiero Consolidado."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización de Valor Incidentes en Reporte de Liquidaciones (Priority: P1)

Como usuario del sistema Velar, necesito que el Reporte de Liquidaciones muestre correctamente el valor de incidentes asociados a cada liquidación, para poder tener una visión completa de la información financiera de cada liquidación.

**Why this priority**: Es el reporte individual más utilizado y la omisión de este campo afecta directamente la toma de decisiones operativas sobre cada liquidación.

**Independent Test**: Puede ser probado independientemente generando un Reporte de Liquidaciones para un período específico y verificando que la columna valor_incidentes aparezca con los valores correctos.

**Acceptance Scenarios**:

1. **Given** una liquidación con valor_incidentes = 0, **When** se genera el Reporte de Liquidaciones, **Then** la columna valor_incidentes muestra "$0.00" o el formato monetario equivalente
2. **Given** una liquidación con valor_incidentes = 1500000, **When** se genera el Reporte de Liquidaciones, **Then** la columna valor_incidentes muestra "$1,500,000.00" (formato con separadores de miles y 2 decimales)
3. **Given** una liquidación con múltiples incidentes asociados, **When** se genera el Reporte de Liquidaciones, **Then** la columna valor_incidentes muestra la suma total de todos los incidentes

---

### User Story 2 - Visualización de Valor Incidentes en Reporte Financiero Consolidado (Priority: P1)

Como usuario del sistema Velar, necesito que el Reporte Financiero Consolidado incluya el valor total de incidentes para cada liquidación, para obtener una visión financiera completa que contemple todos los componentes del valor.

**Why this priority**: Este reporte consolidado es used para toma de decisiones ejecutivas y la omisión de este campo genera información financiera incompleta.

**Independent Test**: Puede ser probado generando un Reporte Financiero Consolidado con múltiples liquidaciones y verificando que los valores de incidentes se incorporen correctamente en los totales.

**Acceptance Scenarios**:

1. **Given** múltiples liquidaciones con diferentes valores de incidentes, **When** se genera el Reporte Financiero Consolidado, **Then** cada liquidación muestra su valor_incidentes correspondiente
2. **Given** un período con liquidaciones que tienen incidentes y otras que no, **When** se genera el Reporte Financiero Consolidado, **Then** las liquidaciones sin incidentes muestran valor_incidentes = $0.00
3. **Given** valores de incidentes altos (millones), **When** se genera el Reporte Financiero Consolidado, **Then** los valores se muestran con formato monetario correcto y sin truncamiento

---

### User Story 3 - Consistencia de Formato Monetario (Priority: P2)

Como usuario del sistema Velar, necesito que el formato del valor_incidentes sea consistente con el resto de los campos financieros del sistema, para mantener la coherencia visual y evitar confusiones en la interpretación de datos.

**Why this priority**: La consistencia en el formato es esencial para la usabilidad y previene errores de interpretación por parte de los usuarios.

**Independent Test**: Puede ser probado comparando visualmente el formato de valor_incidentes con otros campos monetarios (valor_administracion, valor_arrendamiento, etc.) en los reportes.

**Acceptance Scenarios**:

1. **Given** un reporte generado, **When** se compara el formato de valor_incidentes con valor_administracion, **Then** ambos usan el mismo formato (separadores de miles, 2 decimales, prefijo de moneda)
2. **Given** un valor con decimales, **When** se muestra en el reporte, **Then** se redondea a 2 decimales consistentemente

---

### Edge Cases

- ¿Qué sucede cuando una liquidación tiene valor_incidentes NULL en la base de datos? El sistema debe tratar NULL como $0.00
- ¿Cómo maneja el sistema valores de incidentes negativos (si existieran por ajustes)? Debe mostrar el valor tal como está almacenado con formato monetario
- ¿Qué sucede si la consulta SQL no retorna la columna valor_incidentes? El sistema debe registrar un error de diagnóstico y mostrar $0.00 como fallback
- ¿Cómo afecta la generación de reportes en formato Excel vs PDF? Ambos formatos deben incluir el campo con el mismo formato
- ¿Qué sucede si falla la conexión a PostgreSQL al generar un reporte? El sistema debe cancelar la generación y mostrar un error claro al usuario (no mostrar datos incompletos)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST recuperar el campo valor_incidentes directamente de la tabla Liquidaciones en PostgreSQL
- **FR-002**: El backend MUST incluir valor_incidentes en el modelo de datos utilizado para generar ambos reportes
- **FR-003**: El Reporte de Liquidaciones MUST mostrar una columna dedicada para valor_incidentes
- **FR-004**: El Reporte Financiero Consolidado MUST incorporar valor_incidentes en la información financiera presentada
- **FR-005**: El sistema MUST formatear valor_incidentes con separadores de miles, 2 decimales y prefijo de moneda
- **FR-006**: El sistema MUST tratar valores NULL como $0.00 en la presentación
- **FR-007**: La incorporación de este campo MUST NO afectar el rendimiento de generación de reportes
- **FR-008**: El sistema MUST mantener la consistencia entre valores almacenados en PostgreSQL y valores mostrados en reportes

### Key Entities

- **Liquidaciones**: Entidad principal que contiene información financiera de períodos de arrendamiento. Incluye campos como valor_administracion, valor_arrendamiento, valor_incidentes (pre-calculado y almacenado), entre otros.
- **Incidentes**: Entidades asociadas a liquidaciones que representan eventos con impacto financiero. Sus valores se suman para calcular valor_incidentes en la liquidación.
- **Reportes**: Generación de documentos (PDF, Excel) que consolidan información financiera para toma de decisiones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las liquidaciones mostradas en reportes incluyen el valor_incidentes correctamente
- **SC-002**: Los valores en reportes coinciden al 100% con los valores almacenados en PostgreSQL
- **SC-003**: El tiempo de generación de reportes no excede 30 segundos (incremento máximo del 5% respecto a la línea base actual)
- **SC-004**: No se reportan errores de formato o presentación del campo valor_incidentes tras la implementación
- **SC-005**: Todos los escenarios de prueba (liquidaciones sin incidentes, con uno, con múltiples, valores altos) pasan exitosamente

## Clarifications

### Session 2026-07-11

- Q: ¿Cómo se obtiene el valor_incidentes para los reportes? → A: Campo pre-calculado en tabla Liquidaciones (ya existe, solo hay que mostrarlo)
- Q: ¿Qué formatos de reporte deben incluir la corrección? → A: Ambos formatos: PDF y Excel
- Q: ¿Qué debe ocurrir si falla la conexión a PostgreSQL al generar un reporte? → A: Cancelar generación y mostrar error al usuario
- Q: ¿Cuál es el tiempo base actual de generación de reportes? → A: 30 segundos como máximo aceptable
- Q: ¿Quiénes deben ver el campo valor_incidentes en los reportes? → A: Todos los usuarios con acceso a reportes

## Assumptions

- La columna valor_incidentes existe y contiene datos válidos en la tabla Liquidaciones de PostgreSQL
- Los usuarios actualmente necesitan esta información y su omisión es un bug, no una decisión de diseño
- El formato monetario actual del sistema (separadores de miles, 2 decimales) es el correcto para este campo
- Los reportes se generan en al menos dos formatos: PDF y Excel
- No se requieren cambios en la estructura de la base de datos (la columna ya existe)
- La lógica de negocio para calcular valor_incidentes ya está implementada correctamente en el dominio
