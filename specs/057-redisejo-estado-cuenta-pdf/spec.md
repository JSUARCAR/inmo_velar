# Feature Specification: Rediseño Estado de Cuenta PDF Liquidaciones

**Feature Branch**: `057-redisejo-estado-cuenta-pdf`

**Created**: 2026-07-15

**Status**: Draft

**Input**: User description: "Ingeniería inversa y rediseño del Estado de Cuenta PDF (vista individual) del módulo de Liquidaciones de Propietarios, incluyendo columna de Incidentes, reordenamiento del Resumen Financiero, eliminación del Código QR, incorporación de sección de Observaciones, y garantía de consistencia entre BD y PDF."

## Clarifications

### Session 2026-07-15

- Q: ¿Cómo se determina si una propiedad es de Propiedad Horizontal para decidir si mostrar el concepto de Administración? → A: Por gastos_administracion > 0. Si es mayor a 0, se muestra; si es 0, se muestra $0.
- Q: ¿La eliminación del Código QR aplica únicamente al Estado de Cuenta o a todos los tipos de documento PDF? → A: Solo Estado de Cuenta. La generación por lotes (ZIP) hereda el cambio automáticamente ya que usa el mismo template.
- Q: ¿Qué comportamiento debe tener la sección OBSERVACIONES cuando el campo observaciones está vacío, es null o contiene solo IDs de incidentes? → A: Mostrar siempre la sección. Si está vacía, se muestra con contenido vacío o un mensaje indicando que no hay observaciones.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización de Incidentes en el Detalle Financiero (Priority: P1)

Como propietario o administrador, al generar el Estado de Cuenta PDF de una liquidación que contiene incidentes asociados, necesito que la columna INCIDENTES aparezca explícitamente en la tabla de detalle financiero, mostrando el valor exacto registrado en la base de datos, para poder verificar la trazabilidad del cálculo del NETO A PAGAR.

**Why this priority**: Es el cambio central de la funcionalidad. La ausencia de esta columna genera inconsistencias visuales y dificulta la auditoría financiera. Sin ella, el propietario no puede ver de dónde proviene el descuento por incidentes.

**Independent Test**: Se puede probar generando un PDF de una liquidación con incidentes asociados y verificando que la columna INCIDENTES aparece con el valor correcto.

**Acceptance Scenarios**:

1. **Given** una liquidación con `valor_incidentes = 50000`, **When** se genera el Estado de Cuenta PDF, **Then** la columna INCIDENTES muestra `$50.000` en la fila correspondiente de la tabla de detalle financiero.
2. **Given** una liquidación con `valor_incidentes = 0`, **When** se genera el Estado de Cuenta PDF, **Then** la columna INCIDENTES muestra `$0` (o el comportamiento definido por la lógica del sistema para ceros).
3. **Given** una liquidación con `valor_incidentes > 0`, **When** se genera el Estado de Cuenta PDF, **Then** la columna INCIDENTES aparece siempre, independientemente del valor.
4. **Given** una liquidación con múltiples propiedades asociadas, **When** se genera el Estado de Cuenta PDF, **Then** cada propiedad muestra su propio valor de incidentes en la columna INCIDENTES.
5. **Given** una liquidación con `valor_incidentes` persistido en PostgreSQL, **When** se compara el valor en el PDF con el de la BD, **Then** los valores coinciden exactamente.

---

### User Story 2 - Eliminación de la Fila TOTAL del Detalle Financiero (Priority: P1)

Como propietario o administrador, al revisar el Estado de Cuenta PDF, necesito que la fila denominada TOTAL no aparezca en la tabla de detalle financiero, ya que genera redundancia con el Resumen Financiero y no aporta valor funcional adicional.

**Why this priority**: La fila TOTAL es redundante con la sección de resumen y genera confusión visual. Su eliminación simplifica la lectura del documento.

**Independent Test**: Se puede probar generando cualquier PDF y verificando que la fila TOTAL no aparece en la tabla de detalle financiero.

**Acceptance Scenarios**:

