# Feature Specification: Reporte de Liquidaciones - Datos del Propietario y Contrato de Mandato

**Feature Branch**: `054-reporte-liquidaciones-datos-propietario`

**Created**: 2026-07-13

**Status**: Draft

**Input**: User description: "Ingeniería inversa del módulo de Reportes para ampliar la información del Reporte de Liquidaciones con datos del Propietario (documento, teléfono) y Contrato de Mandato (banco, cuenta, consignatario)"

## Clarifications

### Session 2026-07-13

- Q: ¿Dónde exactamente deben colocarse las 5 columnas bancarias en relación con las columnas existentes? → A: Después de TELEFONO_PROPIETARIO, agrupando toda la información del propietario y su contrato de mandato junto (nombre, documento, teléfono, banco, cuenta, tipo cuenta, consignatario, documento consignatario)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización de información del propietario en el reporte (Priority: P1)

Como analista financiero, necesito ver el número de documento y teléfono del propietario directamente en el Reporte de Liquidaciones, inmediatamente después de su nombre, para poder contactarlo y verificar su identidad sin necesidad de consultar otros módulos.

**Why this priority**: Esta es la funcionalidad core que elimina la necesidad de navegar entre módulos para obtener información básica del propietario. Impacto directo en la eficiencia operativa diaria.

**Independent Test**: Puede probarse completamente generando el Reporte de Liquidaciones y verificando que las columnas NUMERO_DOCUMENTO_PROPIETARIO y TELEFONO_PROPIETARIO aparecen correctamente después de NOMBRE_PROPIETARIO con datos consistentes.

**Acceptance Scenarios**:

1. **Given** un usuario en el módulo de Reportes, **When** selecciona "Reporte de Liquidaciones" y genera el reporte, **Then** las columnas NUMERO_DOCUMENTO_PROPIETARIO y TELEFONO_PROPIETARIO aparecen inmediatamente después de NOMBRE_PROPIETARIO
2. **Given** un propietario con documento y teléfono registrados en PERSONAS, **When** se genera el reporte, **Then** los valores mostrados coinciden exactamente con los almacenados en la base de datos
3. **Given** un propietario sin número de teléfono registrado, **When** se genera el reporte, **Then** la celda TELEFONO_PROPIETARIO muestra un valor vacío o indicador de "N/A" sin generar error

---

### User Story 2 - Visualización de información bancaria del Contrato de Mandato (Priority: P1)

Como gestor financiero, necesito ver la información bancaria y de consignación del Contrato de Mandato vigente directamente en el Reporte de Liquidaciones para validar que los datos de pago son correctos y están actualizados.

**Why this priority**: La información bancaria es crítica para la validación de pagos y conciliaciones. Tenerla en el reporte elimina riesgos de error en transferencias y facilita la auditoría financiera.

**Independent Test**: Puede probarse generando el reporte y verificando que las 5 columnas bancarias (BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO) muestran los datos del Contrato de Mandato asociado a cada liquidación.

**Acceptance Scenarios**:

1. **Given** una liquidación con Contrato de Mandato que tiene información bancaria completa, **When** se genera el reporte, **Then** las columnas BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO y DOCUMENTO_CONSIGNATARIO muestran los valores correctos
2. **Given** una liquidación con Contrato de Mandato sin información bancaria configurada, **When** se genera el reporte, **Then** las columnas bancarias muestran valores vacíos o "N/A" sin generar error
3. **Given** un propietario con múltiples Contratos de Mandato (uno vigente y otros históricos), **When** se genera el reporte, **Then** se muestra la información bancaria del contrato asociado a cada liquidación específica, no del contrato más reciente

---

### User Story 3 - Exportación del reporte ampliado en todos los formatos (Priority: P2)

Como usuario del sistema, necesito poder exportar el Reporte de Liquidaciones ampliado en todos los formatos soportados (CSV, Excel, PDF) manteniendo la integridad de las nuevas columnas y el formato adecuado para cada tipo de archivo.

**Why this priority**: La exportación es esencial para compartir el reporte con stakeholders externos y para análisis en herramientas como Excel. Sin esta capacidad, el reporte pierde gran parte de su valor operativo.

**Independent Test**: Puede probarse exportando el reporte en CSV y verificando que todas las nuevas columnas aparecen con el formato correcto (números de cuenta sin truncamiento, documentos con formato adecuado).

**Acceptance Scenarios**:

1. **Given** el reporte ampliado con las nuevas columnas, **When** el usuario exporta a CSV, **Then** el archivo contiene todas las columnas incluidas las nuevas, con valores sin truncamiento
2. **Given** el reporte ampliado, **When** el usuario exporta a Excel, **Then** las columnas aparecen con el ancho adecuado y los números de cuenta/documento no se pierden por formato
3. **Given** el reporte ampliado, **When** el usuario exporta a PDF, **Then** el documento incluye todas las columnas de forma legible sin cortes ni superposiciones

---

### User Story 4 - Consistencia de datos entre reporte y base de datos (Priority: P2)

Como auditor, necesito poder verificar que la información mostrada en el Reporte de Liquidaciones es idéntica a la almacenada en PostgreSQL, garantizando la trazabilidad y confiabilidad de los datos presentados.

**Why this priority**: La confiabilidad de los datos es fundamental para auditorías y decisiones financieras. Cualquier inconsistencia entre el reporte y la base de datos generaría riesgos operativos y de cumplimiento.

**Independent Test**: Puede probarse comparando manualmente los valores de 5 registros arbitrarios entre el reporte exportado y las consultas directas a la base de datos.

**Acceptance Scenarios**:

