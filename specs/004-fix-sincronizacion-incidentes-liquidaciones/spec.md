# Feature Specification: Fix Sincronización Incidentes - Liquidaciones

**Feature Branch**: `004-fix-sincronizacion-incidentes-liquidaciones`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Corregir inconsistencias en la sincronización de información entre los módulos Incidentes y Liquidaciones de Propietarios. Se identificó que el valor de la cuota asociada al incidente no se refleja correctamente en el campo 'Incidentes' de la liquidación, y que el campo 'Observaciones' debe registrar automáticamente el ID del incidente asociado para garantizar la trazabilidad."

## Clarifications

### Session 2026-07-02

- Q: ¿Cuál debe ser la estrategia de sincronización entre triggers de BD y lógica de aplicación? → A: Mantener triggers como fuente primaria de `VALOR_INCIDENTES`, sincronizar cálculos en la capa de aplicación después del commit de la transacción.

- Q: ¿Qué roles del sistema pueden asociar y desasociar incidentes a liquidaciones? → A: Solo Administradores pueden asociar y desasociar incidentes a liquidaciones.

- Q: ¿Se debe ejecutar una migración de datos para corregir liquidaciones existentes con valores inconsistentes? → A: No migrar automáticamente. Proporcionar script de diagnóstico para identificar registros afectados y permitir revisión manual antes de corrección.

- Q: ¿Cuál debe ser el comportamiento cuando las observaciones excedan la capacidad del campo? → A: Mantener solo los IDs de incidentes más recientes, descartando los más antiguos.

- Q: ¿Qué nivel de testing se requiere para este fix? → A: Tests unitarios para lógica de negocio + tests de integración para persistencia en base de datos.

## Contexto del Problema

Durante la validación funcional del sistema, se identificaron inconsistencias críticas en la integración entre los módulos de Incidentes y Liquidaciones de Propietarios. Aunque la asociación entre cuotas del plan de pago y liquidaciones funciona parcialmente, existen problemas de sincronización que afectan la integridad de la información financiera.

**Propiedad afectada**: "Calle Falsa 123 - Test Renov"

### Problemas Identificados por Ingeniería Inversa

1. **Desincronización de NETO_A_PAGAR**: Al asociar un incidente a una liquidación, el trigger de BD actualiza correctamente `VALOR_INCIDENTES`, pero el método `calcular_totales()` en memoria usa el valor antiguo, resultando en un `NETO_A_PAGAR` incorrecto.

2. **Observaciones se sobreescribe**: Al asociar múltiples incidentes, cada uno reemplaza las observaciones anteriores en lugar de hacer append. Solo queda el ID del último incidente asociado.

3. **Desasociar borra todas las observaciones**: Al desasociar un incidente, se limpia completamente el campo observaciones, incluyendo notas del usuario.

4. **ESTADO_PAGO no se persiste**: El repositorio de incidentes no incluye `ESTADO_PAGO` en el UPDATE SQL, aunque el servicio lo modifica en memoria.

5. **Mapeo incorrecto en formulario de edición**: El campo "Incidentes" en el formulario de edición está mapeado a `gastos_reparaciones` en lugar de `valor_incidentes`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización Correcta del Valor de Incidentes (Priority: P1)

Como Administrador, necesito que al abrir el detalle de una liquidación que tiene incidentes asociados, el campo "Incidentes (Plan Pago)" muestre la suma correcta de todas las cuotas de incidentes vinculadas, para poder verificar los descuentos aplicados antes de aprobar la liquidación.

**Why this priority**: Es el problema principal reportado. Sin este fix, la información financiera mostrada es incorrecta y puede llevar a decisiones erróneas.

**Independent Test**: Puede ser probada al abrir el detalle de una liquidación que tiene al menos un incidente asociado y verificar que el valor mostrado en "Incidentes" coincide con la suma de las cuotas asociadas en la base de datos.

**Acceptance Scenarios**:

1. **Given** una liquidación con una cuota de incidente asociada por $250.000, **When** el Administrador abre el detalle de la liquidación, **Then** el campo "Incidentes (Plan Pago)" muestra "$250.000".