1. **Given** cualquier liquidación, **When** se genera el Estado de Cuenta PDF, **Then** la fila TOTAL no se renderiza en la tabla de detalle financiero.
2. **Given** una liquidación con múltiples propiedades, **When** se genera el Estado de Cuenta PDF, **Then** no existe fila TOTAL al final de la tabla de detalle.
3. **Given** una liquidación consolidada con múltiples contratos, **When** se genera el Estado de Cuenta PDF, **Then** la tabla de detalle solo muestra filas por propiedad, sin fila TOTAL.

---

### User Story 3 - Reorganización del Resumen Financiero (Priority: P1)

Como propietario o administrador, al revisar el Estado de Cuenta PDF, necesito que el Resumen Financiero muestre los conceptos en un orden lógico y claro: Total Ingresos, Comisión (con porcentaje), IVA 19%, Administración, Servicios, Predial, Incidentes y NETO A PAGAR, para comprender fácilmente la estructura de costos.

**Why this priority**: El orden actual del resumen no sigue una lógica financiera intuitiva. El reordenamiento mejora la comprensión del documento.

**Independent Test**: Se puede probar generando un PDF y verificando que el Resumen Financiero muestra los conceptos en el orden especificado.

**Acceptance Scenarios**:

1. **Given** una liquidación completa con todos los conceptos, **When** se genera el Estado de Cuenta PDF, **Then** el Resumen Financiero muestra los conceptos en este orden: Total Ingresos → Comisión (X%) → IVA 19% → Administración → Servicios → Predial → Incidentes → NETO A PAGAR.
2. **Given** una liquidación con comisión al 8%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto de Comisión muestra `Comisión (8%)`.
3. **Given** una liquidación con comisión al 12%, **When** se genera el Estado de Cuenta PDF, **Then** el concepto de Comisión muestra `Comisión (12%)`.
4. **Given** una liquidación de propiedad horizontal con gastos de administración, **When** se genera el Estado de Cuenta PDF, **Then** el concepto Administración muestra el valor correspondiente.
5. **Given** una liquidación sin gastos de administración (no es propiedad horizontal), **When** se genera el Estado de Cuenta PDF, **Then** el concepto Administración muestra `$0`.
6. **Given** una liquidación con servicios públicos (energía, agua, gas), **When** se genera el Estado de Cuenta PDF, **Then** el concepto Servicios muestra el total de servicios registrados.
7. **Given** una liquidación sin servicios públicos, **When** se genera el Estado de Cuenta PDF, **Then** el concepto Servicios muestra `$0`.
8. **Given** una liquidación con pago predial, **When** se genera el Estado de Cuenta PDF, **Then** el concepto Predial muestra el valor registrado.
9. **Given** una liquidación sin pago predial, **When** se genera el Estado de Cuenta PDF, **Then** el concepto Predial muestra `$0`.
10. **Given** una liquidación con valor_incidentes > 0, **When** se genera el Estado de Cuenta PDF, **Then** el concepto Incidentes muestra el valor registrado.
11. **Given** una liquidación con valor_incidentes = 0, **When** se genera el Estado de Cuenta PDF, **Then** el concepto Incidentes muestra `$0`.
12. **Given** cualquier liquidación, **When** se genera el Estado de Cuenta PDF, **Then** el NETO A PAGAR se calcula manteniendo la fórmula actual: `total_ingresos - total_egresos - valor_incidentes`.

---

### User Story 4 - Eliminación del Código QR (Priority: P2)

Como propietario o administrador, al generar el Estado de Cuenta PDF, necesito que el Código QR no aparezca en el documento, ya que no se requiere verificación vía QR para este tipo de documento.

**Why this priority**: La eliminación del QR simplifica el layout del encabezado y evita espacios en blanco innecesarios.

**Independent Test**: Se puede probar generando un PDF y verificando que no existe ningún elemento QR ni espacio reservado para él.

**Acceptance Scenarios**:

1. **Given** cualquier liquidación, **When** se genera el Estado de Cuenta PDF, **Then** no se renderiza ningún Código QR en el documento.
2. **Given** cualquier liquidación, **When** se genera el Estado de Cuenta PDF, **Then** el encabezado del documento se redistribuye sin espacios en blanco residuales donde estaba el QR.
3. **Given** cualquier liquidación, **When** se genera el Estado de Cuenta PDF, **Then** el resto del documento se renderiza correctamente sin afectaciones por la eliminación del QR.

---

### User Story 5 - Sección de Observaciones en el PDF (Priority: P2)

Como propietario o administrador, al generar el Estado de Cuenta PDF de una liquidación que contiene observaciones registradas, necesito que dichas observaciones aparezcan en una sección dedicada del documento, para tener visibilidad completa de las notas asociadas a la liquidación.

**Why this priority**: Las observaciones son información relevante que se registra al momento de generar o editar la liquidación. Su ausencia en el PDF genera pérdida de contexto.

**Independent Test**: Se puede probar generando un PDF de una liquidación con observaciones y verificando que la sección OBSERVACIONES muestra el contenido completo.

**Acceptance Scenarios**:

1. **Given** una liquidación con observaciones de texto largo, **When** se genera el Estado de Cuenta PDF, **Then** la sección OBSERVACIONES muestra el contenido completo con saltos de línea correctos.
2. **Given** una liquidación sin observaciones, **When** se genera el Estado de Cuenta PDF, **Then** la sección OBSERVACIONES se renderiza con contenido vacío o un mensaje indicando que no hay observaciones.
3. **Given** una liquidación con observaciones que contienen IDs de incidentes (formato "Inc #123"), **When** se genera el Estado de Cuenta PDF, **Then** las observaciones se muestran completas sin truncamiento.
4. **Given** una liquidación con observaciones de longitud variable, **When** se genera el Estado de Cuenta PDF, **Then** el diseño del PDF se adapta correctamente al contenido sin afectar el layout del resto del documento.
5. **Given** una liquidación con observaciones persistidas en PostgreSQL, **When** se compara el contenido del PDF con el de la BD, **Then** los textos coinciden exactamente.

---

### Edge Cases

- ¿Qué sucede cuando una liquidación tiene `valor_incidentes > 0` pero la propiedad no es horizontal? El valor de incidentes se muestra independientemente del tipo de propiedad.
- ¿Qué pasa si las observaciones contienen caracteres especiales (tildes, ñ, etc.)? El sistema debe renderizarlos correctamente.
- ¿Qué ocurre si una liquidación tiene todos los conceptos en cero? El Resumen Financiero muestra todos los conceptos con `$0` y el NETO A PAGAR es `$0`.
- ¿Cómo se comporta el PDF cuando una liquidación tiene un valor negativo en algún concepto? Se muestra con el signo correspondiente según la lógica actual del sistema.
- ¿Qué pasa si el porcentaje de comisión no está registrado en el contrato? Se muestra el valor por defecto definido por el sistema.

## Requirements *(mandatory)*

### Functional Requirements

#### Sección: DETALLE FINANCIERO

- **FR-001**: El sistema DEBE incluir una columna denominada INCIDENTES en la tabla de detalle financiero del PDF.
- **FR-002**: La columna INCIDENTES DEBE mostrar el valor almacenado en el campo `valor_incidentes` de la liquidación correspondiente.
- **FR-003**: Si la liquidación no posee incidentes (`valor_incidentes = 0`), la columna INCIDENTES DEBE mostrar `$0`.
- **FR-004**: La columna INCIDENTES DEBE mostrarse para todas las liquidaciones, independientemente de si el valor es cero o mayor a cero.
- **FR-005**: El sistema DEBE eliminar completamente la fila denominada TOTAL de la tabla de detalle financiero.
- **FR-006**: La fila TOTAL NO DEBE ser renderizada en ninguna circunstancia, ni para liquidaciones individuales ni consolidadas.
- **FR-007**: El valor mostrado en la columna INCIDENTES DEBE corresponder exactamente al valor persistido en PostgreSQL.

#### Sección: RESUMEN FINANCIERO