1. **Given** registros en la base de datos con datos del propietario y contrato de mandato, **When** se genera el reporte, **Then** cada valor mostrado coincide exactamente con el valor almacenado en PostgreSQL
2. **Given** datos actualizados en la base de datos, **When** se regenera el reporte inmediatamente después, **Then** los valores reflejan el estado actual de los datos (no datos缓存 obsoletos)
3. **Given** múltiples liquidaciones para el mismo propietario, **When** se compara la información del propietario entre registros, **Then** los datos de documento y teléfono son consistentes en todos los registros

---

### Edge Cases

- ¿Qué sucede cuando un propietario tiene múltiples Contratos de Mandato con diferentes información bancaria? El reporte debe mostrar la información del contrato específico asociado a cada liquidación, no la del contrato más reciente.
- ¿Cómo maneja el sistema propietarios sin número de teléfono registrado? La celda debe mostrar un valor vacío o "N/A" sin generar errores de renderizado.
- ¿Qué ocurre si un Contrato de Mandato tiene información bancaria parcial (ej. banco sin número de cuenta)? Las columnas individuales deben mostrarse según su disponibilidad, sin agrupar valores faltantes.
- ¿Cómo se comporta el reporte cuando hay liquidaciones con Contratos de Mandato de diferentes estados (vigente, vencido, cancelado)? Se muestra la información del contrato asociado a cada liquidación independientemente de su estado.
- ¿Qué sucede al exportar a CSV con números de cuenta que comienzan con ceros? Los números deben preservarse completos sin truncamiento por parte de Excel.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST agregar las columnas NUMERO_DOCUMENTO_PROPIETARIO y TELEFONO_PROPIETARIO inmediatamente después de NOMBRE_PROPIETARIO en el Reporte de Liquidaciones
- **FR-002**: El sistema MUST agregar las columnas BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO y DOCUMENTO_CONSIGNATARIO al Reporte de Liquidaciones
- **FR-003**: El sistema MUST obtener los datos del propietario desde la entidad PERSONAS a través de la relación PROPIETARIOS -> PERSONAS
- **FR-004**: El sistema MUST obtener la información bancaria desde la entidad CONTRATOS_MANDATOS asociada a cada liquidación
- **FR-005**: El sistema MUST mantener la posición de las nuevas columnas agrupadas junto a la información del propietario: después de NOMBRE_PROPIETARIO se colocan NUMERO_DOCUMENTO_PROPIETARIO, TELEFONO_PROPIETARIO, BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO
- **FR-006**: El sistema MUST preservar la funcionalidad de exportación CSV con las nuevas columnas, incluyendo sanitización de valores para prevenir truncamiento en Excel
- **FR-007**: El sistema MUST mostrar valores vacíos o "N/A" cuando los datos opcionales no estén configurados
- **FR-008**: El sistema MUST mantener la consistencia de datos mostrados vs almacenados en PostgreSQL
- **FR-009**: El sistema MUST soportar la visualización de información bancaria de Contratos de Mandato en cualquier estado (vigente, vencido, cancelado)
- **FR-010**: El sistema MUST preservar el ordenamiento, filtrado y paginación existentes del reporte

### Key Entities

- **Liquidacion**: Representa un registro financiero mensual de una propiedad. Se vincula a un Contrato de Mandato específico. Contiene todos los datos de ingresos, egresos y estado de liquidación.
- **ContratoMandato**: Acuerdo entre el propietario y la inmobiliaria para la administración de una propiedad. Contiene la información bancaria del propietario para consignación de pagos.
- **Propietario**: Persona propietaria de una propiedad. Se vincula a una Persona para datos de identificación y contacto.
- **Persona**: Entidad que almacena datos de identificación (documento, nombre, teléfono, correo) de propietarios, arrendatarios y asesores.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El Reporte de Liquidaciones incluye 7 nuevas columnas (NUMERO_DOCUMENTO_PROPIETARIO, TELEFONO_PROPIETARIO, BANCO, NUMERO_CUENTA, TIPO_CUENTA, NOMBRE_CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO) sin afectar las 28 columnas existentes
- **SC-002**: El tiempo de generación del reporte no increase más del 10% con respecto al tiempo base actual
- **SC-003**: El 100% de los registros del reporte muestra datos consistentes con la base de datos PostgreSQL
- **SC-004**: La exportación a CSV preserva números de cuenta y documentos sin truncamiento (100% de integridad de datos)
- **SC-005**: No se presentan regresiones funcionales en otros reportes del módulo de Reportes
- **SC-006**: El reporte se genera correctamente en todos los formatos soportados (CSV, Excel, PDF)

## Assumptions

- La información bancaria del propietario está almacenada en la entidad CONTRATOS_MANDATOS (campos: banco_propietario, numero_cuenta_propietario, tipo_cuenta, consignatario, documento_consignatario)
- La información de identificación y contacto del propietario está en la entidad PERSONAS (campos: numero_documento, telefono_principal)
- Las relaciones existentes LIQUIDACIONES -> CONTRATOS_MANDATOS -> PROPIETARIOS -> PERSONAS ya están implementadas y funcionando correctamente
- El número de teléfono del propietario es un campo opcional en la entidad PERSONAS
- La información bancaria en CONTRATOS_MANDATOS puede estar parcialmente configurada (algunos campos vacíos)
- El rendimiento actual del reporte es aceptable y las nuevas columnas no requerirán optimización adicional de queries
- Los formatos de exportación actuales (CSV, Excel, PDF) soportan la adición de columnas sin modificaciones estructurales significativas
- El orden de las columnas es: NOMBRE_PROPIETARIO → NUMERO_DOCUMENTO_PROPIETARIO → TELEFONO_PROPIETARIO → BANCO → NUMERO_CUENTA → TIPO_CUENTA → NOMBRE_CONSIGNATARIO → DOCUMENTO_CONSIGNATARIO (toda la información del propietario y su contrato de mandato agrupada)