2. **Given** una liquidación con tres cuotas de incidentes asociadas ($250.000 + $150.000 + $100.000), **When** el Administrador abre el detalle de la liquidación, **Then** el campo "Incidentes (Plan Pago)" muestra "$500.000" (suma total).

3. **Given** una liquidación sin incidentes asociados, **When** el Administrador abre el detalle, **Then** el campo "Incidentes (Plan Pago)" muestra "$0" o está vacío.

4. **Given** una liquidación con incidentes asociados, **When** el Administrador visualiza el neto a pagar, **Then** el valor es correcto: `total_ingresos - total_egresos - valor_incidentes`.

---

### User Story 2 - Registro Automático de IDs de Incidentes en Observaciones (Priority: P1)

Como Administrador, necesito que al asociar un incidente a una liquidación, el campo "Observaciones" de la liquidación registre automáticamente el ID del incidente, para poder rastrear el origen de cada descuento aplicado.

**Why this priority**: Es esencial para la trazabilidad y auditoría. Sin esta funcionalidad, no es posible identificar qué incidente generó cada descuento.

**Independent Test**: Puede ser probada al asociar uno o varios incidentes a una liquidación y verificar que las observaciones contienen los IDs de todos los incidentes asociados.

**Acceptance Scenarios**:

1. **Given** una liquidación sin observaciones, **When** el Administrador asocia el incidente #101, **Then** las observaciones muestran "Inc #101".

2. **Given** una liquidación con observaciones "Inc #101", **When** el Administrador asocia el incidente #205, **Then** las observaciones muestran "Inc #101\nInc #205" (append, no reemplazo).

3. **Given** una liquidación con observaciones "Inc #101\nInc #205", **When** el Administrador asocia el incidente #310, **Then** las observaciones muestran "Inc #101\nInc #205\nInc #310".

4. **Given** una liquidación con observaciones personalizadas del usuario, **When** el Administrador asocia un incidente, **Then** las observaciones del usuario se preservan y se agrega el ID del incidente.

---

### User Story 3 - Persistencia del Estado de Pago del Incidente (Priority: P2)

Como sistema, necesito que cuando se asocie o desasocie un incidente a una liquidación, el estado de pago del incidente (Pendiente, Parcialmente Pagado, Pagado) se actualice y persista correctamente en la base de datos.

**Why this priority**: Es fundamental para la integridad de datos. Sin persistencia correcta, el estado de pago mostrado en la UI no refleja el estado real.

**Independent Test**: Puede ser probada al asociar un incidente a una liquidación pagada y verificar que el estado de pago del incidente se actualiza en la base de datos.

**Acceptance Scenarios**:

1. **Given** un incidente con estado_pago "Pendiente", **When** se asocia a una liquidación que cambia a estado "Pagada", **Then** el estado_pago del incidente se actualiza a "Pagado" en la base de datos.

2. **Given** un incidente con estado_pago "Pendiente", **When** se asocia a una liquidación que está "En Proceso", **Then** el estado_pago del incidente se actualiza a "Asociada" en la base de datos.

3. **Given** un incidente con estado_pago "Pagado", **When** se desasocia de una liquidación, **Then** el estado_pago del incidente se recalcula y persiste correctamente.

---

### User Story 4 - Desasociación Segura de Incidentes (Priority: P2)

Como Administrador, necesito que al desasociar un incidente de una liquidación, las observaciones se actualicen correctamente (eliminando solo el ID del incidente desasociado) y que el neto a pagar se recalcule.

**Why this priority**: Es esencial para mantener la integridad cuando se corrigen errores de asociación.

**Independent Test**: Puede ser probada al desasociar un incidente de una liquidación que tiene múltiples incidentes asociados y verificar que las observaciones se actualizan correctamente.

**Acceptance Scenarios**:

1. **Given** una liquidación con observaciones "Inc #101\nInc #205", **When** el Administrador desasocia el incidente #101, **Then** las observaciones muestran "Inc #205".

