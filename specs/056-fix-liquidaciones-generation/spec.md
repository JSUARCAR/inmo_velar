# Feature Specification: Corrección Generación de Liquidaciones de Propietarios

**Feature Branch**: `056-fix-liquidaciones-generation`

**Created**: 2026-07-15

**Status**: Draft

**Input**: Ingeniería inversa sobre el módulo de Liquidaciones de Propietarios. Se identificó que el sistema no genera correctamente las liquidaciones para propiedades con Contrato de Mandato activo. La propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" no permite generación individual, y la generación masiva falla con el error "Hubo errores generando todas las liquidaciones."

## User Scenarios & Testing

### User Story 1 - Generación Individual de Liquidación (Priority: P1)

Como usuario administrador del sistema, quiero generar una liquidación mensual para una propiedad específica seleccionándola del formulario, para que se calcule automáticamente la comisión, IVA, gastos de administración y valor de incidentes, y se guarde la liquidación en estado "En Proceso".

**Why this priority**: Es la funcionalidad base del módulo. Sin generación individual funcional, no existe flujo de liquidaciones. El caso de la propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" demuestra que esta funcionalidad está rota para al menos una propiedad elegible.

**Independent Test**: Se puede probar seleccionando la propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" en el formulario de creación, verificando que se cargue el contrato de mandato activo, calculando los valores financieros, y confirmando que la liquidación se persiste correctamente en la base de datos.

**Acceptance Scenarios**:

1. **Given** que existe una propiedad con Contrato de Mandato activo, **When** el usuario la selecciona en el formulario de creación de liquidación, **Then** el sistema carga automáticamente el ID del contrato, el canon de mandato, la dirección de la propiedad y el nombre del propietario.
2. **Given** que se completaron los datos del formulario (período, otros ingresos, gastos), **When** el usuario presiona "Guardar", **Then** el sistema calcula comisión (canon × porcentaje / 10000), IVA (comisión × 19%), obtiene gastos de administración de la propiedad, obtiene valor de incidentes pendientes, y crea la liquidación con estado "En Proceso".
3. **Given** que ya existe una liquidación para el mismo contrato y período, **When** el usuario intenta crear otra, **Then** el sistema muestra un mensaje de error indicando que ya existe una liquidación para ese período.
4. **Given** que la propiedad seleccionada no tiene Contrato de Mandato activo, **When** el usuario intenta seleccionarla, **Then** la propiedad no aparece en las opciones disponibles del formulario.

---

### User Story 2 - Generación Masiva de Liquidaciones (Priority: P1)

Como usuario administrador, quiero ejecutar un proceso que genere liquidaciones para TODAS las propiedades con Contrato de Mandato activo en un solo paso, seleccionando solo el período, para agilizar el cierre mensual de liquidaciones.

**Why this priority**: La generación masiva es el flujo principal de cierre mensual. El error actual ("Hubo errores generando todas las liquidaciones") bloquea completamente el proceso de cierre, impidiendo la operación del negocio.

**Independent Test**: Ejecutar la generación masiva seleccionando un período, verificar que se creen liquidaciones para todas las propiedades con contrato activo, y confirmar que el toast de resultado refleje correctamente la cantidad generada y cualquier omisión.

**Acceptance Scenarios**:

1. **Given** que existen propietarios con Contratos de Mandato activos, **When** el usuario ejecuta la generación masiva seleccionando un período, **Then** el sistema genera una liquidación para cada contrato de mandato activo y muestra un toast con el conteo de liquidaciones generadas exitosamente.
2. **Given** que algunos propietarios ya tienen liquidaciones para el período seleccionado, **When** se ejecuta la generación masiva, **Then** el sistema omite silenciosamente los contratos que ya tienen liquidación y genera solo las faltantes, mostrando un conteo separado de generadas y omitidas.
3. **Given** que NO existen propietarios con Contratos de Mandato activos, **When** se ejecuta la generación masiva, **Then** el sistema muestra un mensaje informativo indicando que no se encontraron propietarios elegibles.
4. **Given** que TODOS los contratos activos ya tienen liquidaciones para el período, **When** se ejecuta la generación masiva, **Then** el sistema muestra un mensaje informativo indicando que ya existían liquidaciones, no un error genérico.

