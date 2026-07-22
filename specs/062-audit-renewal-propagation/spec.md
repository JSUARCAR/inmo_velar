# Feature Specification: Auditoría de Propagación de Renovaciones

**Feature Branch**: `062-audit-renewal-propagation`

**Created**: 2026-07-22

**Status**: Clarified

**Input**: User description: "Auditoría profunda sobre los Contratos de Arrendamiento que fueron renovados o actualizados durante el período de julio 2026, con el objetivo de identificar inconsistencias en la propagación de los cambios hacia los módulos de Liquidación de Propietarios y Recaudos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identificar Inconsistencias de Canon (Priority: P1)

Como auditor del sistema, necesito identificar todos los contratos de arrendamiento renovados en julio 2026 donde el canon actualizado no se haya propagado correctamente a los módulos de Liquidación de Propietarios y Recaudos, para garantizar la integridad financiera del sistema.

**Why this priority**: Es el objetivo principal de la auditoría. Sin esta identificación, no es posible corregir inconsistencias ni garantizar la precisión de los datos financieros.

**Independent Test**: Puede probarse ejecutando el script de auditoría contra la base de datos y verificando que se identifican todas las inconsistencias conocidas.

**Acceptance Scenarios**:

1. **Given** contratos de arrendamiento renovados en julio 2026, **When** se ejecuta la auditoría, **Then** se identifican todos los contratos con discrepancias entre el canon vigente y el utilizado en liquidaciones o recaudos.
2. **Given** una inconsistencia encontrada, **When** se analiza, **Then** se determina la causa raíz específica (liquidación generada antes de renovación, recaudo no actualizado, etc.).
3. **Given** múltiples contratos renovados, **When** se procesan, **Then** cada contrato tiene su estado de sincronización documentado (OK/INCONSISTENTE).

---

### User Story 2 - Generar Informe Estructurado (Priority: P1)

Como administrador del sistema, necesito un informe JSON detallado que contenga métricas, inconsistencias específicas, análisis de código y recomendaciones técnicas, para tomar decisiones informadas sobre correcciones.

**Why this priority**: El informe estructurado es el entregable principal que permite la toma de decisiones y el seguimiento de las correcciones.

**Independent Test**: Puede probarse ejecutando el script y verificando que el JSON generado contiene todas las secciones requeridas con datos válidos.

**Acceptance Scenarios**:

1. **Given** la ejecución completa de la auditoría, **When** se genera el informe, **Then** contiene metadatos, resumen ejecutivo, detalles de inconsistencias, análisis de código y recomendaciones.
2. **Given** el informe JSON, **When** se valida, **Then** cumple con el esquema definido y todos los campos obligatorios están presentes.
3. **Given** el informe, **When** se revisa el resumen, **Then** muestra métricas claras: total renovaciones, inconsistencias encontradas, estado de sincronización.

---

### User Story 3 - Analizar Fallas de Diseño (Priority: P2)

Como desarrollador del sistema, necesito identificar fallas específicas en la lógica de sincronización y propagación de datos entre módulos, para proponer mejoras técnicas que prevengan futuras inconsistencias.

**Why this priority**: El análisis de código permite implementar mejoras estructurales que previenen la recurrencia del problema.

**Independent Test**: Puede probarse revisando la sección de análisis del informe y verificando que identifica fallas reales en el código fuente.

**Acceptance Scenarios**:

1. **Given** el código fuente del sistema, **When** se analiza automáticamente, **Then** se identifican puntos de falla específicos en la cascada de sincronización.
2. **Given** las fallas encontradas, **When** se documentan, **Then** se proporcionan ubicaciones exactas (archivos y líneas) y descripciones claras del problema.
3. **Given** el análisis completado, **When** se revisa, **Then** se identifican al menos 3 problemas de diseño específicos.

---

### User Story 4 - Preservación de Históricos (Priority: P2)

Como auditor del sistema, necesito verificar que los registros históricos de liquidaciones y recaudos anteriores a las renovaciones no hayan sido modificados, para garantizar la trazabilidad financiera.

**Why this priority**: La preservación de datos históricos es crítica para auditorías fiscales y regulatorias.

