# Feature Specification: Ingeniería Inversa Estado de Cuenta PDF Individual

**Feature Branch**: `058-reverse-engineer-pdf-statement`

**Created**: 2026-07-16

**Status**: Draft

**Input**: User description: "Realiza una ingeniería inversa sobre el Estado de Cuenta PDF en la vista individual del módulo correspondiente, con un nivel Senior Experto de Élite. Se han identificado inconsistencias en la sección RESUMEN FINANCIERO del documento PDF: 1) El texto descriptivo de los conceptos financieros no se muestra entre paréntesis debajo de algunos conceptos. 2) El porcentaje de comisión del Contrato de Mandato no se está persistiendo ni mostrando correctamente."

## Clarifications

### Session 2026-07-16

- Q: ¿En cuál de estos escenarios se encuentra el problema principal del porcentaje de comisión? → A: Solo renderización: El dato existe correctamente en BD pero no se muestra en el PDF
- Q: ¿Cuál es el formato exacto que debe mostrarse para el concepto "Comisión"? → A: Solo "Comisión (X%)" sin texto descriptivo adicional debajo
- Q: ¿Qué debe mostrar el sistema cuando el porcentaje de comisión no está registrado? → A: "Comisión (0%)" - Valor por defecto numérico
- Q: ¿Cómo debe mostrarse un porcentaje de comisión decimal en el PDF? → A: Redondear al entero más cercano sin decimales
- Q: ¿En qué formato y ubicación debe entregarse la documentación de la ingeniería inversa? → A: En la propia especificación: Actualizar la sección "Reverse Engineering Summary"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validación de Textos Descriptivos en Resumen Financiero (Priority: P1)

Como propietario o administrador, al generar el Estado de Cuenta PDF de una liquidación en la vista individual, necesito que cada concepto financiero en la sección RESUMEN FINANCIERO muestre su texto descriptivo correspondiente entre paréntesis, para comprender claramente el significado de cada cargo o descuento.

**Why this priority**: Los textos descriptivos son esenciales para la transparencia financiera. Sin ellos, el propietario no puede entender qué representa cada concepto, lo que genera confusión y posibles disputas.

**Independent Test**: Se puede probar generando un PDF de una liquidación y verificando que cada concepto financiero muestra su texto descriptivo entre paréntesis.

**Acceptance Scenarios**:

1. **Given** una liquidación completa con todos los conceptos, **When** se genera el Estado de Cuenta PDF en la vista individual, **Then** el concepto "Total Ingresos" muestra el texto "(Total Canon Mandato)" debajo.
2. **Given** una liquidación con comisión al 8%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Comisión" muestra "Comisión (8%)" sin texto descriptivo adicional.
3. **Given** una liquidación con IVA calculado, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "IVA 19%" muestra "(Gravamen sobre la comisión)".
4. **Given** una liquidación de propiedad horizontal, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Administración" muestra "(Solo aplica para propiedad horizontal)".
5. **Given** una liquidación con servicios públicos, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Servicio" muestra "(Solo aplica para Energía, Agua y Gas)".
6. **Given** una liquidación con pago predial, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Predial" muestra "(Pago anual del impuesto predial de la vivienda)".
7. **Given** una liquidación con incidentes, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Incidentes" muestra "(Valor del incidente; aquí se puede presentar el valor total o parcial del mismo)".
8. **Given** cualquier liquidación, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "NETO A PAGAR" NO muestra texto descriptivo adicional.

---

### User Story 2 - Visualización Correcta del Porcentaje de Comisión (Priority: P1)

Como propietario o administrador, al generar el Estado de Cuenta PDF de una liquidación en la vista individual, necesito que el porcentaje de comisión asociado al Contrato de Mandato se muestre correctamente en la sección RESUMEN FINANCIERO, reflejando el valor real registrado en el contrato.

**Why this priority**: El porcentaje de comisión es un dato contractual crítico. Si no se muestra correctamente, el propietario no puede verificar que se le está cobrando la comisión correcta, lo que genera desconfianza y posibles reclamaciones legales.

**Independent Test**: Se puede probar generando un PDF de una liquidación y verificando que el porcentaje de comisión mostrado coincide con el registrado en el Contrato de Mandato asociado.

**Acceptance Scenarios**:

1. **Given** una liquidación con contrato de mandato con comisión al 5%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Comisión" muestra "Comisión (5%)" sin texto descriptivo adicional.
2. **Given** una liquidación con contrato de mandato con comisión al 8%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Comisión" muestra "Comisión (8%)" sin texto descriptivo adicional.
3. **Given** una liquidación con contrato de mandato con comisión al 12%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Comisión" muestra "Comisión (12%)" sin texto descriptivo adicional.
4. **Given** una liquidación con contrato de mandato con comisión al 10%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Comisión" muestra "Comisión (10%)" sin texto descriptivo adicional.
5. **Given** una liquidación sin porcentaje de comisión registrado, **When** se genera el Estado de Cuenta PDF, **Then** el concepto "Comisión" muestra "Comisión (0%)" como valor por defecto.

---

### User Story 3 - Ingeniería Inversa del Flujo de Generación del PDF (Priority: P2)