- **FR-008**: El sistema DEBE reorganizar el Resumen Financiero en el siguiente orden: Total Ingresos → Comisión (X%) → IVA 19% → Administración → Servicios → Predial → Incidentes → NETO A PAGAR.
- **FR-009**: Total Ingresos DEBE corresponder al valor total del Canon de Mandato registrado en la liquidación (`total_ingresos`).
- **FR-010**: Comisión DEBE mostrar el porcentaje obtenido dinámicamente desde el campo `comision_porcentaje` del contrato, formateado como `Comisión (X%)`.
- **FR-011**: IVA 19% DEBE corresponder exclusivamente al gravamen aplicado sobre el valor de la comisión (`iva_comision`).
- **FR-012**: Administración DEBE mostrarse cuando `gastos_administracion > 0` (propiedad horizontal). Cuando `gastos_administracion = 0`, DEBE mostrar `$0`.
- **FR-013**: Servicios DEBE corresponder a la suma de Energía, Agua y Gas (`gastos_servicios`). Si no existen cargos, DEBE mostrar `$0`.
- **FR-014**: Predial DEBE corresponder al valor del impuesto predial registrado (`pago_predial`). Si no existe, DEBE mostrar `$0`.
- **FR-015**: Incidentes DEBE mostrar el valor registrado en `valor_incidentes`, que puede ser total o parcial según la lógica de pago diferido.
- **FR-016**: NETO A PAGAR DEBE mantener el cálculo actual: `total_ingresos - total_egresos - valor_incidentes`. No se debe modificar ninguna regla financiera existente.
- **FR-017**: La incorporación del concepto Incidentes en el Resumen Financiero DEBE respetar el cálculo actual del NETO.

#### Código QR

- **FR-018**: El sistema DEBE eliminar completamente el Código QR del Estado de Cuenta PDF. Esto aplica tanto a generación individual como por lotes (ZIP).
- **FR-019**: El sistema DEBE eliminar cualquier espacio reservado dentro del layout del PDF para el QR.
- **FR-020**: El encabezado del documento DEBE redistribuirse para evitar espacios en blanco innecesarios tras la eliminación del QR.
- **FR-021**: La eliminación del QR NO DEBE afectar el renderizado del resto del documento.

#### Sección: OBSERVACIONES

- **FR-022**: El sistema DEBE incorporar una sección denominada OBSERVACIONES en el Estado de Cuenta PDF. Esta sección DEBE mostrarse siempre, independientemente de si hay contenido.
- **FR-023**: La sección OBSERVACIONES DEBE mostrar la información registrada en el campo `observaciones` de la liquidación.
- **FR-024**: El sistema DEBE recuperar las observaciones desde la base de datos PostgreSQL.
- **FR-025**: El diseño del PDF DEBE adaptarse correctamente cuando las observaciones sean extensas, implementando manejo de saltos de línea y ajuste automático del contenido.
- **FR-026**: La información mostrada en la sección OBSERVACIONES DEBE coincidir exactamente con las observaciones almacenadas en la liquidación.

#### Consistencia de Datos

- **FR-027**: Todos los valores financieros mostrados en el PDF DEBEN corresponder exactamente a los valores almacenados en PostgreSQL.
- **FR-028**: No DEBE existir diferencia entre los valores mostrados en la interfaz del sistema y los mostrados en el documento PDF.
- **FR-029**: No DEBEN introducirse regresiones funcionales en la generación del Estado de Cuenta.
- **FR-030**: Los cálculos financieros DEBEN permanecer inalterados, salvo los ajustes visuales y de presentación solicitados.

### Key Entities