**Independent Test**: Puede probarse verificando que liquidaciones y recaudos de períodos anteriores a julio 2026 mantienen sus valores originales.

**Acceptance Scenarios**:

1. **Given** liquidaciones generadas antes de julio 2026, **When** se comparan con los valores originales, **Then** no muestran modificaciones.
2. **Given** recaudos de períodos anteriores a la renovación, **When** se validan, **Then** conservan el valor_total original.
3. **Given** el historial de cambios, **When** se analiza, **Then** no existen actualizaciones retroactivas sobre registros financieros.

---

### Edge Cases

- ¿Qué sucede si un contrato fue renovado múltiples veces en julio 2026? → Se audita solo la última renovación del mes (A10)
- ¿Cómo maneja el script contratos sin mandato asociado? → Se marca como ERROR y se omite de la comparación
- ¿Qué occurre si la base de datos no contiene renovaciones en julio 2026? → Se genera informe vacío con total_renovaciones=0
- ¿Cómo se procesan liquidaciones o recaudos en estado "Cancelada" o "Reversado"? → Se excluyen de la comparación
- ¿Qué sucede si hay errores de conexión a la base de datos durante la ejecución? → Se captura el error y se registra en el informe

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El script MUST conectarse a PostgreSQL utilizando la variable de entorno `DATABASE_URL`
- **FR-002**: El script MUST ejecutar únicamente consultas SQL de solo lectura (sin INSERT, UPDATE, DELETE)
- **FR-003**: El script MUST identificar todas las renovaciones de contratos de arrendamiento registradas en julio 2026
- **FR-004**: El script MUST comparar el canon arrendamiento vigente contra el utilizado en liquidaciones para períodos desde la fecha actual en adelante
- **FR-005**: El script MUST comparar el canon arrendamiento vigente contra el utilizado en recaudos para períodos desde la fecha actual en adelante
- **FR-006**: El script MUST verificar la sincronización del canon entre contratos de arrendamiento, mandatos y propiedades
- **FR-007**: El script MUST validar que los registros históricos anteriores a julio 2026 no fueron alterados
- **FR-008**: El script MUST analizar el código fuente para identificar fallas en la lógica de sincronización
- **FR-009**: El script MUST generar un archivo JSON con la estructura definida
- **FR-010**: El informe JSON MUST incluir metadatos de ejecución (fecha, duración, total procesado)
- **FR-011**: El informe JSON MUST incluir un resumen ejecutivo con métricas clave
- **FR-012**: El informe JSON MUST detallar cada inconsistencia encontrada con causa raíz
- **FR-013**: El informe JSON MUST incluir análisis de código con ubicaciones específicas de fallas
- **FR-014**: El informe JSON MUST proporcionar recomendaciones técnicas priorizadas
- **FR-015**: El script MUST manejar errores de conexión y consultas gracefulmente

### Key Entities

- **ContratoArrendamiento**: Contrato de alquiler entre inmobiliaria y arrendatario. Campo clave: `canon_arrendamiento`
- **RenovacionContrato**: Registro histórico de renovaciones con valores anterior y nuevo. Campos: `canon_anterior`, `canon_nuevo`, `fecha_renovacion`
- **ContratoMandato**: Contrato entre propietario e inmobiliaria. Campo clave: `canon_mandato`
- **Propiedad**: Inmueble administrado. Campo clave: `canon_arrendamiento_estimado`
- **Liquidacion**: Estado de cuenta mensual del propietario. Campo clave: `canon_bruto`
- **Recaudo**: Pago recibido del inquilino. Campo clave: `valor_total`
- **RecaudoConcepto**: Concepto específico del pago (Canon, Administración, etc.). Campo clave: `valor`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las renovaciones de julio 2026 son identificadas y procesadas por el script
- **SC-002**: El informe JSON se genera en menos de 30 segundos con datos completos
- **SC-003**: 100% de las inconsistencias identificadas incluyen causa raíz específica
- **SC-004**: El análisis de código identifica al menos 3 fallas de diseño en la sincronización
- **SC-005**: Se proporcionan recomendaciones técnicas específicas para cada falla encontrada
- **SC-006**: El informe contiene datos precisos que pueden ser usados para planificar correcciones
- **SC-007**: El script se ejecuta sin errores en el entorno de staging/producción
- **SC-008**: El JSON resultante es válido y puede ser procesado por herramientas de análisis
- **SC-009**: El archivo JSON se guarda correctamente en `scripts/diagnostico/` con nombre basado en timestamp
- **SC-010**: Contratos con múltiples renovaciones en julio 2026 son procesados correctamente (solo última)