---

### User Story 3 - Diagnóstico y Corrección de Causa Raíz (Priority: P1)

Como desarrollador del sistema, quiero que se identifique y corrija la causa raíz por la que la generación masiva falla para TODOS los propietarios simultáneamente, para que el sistema sea confiable en producción.

**Why this priority**: El error masivo sugiere un problema sistémico (no un caso aislado) que afecta toda la operación. Sin su corrección, ni la generación individual ni la masiva funcionan de manera confiable.

**Independent Test**: Ejecutar la generación masiva en el entorno de producción con datos reales, verificar que se generen liquidaciones para todas las propiedades elegibles, y revisar los logs del servidor para confirmar ausencia de excepciones no controladas.

**Acceptance Scenarios**:

1. **Given** que el sistema tiene datos de prueba con al menos 3 propietarios con contratos activos, **When** se ejecuta la generación masiva, **Then** se generan al menos 3 liquidaciones (una por contrato activo) sin errores.
2. **Given** que se produce un error durante la generación para un propietario específico, **When** el proceso continúa con los demás propietarios, **Then** el sistema registra el error específico del propietario afectado en los logs y genera las liquidaciones restantes sin interrupción.
3. **Given** que la propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" tiene un Contrato de Mandato activo, **When** se busca en el formulario de creación individual, **Then** la propiedad aparece en las opciones y permite generar la liquidación correctamente.

---

### Edge Cases

- ¿Qué sucede cuando un propietario tiene múltiples propiedades con contratos activos? → Se debe generar una liquidación por cada contrato activo.
- ¿Qué sucede cuando el canon de mandato es 0? → Se debe generar la liquidación con comisión = 0, pero la liquidación debe crearse.
- ¿Qué sucede cuando la conexión a la base de datos falla durante la generación masiva? → Se debe registrar el error, continuar con los propietarios restantes, y reportar el resultado parcial.
- ¿Qué sucede cuando un contrato de mandato cambia de estado durante la generación masiva (carrera de condiciones)? → Se debe validar el estado al momento de la inserción, no al inicio del proceso.
- ¿Qué sucede cuando el período seleccionado tiene formato inválido? → Se debe validar antes de iniciar el proceso y mostrar un mensaje claro.

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE permitir generar liquidaciones individuales seleccionando una propiedad que tenga un Contrato de Mandato activo.
- **FR-002**: El sistema DEBE calcular automáticamente la comisión (canon × porcentaje / 10000), IVA (comisión × 19%), gastos de administración (desde la propiedad), y valor de incidentes pendientes (desde cuotas de incidentes de la propiedad).
- **FR-003**: El sistema DEBE permitir generar liquidaciones masivas para todos los propietarios con Contratos de Mandato activos en un solo paso, seleccionando solo el período.
- **FR-004**: El sistema DEBE validar que no exista una liquidación duplicada para el mismo contrato y período (restricción UNIQUE en base de datos).
- **FR-005**: El sistema DEBE manejar errores individuales durante la generación masiva sin interrumpir el proceso completo, clasificando cada resultado como: generada, omitida (ya existía liquidación para ese contrato/período), o error (fallo real). Los errores se registran en logs con ID del propietario, ID del contrato y causa.
- **FR-006**: El sistema DEBE mostrar un toast con tres contadores: "X generadas, Y ya existían, Z con error". Si Z = 0, el toast es informativo (no de error). Si Z > 0, el toast es de warning indicando que hubo fallos parciales.
- **FR-007**: El sistema DEBE filtrar propiedades disponibles en el formulario de creación individual para mostrar SOLO aquellas con Contrato de Mandato activo.
- **FR-008**: El sistema DEBE permitir la generación masiva incluso cuando todos los contratos ya tienen liquidaciones para el período, mostrando un toast informativo "0 generadas, N ya existían" sin clasificar como error.
- **FR-009**: El sistema DEBE registrar en los logs del servidor cada error específico durante la generación masiva (ID del propietario, mensaje de error, traceback).
- **FR-010**: El sistema DEBE persistir las liquidaciones generadas en estado "En Proceso" y permitir el flujo posterior de aprobación y pago.

