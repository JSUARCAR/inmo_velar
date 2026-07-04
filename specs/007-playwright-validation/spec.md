# Feature Specification: playwright-validation

**Feature Branch**: `007-playwright-validation`

**Created**: 2026-07-03

**Status**: Draft

**Input**: User description: "Quiero que utilices **Playwright** para realizar un proceso de **ingeniería inversa y validación funcional de nivel Senior/Principal** sobre los módulos **Incidentes** y **Liquidaciones de Propietarios**..."

## Clarifications

### Session 2026-07-03
- Q: ¿Cómo manejar la eliminación de datos en producción? → A: La propiedad "Calle Falsa 123 - Test Renov" es un entorno de pruebas seguro; se pueden eliminar registros sin necesidad de revertirlos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validación del Plan de Pago en Incidentes (Priority: P1)

Como evaluador del sistema, quiero verificar que el Plan de Pago se visualice correctamente en el detalle de un incidente para confirmar que las cuotas y estados financieros son consistentes.

**Why this priority**: Es crítico garantizar la transparencia financiera y la exactitud en la facturación a los propietarios, asegurando que las liquidaciones cuadren con las cotizaciones aprobadas.

**Independent Test**: Can be fully tested by navigating to the Incidentes module, selecting property "CONJ CIUDADELA COMFENALCO MZ H CS 29", and asserting the presence and correct amounts/states of the payment plan installments.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado en el módulo de Incidentes, **When** abre el detalle del incidente de la propiedad "CONJ CIUDADELA COMFENALCO MZ H CS 29", **Then** el Plan de Pago se muestra con todas las cuotas generadas y asociadas a su respectiva liquidación.
2. **Given** el Plan de Pago visible, **When** se examinan las cuotas, **Then** los valores coinciden con el valor aprobado de la cotización y el estado de pago global del incidente es consistente.

---

### User Story 2 - Selección de Incidentes en Liquidaciones (Priority: P1)

Como evaluador del sistema, quiero verificar la funcionalidad de selección de incidentes dentro del modal de edición de liquidaciones para la propiedad "Calle Falsa 123 - Test Renov".

**Why this priority**: La correcta asociación de incidentes a liquidaciones es fundamental para el proceso de recaudo y consolidación de deudas en el sistema.

**Independent Test**: Can be fully tested by opening the liquidation edit modal, clicking the incident selection button, and selecting incidents via checkboxes.

**Acceptance Scenarios**:

1. **Given** el modal de edición de liquidaciones abierto para la propiedad indicada, **When** la liquidación cumple las reglas de negocio, **Then** el botón "Seleccionar Incidentes" se encuentra visible y habilitado.
2. **Given** el botón habilitado, **When** se hace clic en él, **Then** se abre un modal que lista únicamente incidentes cuyo estado de pago sea distinto a "Pagado", permitiendo selección múltiple.
3. **Given** incidentes seleccionados, **When** se confirma la selección, **Then** se actualiza correctamente el campo "Incidentes" en la liquidación.

---

### User Story 3 - Eliminación de Liquidaciones (Priority: P1)

Como evaluador del sistema, quiero validar la acción de eliminar una liquidación en el módulo correspondiente, asegurando que el flujo completo (frontend a backend) se ejecuta sin errores.

**Why this priority**: La eliminación de registros financieros debe funcionar impecablemente y reflejar de inmediato los cambios en la interfaz, sin dejar datos huérfanos o estados inconsistentes.

**Independent Test**: Can be fully tested by triggering the delete action on a valid liquidation, confirming the prompt, and verifying the backend response and table update.

**Acceptance Scenarios**:

1. **Given** una liquidación que cumple las reglas de eliminación, **When** el usuario hace clic en "Eliminar" y confirma, **Then** la solicitud HTTP se envía correctamente, la eliminación se ejecuta en base de datos, y la tabla se actualiza automáticamente mostrando un mensaje de éxito.
2. **Given** una liquidación que NO puede ser eliminada, **When** se evalúa la visibilidad de la acción, **Then** la opción "Eliminar" no es visible o se encuentra inhabilitada, previniendo errores.

### Edge Cases

- What happens when la conexión de red falla durante la confirmación de la eliminación de una liquidación?
- How does system handle si los datos de la cotización en el backend no coinciden con las sumas de las cuotas del Plan de Pago?
- What happens when la propiedad "Calle Falsa 123 - Test Renov" no tiene incidentes con estado diferente de "Pagado"?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST ejecutar los flujos de validación utilizando scripts de automatización E2E en Playwright contra el entorno de producción (`https://extraordinary-joy-production-2fd2.up.railway.app/`).
- **FR-002**: System MUST iniciar sesión exitosamente utilizando las credenciales provistas.
- **FR-003**: System MUST documentar los pasos ejecutados y capturar trazas, logs de consola (frontend) y de red (HTTP) para cada acción evaluada.
- **FR-004**: System MUST proveer un reporte de diagnóstico identificando la causa raíz de las anomalías detectadas, categorizándolas (frontend, backend, DB, reglas de negocio).
- **FR-005**: System MUST proponer soluciones técnicas alineadas a la arquitectura actual (Reflex/PostgreSQL) para corregir los defectos encontrados.

### Key Entities *(include if feature involves data)*

- **Incidente**: Entidad de negocio que posee un estado de pago, plan de pago asociado, y se vincula a una propiedad específica.
- **Liquidacion**: Representa el estado financiero consolidado mensual de una propiedad, capaz de asociar incidentes pendientes de pago.
- **Plan de Pago**: Conjunto de cuotas con valores y estados definidos, enlazadas tanto a un incidente como a liquidaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los 3 flujos requeridos son validados y documentados con evidencia de ejecución.
- **SC-002**: Las causas raíz de los problemas encontrados son identificadas concluyentemente en el informe final.
- **SC-003**: El reporte final incluye propuestas técnicas de solución que no infringen los principios de inmutabilidad y Clean Architecture del proyecto.

## Assumptions

- El entorno de producción (`https://extraordinary-joy-production-2fd2.up.railway.app/`) se encuentra activo, accesible, y el login es funcional.
- Las propiedades "CONJ CIUDADELA COMFENALCO MZ H CS 29" y "Calle Falsa 123 - Test Renov" existen en la base de datos de producción con la data necesaria para las pruebas.
- No se requiere modificar el código durante esta fase de validación e ingeniería inversa, solo diagnosticar y reportar.
- La propiedad "Calle Falsa 123 - Test Renov" actúa como un entorno aislado de pruebas (sandbox), por lo que es seguro realizar operaciones destructivas (como eliminar liquidaciones) sin afectar datos reales de producción y sin requerir rollback.
