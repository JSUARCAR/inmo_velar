# Feature Specification: Fix Estado Cuenta PDF - Incidentes

**Feature Branch**: `051-fix-estado-cuenta-pdf-incidentes`

**Created**: 2026-07-12

**Status**: Draft

**Input**: User description: "Ingeniería inversa del módulo Liquidaciones para validar que el proceso de generación del Estado de Cuenta PDF incluya correctamente el valor correspondiente a Incidentes, tanto en el detalle de la liquidación como en todos los cálculos financieros que intervienen en el documento."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización de Incidentes en Estado de Cuenta PDF (Priority: P1)

Como propietario de una propiedad que tiene incidentes asociados a una liquidación, necesito que al descargar mi Estado de Cuenta en PDF, el valor correspondiente a incidentes aparezca claramente en el detalle de la liquidación y sea parte de los cálculos financieros del documento, para poder verificar la integridad de la información financiera que me es presentada.

**Why this priority**: Es la funcionalidad core que resuelve el problema reportado. Sin ella, el documento PDF no refleja la información completa de la liquidación, generando desconfianza en los propietarios y potenciales disputas financieras.

**Independent Test**: Puede probarse completamente generando un Estado de Cuenta PDF para una liquidación con incidentes asociados y verificando que el valor aparece en el detalle y afecta el Neto a Pagar.

**Acceptance Scenarios**:

1. **Given** una liquidación con un incidente asociado por valor de $500.000, **When** se genera el Estado de Cuenta PDF, **Then** el documento muestra el valor de Incidentes como línea separada en el detalle y el Neto a Pagar refleja la deducción.
2. **Given** una liquidación con múltiples incidentes asociados por valores de $200.000, $300.000 y $500.000, **When** se genera el Estado de Cuenta PDF, **Then** el documento muestra el total de Incidentes como $1.000.000 en el detalle y el Neto a Pagar refleja la deducción completa.
3. **Given** una liquidación con incidentes cuyos valores son elevados (superiores a $10.000.000), **When** se genera el Estado de Cuenta PDF, **Then** los valores se formatean correctamente con separadores de miles y el Neto a Pagar se calcula sin errores de precisión.

---

### User Story 2 - Consistencia entre UI y PDF (Priority: P2)

Como administrador del sistema, necesito que los valores mostrados en la interfaz del módulo Liquidaciones (tabla de detalle, modal de edición) coincidan exactamente con los valores reflejados en el Estado de Cuenta PDF, para garantizar la consistencia de la información presentada al propietario.

**Why this priority**: La inconsistencia entre UI y PDF es un problema de integridad de datos que afecta la confiabilidad del sistema. Los propietarios pueden comparar la información visualizada en la plataforma con el documento descargado.

**Independent Test**: Puede probarse comparando los valores visuales en la UI de liquidaciones con los valores generados en el PDF para la misma liquidación.

**Acceptance Scenarios**:

1. **Given** una liquidación visible en la tabla de liquidaciones con un valor de incidentes de $750.000, **When** se descarga el Estado de Cuenta PDF, **Then** el valor de Incidentes en el PDF coincide exactamente con el valor mostrado en la UI.
2. **Given** una liquidación con valor_incidentes = 0 (sin incidentes), **When** se genera el Estado de Cuenta PDF, **Then** el documento no muestra línea de Incidentes o la muestra con valor $0, y el Neto a Pagar no se ve afectado.
3. **Given** una liquidación aprobada con incidentes pendientes de pago, **When** se compara el neto_a_pagar de la UI con el del PDF, **Then** ambos valores son idénticos.

---

### User Story 3 - Regresión y Robustez (Priority: P3)

Como desarrollador del sistema, necesito que la incorporación del valor de Incidentes en el PDF no afecte la generación de otros documentos PDF ni introduzca regresiones funcionales en el módulo de Liquidaciones, para mantener la estabilidad del sistema.

**Why this priority**: Garantiza que la corrección no genere nuevos problemas. La estabilidad del sistema es fundamental para la confianza del usuario.

**Independent Test**: Puede probarse ejecutando la generación de todos los tipos de PDF del sistema (Estado de Cuenta, contratos, reportes) y verificando que no hay errores ni cambios inesperados.

**Acceptance Scenarios**:

1. **Given** el sistema con la corrección implementada, **When** se generan Estados de Cuenta para liquidaciones sin incidentes, **Then** el PDF se genera correctamente sin errores.
2. **Given** el sistema con la corrección implementada, **When** se generan otros tipos de documentos PDF (contratos, reportes), **Then** se generan correctamente sin afectación.
3. **Given** el sistema con la corrección implementada, **When** se ejecutan las pruebas de regresión del módulo de liquidaciones, **Then** todas las pruebas pasan exitosamente.