2. **Given** una liquidación con observaciones "Inc #101\nInc #205", **When** el Administrador desasocia el incidente #205, **Then** las observaciones muestran "Inc #101".

3. **Given** una liquidación con observaciones "Inc #101", **When** el Administrador desasocia el incidente #101, **Then** las observaciones quedan vacías.

4. **Given** una liquidación con observaciones del usuario "Nota importante: verificar con propietario" más "Inc #101", **When** el Administrador desasocia el incidente #101, **Then** las observaciones muestran "Nota importante: verificar con propietario".

---

### User Story 5 - Formulario de Edición Correcto (Priority: P2)

Como Administrador, necesito que al editar una liquidación, el campo "Incidentes" muestre y permita editar el valor correcto de descuentos por incidentes, sin mezclarlo con otros campos como gastos de reparación.

**Why this priority**: Es esencial para la edición correcta de liquidaciones. Un mapeo incorrecto puede causar pérdida de datos.

**Independent Test**: Puede ser probada al abrir el formulario de edición de una liquidación con incidentes asociados y verificar que el campo "Incidentes" muestra el valor correcto.

**Acceptance Scenarios**:

1. **Given** una liquidación con valor_incidentes $500.000, **When** el Administrador abre el formulario de edición, **Then** el campo "Incidentes" muestra $500.000.

2. **Given** una liquidación con valor_incidentes $500.000 y gastos_reparaciones $200.000, **When** el Administrador edita el campo "Incidentes" a $600.000, **Then** el campo "Gastos Reparaciones" mantiene su valor de $200.000.

3. **Given** una liquidación con valor_incidentes $500.000, **When** el Administrador guarda los cambios, **Then** el valor_incidentes se actualiza a $600.000 en la base de datos y el neto_a_pagar se recalcula correctamente.

---

### User Roles

| Rol | Asociar Incidentes a Liquidación | Desasociar Incidentes de Liquidación |
|-----|----------------------------------|-------------------------------------|
| Administrador | Sí | Sí |
| Asesor | No | No |
| Operador | No | No |

---

### Edge Cases

- ¿Qué sucede si se intenta asociar un incidente a una liquidación que ya tiene el máximo de observaciones permitidas? → El sistema debe permitir la asociación y mantener solo los IDs de incidentes más recientes, descartando los más antiguos cuando se exceda la capacidad del campo.

- ¿Qué sucede si la conexión a la base de datos se pierde durante una operación de asociación? → La transacción debe hacer rollback automáticamente y mantener el estado original.

- ¿Qué sucede si se asocia y desasocia rápidamente el mismo incidente? → El sistema debe manejar la concurrencia correctamente y mantener la integridad de los datos.

- ¿Qué sucede si el valor de la liquidación es menor al valor de la cuota del incidente? → El sistema debe permitir la asociación pero mostrar una advertencia sobre el impacto en el neto a pagar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST correctly calculate and display the sum of all incident installments in the "Incidentes" field of the liquidation detail view.

- **FR-002**: System MUST recalculate `NETO_A_PAGAR` after each incident association or disassociation, using the updated `VALOR_INCIDENTES` value from the database trigger (not from in-memory state).

- **FR-003**: System MUST append incident IDs to the "Observaciones" field when associating incidents, preserving existing observations.

- **FR-004**: System MUST remove only the specific incident ID from "Observaciones" when disassociating an incident, preserving other observations.

- **FR-005**: System MUST persist `ESTADO_PAGO` changes in the incidentes table when association or disassociation operations occur.

- **FR-006**: System MUST correctly map the "Incidentes" field in the liquidation edit form to `valor_incidentes`, not to `gastos_reparaciones`.

- **FR-007**: System MUST maintain data consistency between the database triggers and the application layer calculations.

- **FR-008**: System MUST preserve user-entered observations when associating or disassociating incidents.

- **FR-009**: System MUST recalculate all financial totals (total_egresos, neto_a_pagar) after any incident association or disassociation.