- **Liquidacion**: Representa la liquidación mensual de un contrato de mandato para un propietario. Contiene todos los valores financieros (canon, comisión, IVA, gastos, incidentes, neto), el estado de la liquidación, observaciones y metadatos de auditoría.
- **Incidente**: Representa un incidente asociado a una propiedad (reparación, mantenimiento, etc.). Puede tener un plan de pago con cuotas que se descuentan de liquidaciones.
- **IncidenteLiquidacion**: Entidad de unión que vincula un incidente específico con una liquidación, registrando el valor de descuento y la cuota asociada.
- **ContratoMandato**: Contrato que establece el canon de mandato y el porcentaje de comisión. Es la fuente del porcentaje de comisión mostrado en el Resumen Financiero.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los valores financieros en el PDF coinciden exactamente con los valores almacenados en PostgreSQL (verificable por auditoría directa).
- **SC-002**: La columna INCIDENTES se muestra correctamente en el 100% de las liquidaciones generadas, incluyendo aquellas con `valor_incidentes = 0`.
- **SC-003**: El Resumen Financiero muestra los 8 conceptos en el orden especificado en el 100% de los documentos generados.
- **SC-004**: El Código QR no aparece en ningún Estado de Cuenta PDF generado después de la implementación.
- **SC-005**: La sección OBSERVACIONES muestra el contenido completo sin truncamiento en el 100% de las liquidaciones con observaciones.
- **SC-006**: El diseño visual del PDF se mantiene limpio y correctamente alineado tras todos los cambios, sin espacios en blanco innecesarios ni elementos superpuestos.
- **SC-007**: No existen regresiones funcionales: liquidaciones sin incidentes, con servicios, con administración, con predial, con y sin observaciones se generan correctamente.

## Assumptions

- La entidad `Liquidacion` ya tiene el campo `valor_incidentes` persistido correctamente en PostgreSQL, sincronizado via triggers que recalculan el total al asociar/desasociar incidentes.
- El campo `observaciones` de la liquidación ya contiene la información registrada al momento de generar o editar la liquidación.
- El porcentaje de comisión (`comision_porcentaje`) se almacena en base 10000 (ej. 500 = 5%, 800 = 8%, 1200 = 12%).
- La lógica de cálculo del NETO A PAGAR (`total_ingresos - total_egresos - valor_incidentes`) no debe modificarse.
- El tipo de propiedad (horizontal vs. no horizontal) se determina por el valor de `gastos_administracion`: si es mayor a 0, la propiedad es horizontal y se muestra el concepto Administración; si es 0, se muestra `$0`.
- Solo se modifica el template `EstadoCuentaElite` (ReportLab), no el Legacy (`ServicioDocumentosPDF` con FPDF).
- Las observaciones en la BD pueden contener IDs de incidentes en formato "Inc #123" que se generan automáticamente al asociar incidentes.

## Reverse Engineering Summary *(informativo, no para implementación)*

### Flujo de Generación del PDF (Estado Actual)

```
Usuario → PDFState.generar_liquidacion_pdf(id)
  → ServicioFinanciero.obtener_datos_liquidacion_para_pdf(id)
    → RepositorioLiquidacionPostgres.obtener_datos_para_pdf(id)
      SQL JOIN: LIQUIDACIONES + CONTRATOS_MANDATOS + PROPIEDADES + PROPIETARIOS + PERSONAS
  → _transform_individual_to_pdf_format(datos)
  → ServicioPDFFacade.generar_estado_cuenta_elite(datos)
    → EstadoCuentaElite.generate(data)
      → enable_verification_qr("estado", id)  ← SE ELIMINARÁ
      → _add_informacion_consolidada()         ← MANTIENE
      → _add_tabla_propiedades()               ← MANTIENE
      → _add_detalle_propiedades()             ← MODIFICA: columna INCIDENTES siempre visible, elimina fila TOTAL
      → _add_resumen_financiero()              ← MODIFICA: reordenar conceptos, formato Comisión (X%)
      → _add_notas()                           ← MODIFICA: sección OBSERVACIONES
      → build() con QR + membrete              ← QR se elimina del build
```

### Archivos Clave a Modificar

| Archivo | Cambio |
|---|---|
| `estado_cuenta_elite.py` | Template principal: columna INCIDENTES, eliminar fila TOTAL, reordenar resumen, eliminar QR, agregar secciones OBSERVACIONES |
| `base_template.py` | Soporte para deshabilitar QR sin afectar membrete ni footer |
| `pdf_state.py` | Asegurar que `valor_incidentes` y `observaciones` se pasan al template |