Como desarrollador Senior Experto de Élite, necesito realizar una ingeniería inversa completa del flujo de generación del Estado de Cuenta PDF en la vista individual, para comprender la estructura actual, el origen de los datos y la lógica de renderización, con el fin de garantizar la corrección de las inconsistencias identificadas.

**Why this priority**: Antes de implementar cualquier corrección, se debe comprender completamente el flujo actual para evitar regresiones y asegurar que las modificaciones sean precisas y completas.

**Independent Test**: Se puede verificar la ingeniería inversa revisando la documentación generada que describe el flujo completo, el origen de datos y la lógica de renderización.

**Acceptance Scenarios**:

1. **Given** el código fuente del sistema, **When** se realiza la ingeniería inversa, **Then** se documenta el flujo completo de generación del PDF desde la vista individual.
2. **Given** la base de datos PostgreSQL, **When** se analiza el esquema, **Then** se identifica el origen de cada campo utilizado en la sección RESUMEN FINANCIERO.
3. **Given** el template del PDF, **When** se examina la lógica de renderización, **Then** se identifica dónde se renderizan los textos descriptivos y el porcentaje de comisión.
4. **Given** el contrato de mandato, **When** se analiza la consulta, **Then** se verifica cómo se obtiene el porcentaje de comisión.
5. **Given** los datos en la base de datos, **When** se comparan con los valores en el PDF, **Then** se identifican inconsistencias específicas en el mapeo de datos.

---

### Edge Cases

- ¿Qué sucede cuando el porcentaje de comisión no está registrado en el contrato de mandato? El sistema debe mostrar un valor por defecto o un mensaje indicando que el porcentaje no está configurado.
- ¿Qué pasa si los textos descriptivos contienen caracteres especiales (tildes, ñ, etc.)? El sistema debe renderizarlos correctamente en el PDF.
- ¿Qué ocurre cuando una liquidación tiene todos los conceptos en cero? El Resumen Financiero muestra todos los conceptos con sus textos descriptivos y el NETO A PAGAR es $0.
- ¿Cómo se comporta el PDF cuando el porcentaje de comisión es un número decimal? Se redondea al entero más cercano sin decimales (ej: 8.5% → 9%, 7.3% → 7%).
- ¿Qué pasa si el contrato de mandato no está asociado a la liquidación? El sistema debe manejar este caso de error adecuadamente.

## Requirements *(mandatory)*

### Functional Requirements

#### Sección: RESUMEN FINANCIERO - Textos Descriptivos

- **FR-001**: El sistema DEBE mostrar el texto descriptivo "(Total Canon Mandato)" debajo del concepto "Total Ingresos" en la sección RESUMEN FINANCIERO.
- **FR-002**: El sistema DEBE mostrar el concepto "Comisión" en el formato "Comisión (X%)" SIN texto descriptivo adicional debajo.
- **FR-003**: El sistema DEBE mostrar el texto descriptivo "(Gravamen sobre la comisión)" debajo del concepto "IVA 19%" en la sección RESUMEN FINANCIERO.
- **FR-004**: El sistema DEBE mostrar el texto descriptivo "(Solo aplica para propiedad horizontal)" debajo del concepto "Administración" en la sección RESUMEN FINANCIERO.
- **FR-005**: El sistema DEBE mostrar el texto descriptivo "(Solo aplica para Energía, Agua y Gas)" debajo del concepto "Servicio" en la sección RESUMEN FINANCIERO.
- **FR-006**: El sistema DEBE mostrar el texto descriptivo "(Pago anual del impuesto predial de la vivienda)" debajo del concepto "Predial" en la sección RESUMEN FINANCIERO.
- **FR-007**: El sistema DEBE mostrar el texto descriptivo "(Valor del incidente; aquí se puede presentar el valor total o parcial del mismo)" debajo del concepto "Incidentes" en la sección RESUMEN FINANCIERO.
- **FR-008**: El concepto "NETO A PAGAR" NO DEBE mostrar ningún texto descriptivo adicional.

#### Sección: RESUMEN FINANCIERO - Porcentaje de Comisión

- **FR-009**: El sistema DEBE obtener el porcentaje de comisión dinámicamente desde el contrato de mandato asociado a la liquidación.
- **FR-010**: El sistema DEBE mostrar el porcentaje de comisión en el formato "Comisión (X%)" donde X es el porcentaje registrado en el contrato.
- **FR-011**: El porcentaje de comisión YA SE ENCUENTRA persistido correctamente en la base de datos (la corrección se enfoca en la renderización, no en la persistencia).
- **FR-012**: El sistema DEBE validar que el porcentaje de comisión sea un número válido antes de mostrarlo en el PDF.
- **FR-013**: Si el porcentaje de comisión no está registrado, el sistema DEBE mostrar "Comisión (0%)" como valor por defecto.

#### Ingeniería Inversa y Validación