- **FR-010**: System MUST ensure that the edit form correctly saves changes to `valor_incidentes` without affecting `gastos_reparaciones`.

### Key Entities

- **Liquidacion**: Monthly account statement for a property owner. Key fields affected: `valor_incidentes`, `neto_a_pagar`, `observaciones`.

- **Incidente**: Maintenance incident. Key field affected: `estado_pago`.

- **CuotaIncidente**: Installment of the payment plan. Key fields: `id_liquidacion`, `estado_pago`.

- **IncidenteLiquidacion**: Relationship entity linking incidents to liquidations. Key fields: `id_incidente`, `id_liquidacion`, `valor_descuento`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of liquidations with associated incidents display the correct sum in the "Incidentes" field.

- **SC-002**: 100% of incident association operations correctly append the incident ID to "Observaciones".

- **SC-003**: 100% of incident disassociation operations correctly remove only the specific incident ID from "Observaciones".

- **SC-004**: 100% of `ESTADO_PAGO` changes are persisted in the database after association/disassociation operations.

- **SC-005**: 0% of data corruption incidents where `gastos_reparaciones` is modified when editing `valor_incidentes`.

- **SC-006**: All financial calculations (neto_a_pagar) are consistent with the sum of their components after any operation.

- **SC-007**: User-entered observations are preserved in 100% of association/disassociation operations.

- **SC-008**: >90% test coverage for new business logic (unit tests) and persistence logic (integration tests).

## Testing Strategy

- **Unit Tests**: Lógica de negocio en `ServicioIncidenteLiquidacion` y `ServicioEstadoPago` (cálculo de totales, append/remove de observaciones, recálculo de estado de pago).

- **Integration Tests**: Persistencia en `RepositorioIncidentesPostgres` y `RepositorioLiquidacionPostgres` (verificar que `ESTADO_PAGO` se persiste correctamente, que `NETO_A_PAGAR` se recalcula tras asociación/desasociación).

- **Script de Diagnóstico**: Herramienta para identificar liquidaciones existentes con `valor_incidentes` o `neto_a_pagar` inconsistentes antes de aplicar el fix en producción.

## Assumptions

- The existing database triggers for `VALOR_INCIDENTES` are functioning correctly and will be maintained as the primary source of truth. Application-layer calculations will sync after trigger execution.

- Only Administrators can perform association/disassociation operations. The permission system must enforce this restriction.

- Existing liquidations with incorrect values will NOT be migrated automatically. A diagnostic script will be provided for manual review.

- When observations exceed field capacity, only the most recent incident IDs will be preserved.

- Testing will include unit tests for business logic and integration tests for persistence, meeting the >90% coverage requirement.

- The existing permission system already supports the required access controls for these operations.

- The current UI component library (neuro_elements) can be used for any new UI elements needed.

- The existing transaction management in the repository layer can be extended to support the additional operations.

- The bug fixes will not require changes to the database schema, only to application code and potentially trigger logic.

## Dependencies

- **Existing Module**: Incidentes (with payment plan and installment functionality)

- **Existing Module**: Liquidaciones de Propietarios (with approval, payment, and reversal workflows)

- **Database Triggers**: TRG_INCIDENTE_LIQ_ACTUALIZAR_VALOR_INSERT and TRG_INCIDENTE_LIQ_ACTUALIZAR_VALOR_DELETE

- **UI Framework**: Reflex framework with neuro_elements component library

## Technical Justification

The implementation follows the existing architecture patterns:

1. **Service Layer**: Fixes will be applied to `ServicioIncidenteLiquidacion` and `ServicioEstadoPago` to ensure correct calculation and persistence.

2. **Repository Layer**: Updates to `RepositorioIncidentesPostgres` to include `ESTADO_PAGO` in UPDATE statements.

3. **UI Layer**: Corrections to `liquidacion_edit_form.py` to fix field mapping.

4. **Observations Logic**: Implementation of append/remove logic for incident IDs in observations.

5. **Financial Calculations**: Ensuring `calcular_totales()` is called with the updated `valor_incidentes` value.