## Assumptions

- La base de datos PostgreSQL está accesible mediante la variable de entorno `DATABASE_URL`
- Los datos de renovaciones de julio 2026 están disponibles en la tabla `RENOVACIONES_CONTRATOS`
- El script se ejecuta en un entorno con acceso al código fuente para análisis (filesystem access)
- Las consultas SQL son compatibles con PostgreSQL 12+
- Los nombres de tablas y columnas siguen la convención de mayúsculas utilizada en el sistema
- El script puede acceder a los archivos Python del proyecto para análisis de código
- Los datos de prueba en staging son representativos del comportamiento en producción
- Se audita solo la última renovación de julio 2026 por contrato (no renovaciones múltiples)
- Los períodos "futuros" se definen desde la fecha actual en adelante
- El informe se guarda como archivo local en `scripts/diagnostico/`

## Aclaraciones

### A1 - Formato del Entregable
**Decisión**: Script Python que genera archivo JSON con informe estructurado.
**Justificación**: JSON es ampliamente soportado por herramientas de análisis y permite procesamiento automatizado.

### A2 - Alcance Temporal
**Decisión**: Solo se auditan renovaciones registradas entre el 1 y 31 de julio de 2026.
**Justificación**: El usuario especificó específicamente julio 2026 como período de interés.

### A3 - Tipo de Operación
**Decisión**: El script es de solo lectura; no realiza modificaciones a la base de datos.
**Justificación**: Una auditoría debe ser no intrusiva para preservar la integridad de los datos.

### A4 - Análisis de Código
**Decisión**: El script incluye análisis estático del código fuente para identificar fallas de diseño.
**Justificación**: Permite identificar la causa raíz系统ica de las inconsistencias, no solo los síntomas.

### A5 - Causa Raíz
**Decisión**: El script determina automáticamente la causa raíz de cada inconsistencia.
**Justificación**: Facilita la priorización y planificación de correcciones.

### A6 - Alcance Temporal de Comparación
**Decisión**: "Períodos futuros" se define como períodos desde la fecha actual (hoy) en adelante.
**Justificación**: Permite identificar inconsistencias activas que afectan la operación actual, no solo históricas.

### A7 - Análisis de Código Fuente
**Decisión**: El script tiene acceso al filesystem del proyecto para analizar archivos Python (.py) del dominio de persistencia y servicios.
**Justificación**: El análisis estático es esencial para identificar fallas de diseño en la cascada de sincronización.

### A8 - Estructura del JSON
**Decisión**: La estructura del JSON queda flexible para que el implementador la diseñe según los requerimientos funcionales.
**Justificación**: Permite mayor libertad en la implementación manteniendo los campos obligatorios definidos en FR.

### A9 - Destino del Informe
**Decisión**: El JSON se guarda como archivo local en `scripts/diagnostico/` con nombre basado en timestamp.
**Justificación**: Centraliza los diagnósticos en un solo lugar del proyecto para fácil acceso.

### A10 - Renovaciones Múltiples
**Decisión**: Si un contrato fue renovado múltiples veces en julio 2026, se audita solo la última renovación del mes (estado final).
**Justificación**: El objetivo es auditar el estado actual del sistema, no reconstruir historiales parciales.

---

## Decision Log

| # | Fecha | Decisión | Pregunta |
|---|-------|----------|----------|
| D1 | 2026-07-22 | Períodos futuros = desde hoy | ¿Alcance temporal de comparación? |
| D2 | 2026-07-22 | Incluir filesystem access | ¿Análisis de código incluido? |
| D3 | 2026-07-22 | Estructura JSON flexible | ¿Definir schema ahora? |
| D4 | 2026-07-22 | Archivo local en scripts/diagnostico/ | ¿Dónde guardar el JSON? |
| D5 | 2026-07-22 | Solo última renovación del mes | ¿Cómo manejar múltiples renovaciones? |