- **FR-014**: El sistema DEBE documentar el flujo completo de generación del Estado de Cuenta PDF en la vista individual dentro de la sección "Reverse Engineering Summary" de esta especificación.
- **FR-015**: El sistema DEBE identificar el origen de cada dato utilizado en la sección RESUMEN FINANCIERO.
- **FR-016**: El sistema DEBE verificar la consistencia entre los valores almacenados en la base de datos y los valores presentados en el PDF.
- **FR-017**: El sistema DEBE validar que la consulta utilizada para obtener los datos del contrato de mandato sea correcta y eficiente.
- **FR-018**: El sistema DEBE documentar el proceso de renderización de los textos descriptivos en el PDF.

### Key Entities

- **Liquidacion**: Representa la liquidación mensual de un contrato de mandato para un propietario. Contiene todos los valores financieros (canon, comisión, IVA, gastos, incidentes, neto), el estado de la liquidación, observaciones y metadatos de auditoría.
- **ContratoMandato**: Contrato que establece el canon de mandato y el porcentaje de comisión. Es la fuente del porcentaje de comisión mostrado en el Resumen Financiero.
- **EstadoCuentaPDF**: Documento PDF generado que muestra el estado de cuenta de una liquidación específica, incluyendo la sección RESUMEN FINANCIERO con todos los conceptos financieros.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los textos descriptivos se muestran correctamente en la sección RESUMEN FINANCIERO del PDF.
- **SC-002**: El porcentaje de comisión se muestra correctamente en el 100% de los PDF generados, reflejando el valor registrado en el contrato.
- **SC-003**: La ingeniería inversa completa se documenta con el 100% de los flujos de datos identificados.
- **SC-004**: No existen inconsistencias entre los valores almacenados y los valores presentados en el PDF para la sección RESUMEN FINANCIERO.
- **SC-005**: El tiempo de generación del PDF no se incrementa en más del 10% debido a las validaciones adicionales.
- **SC-006**: Los textos descriptivos se renderizan correctamente con caracteres especiales (tildes, ñ, etc.) en el 100% de los casos.
- **SC-007**: El porcentaje de comisión se obtiene correctamente del contrato de mandato en el 100% de las liquidaciones procesadas.

## Assumptions

- El contrato de mandato ya tiene el porcentaje de comisión persistido correctamente en la base de datos.
- El problema identificado está SOLO en la renderización/mostrado del dato en el PDF, no en la persistencia ni en la consulta SQL.
- Los textos descriptivos están definidos en el template del PDF y no en la base de datos.
- El flujo de generación del PDF en la vista individual es independiente de la generación por lotes.
- La consulta para obtener los datos del contrato de mandato ya existe y es accesible desde el servicio de generación de PDF.
- Los textos descriptivos deben mantenerse consistentes con la documentación existente del sistema.

## Reverse Engineering Summary *(informativo, documentado)*

### Flujo de Generación del PDF (Confirmado)

```
Vista Individual → Generación del PDF
  → ServicioFinanciero.obtener_datos_liquidacion_para_pdf(id)
    → Consulta PostgreSQL (JOIN: liquidaciones + contratos_mandatos + propiedades)
      → El campo `comision_porcentaje_contrato_m` se obtiene en base 10000 (ej: 1000 = 10%)
  → PDFState._transform_individual_to_pdf_format(datos)
    → Construye el diccionario `data["resumen"]` con `comision_porcentaje`
  → EstadoCuentaElite.generate(data)
    → Adición de información consolidada
    → Adición de tabla de propiedades
    → Adición de detalle de propiedades
    → Adición de resumen financiero (`_add_resumen_financiero()`)
      → Se divide `comision_porcentaje / 100` para obtener el porcentaje real a mostrar (ej: 1000/100 = 10)
      → Se configuran los textos descriptivos usando `Paragraph` de ReportLab para la celda "Concepto"
      → Se renderiza la tabla `AdvancedTable`
    → Adición de notas
    → Construcción del documento
```

### Archivos Clave Analizados

| Archivo | Propósito |
|---|---|
| `estado_cuenta_elite.py` | Renderiza la sección RESUMEN FINANCIERO en `_add_resumen_financiero()`. Es el punto exacto de modificación para textos descriptivos y correcciones visuales. |
| `database.py` | Gestor de conexiones PostgreSQL/SQLite que confirma el uso nativo de psycopg2. |
| `contratos_mandatos` (Tabla DB) | Contiene la columna `comision_porcentaje_contrato_m` que guarda el porcentaje en base 10000. |

### Puntos de Verificación (Estado Real)

1. **Origen del dato**: Se obtiene de `comision_porcentaje_contrato_m` en la tabla `contratos_mandatos`.
2. **Formato en BD**: Se almacena en base 10000 (comprobado vía consulta directa: 1000 equivale a 10%).
3. **Persistencia**: La persistencia es correcta y no requiere modificaciones.
4. **Transformación**: La división `/ 100` en `estado_cuenta_elite.py` es matemáticamente correcta para base 10000.
5. **Renderización**: Los textos descriptivos deben implementarse utilizando objetos `Paragraph` de ReportLab en la primera columna ("Concepto") de la tabla de resumen financiero para soportar texto multilínea con estilos diferentes (negrita para el título y normal/pequeño para la descripción).
6. **Consistencia**: El valor de la comisión se muestra redondeado sin decimales (`.0f`), según los requerimientos.