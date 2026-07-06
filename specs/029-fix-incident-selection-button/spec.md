# Feature Specification: fix-incident-selection-button

**Feature Branch**: `029-fix-incident-selection-button`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User description: "Ingeniería inversa y validación funcional del módulo Liquidaciones — regresión en funcionalidad de selección de incidentes. El botón 'Seleccionar Incidentes' no se visualiza dentro del modal de creación y edición de liquidaciones, impidiendo asociar incidentes a una liquidación."

## Análisis de Ingeniería Inversa (Hallazgos)

Tras la investigación profunda del código fuente del módulo de Liquidaciones, se identificaron los siguientes hallazgos:

### Estructura Actual de Archivos Involucrados

| Archivo | Rol | Estado |
|---------|-----|--------|
| `liquidacion_create_form.py` | Formulario de creación | ❌ **SIN** botón "Seleccionar Incidentes" |
| `liquidacion_edit_form.py` | Formulario de edición | ✅ **CON** botón (L151-163) — Funcional |
| `modal_seleccion_incidentes.py` | Modal de selección | ✅ Implementado completo |
| `liquidaciones_state.py` | State handlers | ✅ Handlers existen (L1928-2181) |
| `liquidaciones.py` (page) | Página principal | ✅ Modal incluido en render (L723) |

### Causa Raíz Identificada

1. **Formulario de CREACIÓN** (`liquidacion_create_form.py`): **NO contiene** el botón "Seleccionar Incidentes". Esto significa que durante la creación de una liquidación **nunca** fue posible asociar incidentes, ya que el campo `gastos_reparaciones` se ingresa manualmente sin vinculación real a incidentes.

2. **Formulario de EDICIÓN** (`liquidacion_edit_form.py`): **SÍ contiene** el botón (líneas 151-163), y está renderizado **sin condición** — se muestra siempre que el modal de edición esté abierto (que solo ocurre para liquidaciones "En Proceso"). El botón invoca `LiquidacionesState.open_seleccion_incidentes_modal(form_data["id_liquidacion"].to(int))`.

3. **Flujo Backend**: Los handlers `open_seleccion_incidentes_modal`, `toggle_seleccion_incidente`, `asociar_incidentes_seleccionados` y `close_seleccion_incidentes_modal` existen en `liquidaciones_state.py` (L1928-2181). Los repositorios `RepositorioIncidenteLiquidacionPostgres`, `RepositorioCuotaPostgres`, `RepositorioPlanPagoPostgres` y el `ServicioIncidenteLiquidacion` también existen.

4. **Modal de incidentes**: El componente `modal_seleccion_incidentes` está correctamente implementado con tabla de incidentes elegibles, checkboxes de selección, totales de descuentos y botón "Asociar Seleccionados".

### Hipótesis de Regresión

La regresión reportada ("el botón ya no se visualiza") puede deberse a:
- **Escenario A**: El botón **nunca existió en el formulario de creación** — la expectativa del usuario es que debería existir también allí.
- **Escenario B**: El botón existió previamente en el formulario de edición y fue removido/ocultado por un cambio reciente.
- **Escenario C**: El modal de edición no se abre correctamente (error de rendering de Reflex), lo que impide ver el botón que sí está en el código.

Dado que el botón **está presente en el código del formulario de edición** (L151-163), la validación en vivo determinará si el problema es de rendering o de lógica condicional.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seleccionar Incidentes al Editar Liquidación (Priority: P1)

Como administrador del sistema, quiero poder hacer clic en el botón "Seleccionar Incidentes" dentro del formulario de edición de una liquidación "En Proceso", para asociar uno o varios incidentes pendientes de pago y que sus cuotas se descuenten automáticamente del neto a pagar.

**Why this priority**: Es la funcionalidad core que reporta la regresión. Sin ella, los incidentes no pueden vincularse a liquidaciones, afectando directamente la facturación y el flujo de cobro.

**Independent Test**: Abrir la página de Liquidaciones, editar una liquidación en estado "En Proceso", verificar que el botón "Seleccionar Incidentes" sea visible, hacer clic, confirmar que el modal se abre con incidentes elegibles.

**Acceptance Scenarios**:

1. **Given** un administrador edita una liquidación con estado "En Proceso", **When** el formulario de edición se carga, **Then** el botón "Seleccionar Incidentes" se muestra visible y habilitado.
2. **Given** el botón "Seleccionar Incidentes" es visible, **When** el administrador hace clic en él, **Then** el modal de selección de incidentes se abre mostrando un spinner de carga seguido de la tabla de incidentes elegibles.
3. **Given** el modal de incidentes está abierto con incidentes disponibles, **When** el administrador selecciona uno o más incidentes mediante checkboxes, **Then** el resumen inferior muestra la cantidad seleccionada y el total de descuentos.
4. **Given** el administrador ha seleccionado incidentes, **When** hace clic en "Asociar Seleccionados", **Then** los incidentes quedan vinculados a la liquidación, el valor de incidentes se actualiza en el formulario de edición, y se muestra un toast de confirmación.

---

### User Story 2 - Seleccionar Incidentes al Crear Liquidación (Priority: P2)

Como administrador del sistema, quiero poder seleccionar incidentes pendientes de pago al momento de crear una nueva liquidación, para que los descuentos por incidentes se apliquen desde el inicio sin necesidad de editar la liquidación después.

**Why this priority**: Actualmente, el botón "Seleccionar Incidentes" solo existe en el formulario de edición. Agregarlo al formulario de creación optimiza el flujo del usuario y reduce pasos manuales.

**Independent Test**: Abrir la página de Liquidaciones, hacer clic en "Nueva Liquidación", seleccionar un contrato/propiedad, verificar que el botón "Seleccionar Incidentes" aparezca (solo después de seleccionar contrato), y confirmar que el modal funciona correctamente.

**Acceptance Scenarios**:

1. **Given** un administrador está creando una nueva liquidación y ha seleccionado una propiedad/contrato, **When** el formulario muestra los datos del contrato, **Then** el botón "Seleccionar Incidentes" se muestra visible en la sección de Egresos Variables.
2. **Given** el formulario de creación NO tiene propiedad seleccionada, **When** se renderiza la sección de Egresos, **Then** el botón "Seleccionar Incidentes" NO se muestra (ya que no se puede buscar incidentes sin contexto de contrato).
3. **Given** el modal de incidentes se abre desde el formulario de creación, **When** el administrador selecciona incidentes y confirma, **Then** el campo "Incidentes" (`gastos_reparaciones`) se actualiza con la suma total de descuentos.

---

### User Story 3 - Persistencia y Consistencia de Datos (Priority: P1)

Como sistema, debo garantizar que toda la información de asociación de incidentes a liquidaciones se almacene correctamente en la base de datos PostgreSQL y que exista consistencia entre la interfaz, el backend y la base de datos.

**Why this priority**: Sin persistencia correcta, toda la funcionalidad de selección es inútil. Debe funcionar de extremo a extremo.

**Independent Test**: Asociar un incidente a una liquidación, verificar en la base de datos que la tabla de relación `INCIDENTES_LIQUIDACIONES` contiene el registro correcto con los valores esperados.

**Acceptance Scenarios**:

1. **Given** incidentes han sido asociados exitosamente, **When** se consulta la tabla de relación en la base de datos, **Then** cada registro contiene `id_incidente`, `id_liquidacion`, `numero_cuota`, `valor_descuento` y `asociado_por` correctos.
2. **Given** una liquidación tiene incidentes asociados, **When** se reabre el modal de selección de incidentes, **Then** los incidentes ya asociados se muestran marcados como "Ya asociado" con el checkbox deshabilitado.
3. **Given** el campo `valor_incidentes` de la liquidación se actualizó, **When** se recarga la página de liquidaciones, **Then** el neto a pagar refleja el descuento correctamente.

---

### Edge Cases