### Key Entities

- **Liquidacion**: Registro contable mensual de una propiedad. Campos clave: id_liquidacion, id_contrato_m (FK), periodo (YYYY-MM), canon_bruto, comision_monto, iva_comision, gastos_administracion, valor_incidentes, neto_a_pagar, estado_liquidacion. Restricción: UNIQUE(ID_CONTRATO_M, PERIODO).
- **ContratoMandato**: Acuerdo entre propietario y empresa de administración. Campos relevantes: id_contrato_m, id_propiedad, id_propietario, canon_mandato, comision_porcentaje_contrato_m, estado_contrato_m.
- **Propiedad**: Inmueble administrado. Campos relevantes: id_propiedad, direccion_propiedad, valor_administracion.
- **Propietario**: Persona dueña de la propiedad. Relación: uno a muchos con ContratoMandato.
- **CuotaIncidente**: Cuota de pago de un incidente. Campos: id_cuota, id_liquidacion (nullable FK), valor_cuota, estado_pago. Relación: se asocia a liquidaciones durante la generación.

## Success Criteria

### Measurable Outcomes

- **SC-001**: La generación individual de liquidaciones funciona para el 100% de las propiedades con Contrato de Mandato activo (incluyendo "BRR EL SILENCIO ET 2 MZ D CS 4").
- **SC-002**: La generación masiva completa el proceso sin errores para al menos el 95% de los propietarios con contratos activos en un entorno de producción con datos reales.
- **SC-003**: Los mensajes de resultado durante la generación masiva son precisos: distinguen entre generadas, omitidas (duplicados) y errores (fallos reales), y los errores se registran en logs con detalles suficientes para diagnóstico.
- **SC-004**: El tiempo de ejecución de la generación masiva para 100 propietarios es menor a 30 segundos.
- **SC-005**: No se producen liquidaciones duplicadas (mismo contrato, mismo período) bajo ninguna circunstancia.
- **SC-006**: Los usuarios pueden completar el proceso de cierre mensual de liquidaciones (generación → aprobación → pago) sin errores bloqueantes.

## Clarifications

### Session 2026-07-15

- Q: ¿Qué nivel de detalle debe mostrar el sistema cuando la generación masiva tiene errores parciales? → A: Conteos + logs. El toast muestra generadas/omitidas/error; los detalles completos (ID propietario, contrato, causa) se registran en logs del servidor para diagnóstico.
- Q: ¿Cómo debe distinguir el sistema entre "ya existían" (informativo) y "fallo real" (error) en la generación masiva? → A: Contar como omitidas (no como error). Un contrato que ya tiene liquidación para el período se clasifica como "omitido", no como "error". El toast dice "X generadas, Y ya existían" sin mención de errores si no hubo fallos reales.

## Assumptions

- La base de datos PostgreSQL contiene datos de producción con propiedades, propietarios y contratos de mandato en diversos estados.
- La propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" tiene al menos un Contrato de Mandato con estado "ACTIVO" en la base de datos.
- El error "Hubo errores generando todas las liquidaciones" se produce porque TODOS los propietarios fallan durante la generación individual, no porque no existan propietarios elegibles.
- La consulta SQL que obtiene la lista de propietarios con contratos activos funciona correctamente (retorna resultados).
- El problema raíz está en la capa de servicio (`ServicioFinanciero.generar_liquidacion_propietario` o `generar_liquidacion_mensual`), no en la consulta de propietarios activos.
- Los parámetros de configuración (IVA_DEFAULT, IMPUESTO_4X1000) están correctamente configurados en la base de datos.
- La conexión a la base de datos está funcionando correctamente durante la ejecución.
- El código actual no tiene migraciones pendientes que afecten la estructura de tablas.