---

### Edge Cases

- ¿Qué sucede cuando una liquidación tiene incidentes asociados pero con valor_incidentes = 0 en la base de datos?
- ¿Cómo maneja el sistema liquidaciones con valores de incidentes en decimales (aunque el tipo sea INTEGER, ¿hay conversión)?
- ¿Qué ocurre cuando se genera un PDF en lote (ZIP) y algunas liquidaciones tienen incidentes y otras no?
- ¿Cómo se comporta el formato de moneda para valores de incidentes muy grandes (superiores a $999.999.999)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El proceso de generación del Estado de Cuenta PDF MUST recuperar el campo `valor_incidentes` directamente desde la consulta SQL que obtiene los datos de la liquidación.
- **FR-002**: La plantilla del Estado de Cuenta PDF MUST incluir una línea o sección dedicada para mostrar el valor de Incidentes en el detalle de la liquidación.
- **FR-003**: El cálculo del Neto a Pagar en el PDF MUST incluir la deducción del valor de Incidentes, siendo consistente con el cálculo `neto_a_pagar = total_ingresos - total_egresos - valor_incidentes`.
- **FR-004**: El valor de Incidentes MUST formatearse como moneda colombiana (separadores de miles, sin decimales) de forma consistente con los demás valores monetarios del documento.
- **FR-005**: Cuando el valor de Incidentes sea cero, el PDF MUST ocultar la línea de Incidentes o mostrarla con valor $0 sin afectar el cálculo del Neto a Pagar.
- **FR-006**: El Resumen Financiero del PDF MUST incluir el valor de Incidentes como concepto deducible, mostrando su impacto en el Valor Neto.
- **FR-007**: La generación del PDF en lote (ZIP) MUST incluir el valor de Incidentes en cada Estado de Cuenta individual.
- **FR-008**: Los valores mostrados en el PDF MUST coincidir exactamente con los valores almacenados en PostgreSQL para la liquidación correspondiente.
- **FR-009**: La solución MUST mantener la consistencia entre la información visualizada en la UI del módulo Liquidaciones y la presentada en el PDF.
- **FR-010**: La implementación MUST preservar la funcionalidad existente de generación de PDF sin introducir regresiones.

### Key Entities

- **Liquidación**: Representación mensual de la cuenta del propietario. Contiene campos financieros como `total_ingresos`, `total_egresos`, `valor_incidentes`, `neto_a_pagar`. Relacionada con contratos, propiedades e incidentes.
- **Incidente**: Evento reportado en una propiedad (daño, mantención, etc.) con un valor económico. Puede tener un plan de pago asociado.
- **Incidente-Liquidación**: Tabla de unión que asocia cuotas de incidentes con liquidaciones específicas, registrando el valor de descuento aplicado.
- **Estado de Cuenta PDF**: Documento generado en formato PDF que resume la información financiera de una liquidación para un propietario en un período específico.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los Estados de Cuenta PDF generados para liquidaciones con incidentes muestran correctamente el valor de Incidentes en el detalle.
- **SC-002**: El Neto a Pagar en el PDF coincide exactamente con el neto_a_pagar almacenado en PostgreSQL para el 100% de las liquidaciones generadas.
- **SC-003**: No existen diferencias entre los valores mostrados en la UI del módulo Liquidaciones y los reflejados en el Estado de Cuenta PDF (tolerancia: $0).
- **SC-004**: La generación de PDF no introduce regresiones en otros documentos del sistema (0 errores en pruebas de regresión).
- **SC-005**: El tiempo de generación del PDF no se incrementa en más del 5% respecto al tiempo actual.

## Assumptions

- El campo `valor_incidentes` ya existe en la tabla LIQUIDACIONES y está correctamente poblado por la lógica de negocio existente.
- La consulta SQL `obtener_datos_para_pdf()` ya retorna el campo `valor_incidentes` pero puede no estar siendo utilizado en la plantilla.
- La lógica de cálculo `neto_a_pagar = total_ingresos - total_egresos - valor_incidentes` en la entidad Liquidación es la fuente de verdad para el cálculo financiero.
- El formato de moneda colombiana (separadores de miles, sin decimales) es el estándar para todos los valores monetarios en el PDF.
- La plantilla actual del Estado de Cuenta PDF utiliza ReportLab y está definida en `estado_cuenta_elite.py`.
- El mapeo de datos para PDF en `servicio_financiero.py` (`mapear_consolidado_a_pdf_elite`) es el punto donde se preparan los datos para la plantilla.
- Los escenarios de prueba deben cubrir al menos: liquidaciones sin incidentes, con un único incidente, con múltiples incidentes, y con valores elevados.