- ¿Qué ocurre cuando no hay incidentes elegibles para asociar? El modal debe abrirse y mostrar el mensaje "No hay incidentes disponibles para asociar."
- ¿Qué ocurre si un incidente no tiene plan de pago activo? El backend lo excluye de la lista (lógica existente en L2004-2005).
- ¿Qué ocurre si un incidente ya fue completamente pagado? Se filtra por `ESTADO_PAGO != 'Pagado'` en la consulta SQL.
- ¿Qué sucede al seleccionar un incidente cuya cuota ya está asociada a otra liquidación? Se excluye (`cuota.id_liquidacion != id_liquidacion` en L2013).
- ¿Qué pasa si se produce un error de conexión al cargar incidentes? Se muestra un callout rojo con el mensaje de error.
- ¿Qué ocurre si se intenta asociar desde el formulario de creación antes de guardar la liquidación? Se necesita evaluar si el flujo requiere un ID de liquidación previo (requisito de diseño).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST renderizar el botón "Seleccionar Incidentes" en el formulario de edición de liquidaciones en estado "En Proceso".
- **FR-002**: El sistema MUST abrir el modal de selección de incidentes al hacer clic en el botón "Seleccionar Incidentes".
- **FR-003**: El modal MUST cargar únicamente incidentes con estado en [`Aprobado`, `En Reparacion`, `Finalizado`] cuyo `ESTADO_PAGO` sea diferente de `Pagado`.
- **FR-004**: El modal MUST permitir seleccionar múltiples incidentes mediante checkboxes individuales.
- **FR-005**: El modal MUST mostrar un resumen en tiempo real con la cantidad de incidentes seleccionados y el total de descuentos.
- **FR-006**: Al confirmar la selección ("Asociar Seleccionados"), el sistema MUST persistir cada relación incidente-liquidación en la base de datos.
- **FR-007**: El sistema MUST actualizar el campo `valor_incidentes` de la liquidación con la suma de descuentos de cuotas asociadas.
- **FR-008**: Los incidentes previamente asociados a la misma liquidación MUST mostrarse como "Ya asociado" con el checkbox deshabilitado.
- **FR-009**: El sistema MUST agregar el botón "Seleccionar Incidentes" al formulario de creación, visible solo cuando se haya seleccionado un contrato/propiedad.
- **FR-010**: El modal de incidentes MUST ser interactivo (pointer-events: auto) cumpliendo con el protocolo de Superposiciones y Portals (Radix UI) del proyecto.

### Key Entities

- **Liquidación**: Estado de cuenta mensual de un propietario. Atributos clave: `id_liquidacion`, `id_contrato_m`, `periodo`, `estado`, `valor_incidentes`, `neto_pagar`.
- **Incidente**: Evento financiero (reparación, cargo) asociado a una propiedad. Atributos clave: `id_incidente`, `descripcion`, `costo_incidente`, `estado`, `estado_pago`, `id_propiedad`.
- **Plan de Pago**: Estructura de cuotas para un incidente. Atributos: `id_plan_pago`, `id_incidente`, `valor_cuota`, `num_cuotas`.
- **Cuota**: Unidad de pago de un plan. Atributos: `id_cuota`, `numero_cuota`, `id_liquidacion`, `estado`.
- **Relación Incidente-Liquidación**: Vínculo entre un incidente y una liquidación. Atributos: `id_incidente`, `id_liquidacion`, `numero_cuota`, `valor_descuento`, `asociado_por`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las veces que un administrador abre el formulario de edición de una liquidación "En Proceso", el botón "Seleccionar Incidentes" es visible y funcional.
- **SC-002**: El modal de selección se abre y carga datos en menos de 2 segundos bajo condiciones normales de red.
- **SC-003**: Los incidentes asociados se persisten correctamente en la base de datos con 0% de pérdida de datos tras la confirmación.
- **SC-004**: El valor total de descuentos se refleja correctamente en el campo `valor_incidentes` de la liquidación, tanto en la interfaz como en la base de datos.
- **SC-005**: Ninguna funcionalidad existente del módulo de Liquidaciones presenta regresión tras la implementación.
- **SC-006**: La consola del navegador no muestra errores relacionados con el flujo de selección de incidentes.

## Assumptions

- Los repositorios de infraestructura (`RepositorioIncidenteLiquidacionPostgres`, `RepositorioCuotaPostgres`, `RepositorioPlanPagoPostgres`) y el servicio de aplicación (`ServicioIncidenteLiquidacion`) están implementados y funcionales.
- El botón en el formulario de edición ya existe en el código (L151-163 de `liquidacion_edit_form.py`) y la regresión puede ser un problema de rendering de Reflex o de un cambio reciente que impide su visualización.
- La base de datos PostgreSQL tiene las tablas `INCIDENTES`, `PLANES_PAGO`, `CUOTAS_PLAN_PAGO` e `INCIDENTES_LIQUIDACIONES` creadas y funcionales.
- El formulario de creación de liquidaciones nunca tuvo el botón "Seleccionar Incidentes", por lo que su adición es una mejora nueva (no una restauración).
- El estado `form_data["id_liquidacion"]` está correctamente establecido antes de que el botón sea clickeado en el formulario de edición.
