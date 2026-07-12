# Feature Specification: Agregar Columna MONTO COMISIÓN a Liquidaciones

**Feature Branch**: `feature/add-monto-comision-column`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Agregar una nueva columna en la tabla liquidaciones: MONTO COMISIÓN"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar MONTO COMISIÓN en tabla de liquidaciones (Priority: P1)

Como operador del sistema de liquidaciones, necesito ver la columna "MONTO COMISIÓN" en la tabla de liquidaciones para conocer el monto monetario de la comisión correspondiente a cada registro de liquidación.

**Why this priority**: Esta es la funcionalidad principal solicitada. Sin esta columna visible, el usuario no puede ver el monto de comisión en la tabla, lo cual es esencial para la operación diaria del sistema de liquidaciones. El valor ya persiste en la base de datos; solo es necesario exponerlo en la interfaz.

**Independent Test**: Puede probarse independientemente verificando que la tabla de liquidaciones renderiza correctamente con la columna MONTO COMISIÓN visible, entre CANON e IVA COMISIÓN.

**Acceptance Scenarios**:

1. **Given** que el usuario navega a la vista de liquidaciones, **When** la tabla se carga, **Then** la columna MONTO COMISIÓN aparece en la posición correcta entre CANON e IVA COMISIÓN.
2. **Given** que un registro de liquidación tiene un monto de comisión de $1,500.00, **When** se muestra en la tabla, **Then** la celda de MONTO COMISIÓN muestra el valor formateado como moneda (ej. $1,500.00).
3. **Given** que un registro de liquidación tiene monto de comisión igual a $0.00 o nulo (NULL en BD), **When** se muestra en la tabla, **Then** la celda muestra $0.00 (sin distinción visual entre NULL y cero).

---

### User Story 2 - Visualizar NETO A PAGAR incorporando MONTO COMISIÓN (Priority: P2)

Como operador financiero, necesito que el NETO A PAGAR en la tabla de liquidaciones refleje el MONTO COMISIÓN como un egreso (se resta), para que el saldo neto muestre el valor correcto de lo que se debe pagar al propietario.

**Why this priority**: El monto de comisión impacta directamente el cálculo del neto a pagar. Al mostrar la columna en la tabla, el usuario debe poder verificar que el NETO A PAGAR ya incorpora este descuento correctamente.

**Independent Test**: Puede probarse verificando que el NETO A PAGAR mostrado en la tabla coincide con el cálculo que incluye el MONTO COMISIÓN como egreso.

**Acceptance Scenarios**:

1. **Given** una liquidación con OTROS INGRESOS de $10,000, MONTO COMISIÓN de $1,500, IVA COMISIÓN de $240, GASTOS ADMIN de $500, GASTOS SERV de $300, GASTOS REP de $200, V. INCIDENTES de $100, PAGO PREDIAL de $0, OTROS EGRESOS de $0, **When** se muestra el NETO A PAGAR en la tabla, **Then** el valor refleja la resta del MONTO COMISIÓN como egreso.
2. **Given** una liquidación existente sin MONTO COMISIÓN (dato histórico), **When** se carga en la tabla, **Then** se muestra $0.00 y el NETO A PAGAR se mantiene con el valor existente.

---

### User Story 3 - Verificar origen del MONTO COMISIÓN (Priority: P3)

Como administrador del sistema, necesito que la columna MONTO COMISIÓN muestre el valor calculado a partir del porcentaje de comisión que se descuenta del canon de mandato, para verificar que el dato refleja correctamente la comisión acordada.

**Why this priority**: Permite validar que el dato mostrado en la tabla es consistente con la regla de negocio del porcentaje de comisión sobre el canon. El valor ya se calcula y persiste en el sistema; solo se expone en la tabla.

**Independent Test**: Puede probarse verificando que el MONTO COMISIÓN mostrado en la tabla coincide con el resultado de aplicar el porcentaje de comisión al canon de mandato del registro.

**Acceptance Scenarios**:

1. **Given** una liquidación con CANON de $10,000 y un porcentaje de comisión del 15%, **When** se muestra en la tabla, **Then** el MONTO COMISIÓN muestra $1,500.00 (15% de $10,000).
2. **Given** una liquidación con CANON de $0 o sin porcentaje de comisión definido, **When** se muestra en la tabla, **Then** el MONTO COMISIÓN muestra $0.00.

---

### Edge Cases

- ¿Qué sucede cuando el MONTO COMISIÓN es mayor que el CANON? El sistema debe permitirlo ya que el dato proviene del cálculo de negocio (porcentaje de comisión sobre canon).
- ¿Cómo maneja el sistema liquidaciones históricas que no tienen MONTO COMISIÓN? Se muestra $0.00 para visualización, sin alterar el NETO A PAGAR histórico.
- ¿Qué sucede si el porcentaje de comisión no está definido para una propiedad? El MONTO COMISIÓN se muestra como $0.00.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La tabla de liquidaciones MUST incluir la columna "MONTO COMISIÓN" posicionada entre las columnas CANON e IVA COMISIÓN. La tabla MUST soportar scroll horizontal cuando el contenido exceda el viewport.
- **FR-002**: La columna MONTO COMISIÓN MUST ser ordenable (ascendente/descendente) como las demás columnas numéricas de la tabla.
- **FR-003**: La columna MONTO COMISIÓN MUST mostrar valores formateados como moneda colombiana COP con símbolo $, separadores de miles y dos decimales (ej. $1,500.00).
- **FR-004**: La columna MONTO COMISIÓN MUST mostrar un tooltip al pasar el cursor con el porcentaje de comisión aplicado (ej. "15% sobre canon").
- **FR-005**: El sistema MUST mostrar el MONTO COMISIÓN como el valor calculado a partir del porcentaje de comisión sobre el canon de mandato.
- **FR-006**: El NETO A PAGAR MUST incorporar el MONTO COMISIÓN como un egreso (se resta) en el cálculo.
- **FR-007**: Liquidaciones históricas sin MONTO COMISIÓN MUST mostrar $0.00 sin alterar el NETO A PAGAR existente.

### Key Entities

- **Liquidación**: Representa el cálculo financiero de un ciclo operativo para una propiedad. Atributos relevantes: ID, Período, Ciclo Operativo, Propiedad, Canon, Monto Comisión (ya existe en BD, ahora visible), IVA Comisión, Otros Ingresos, Gastos Administrativos, Gastos Servicio, Gastos Reparación, Valor Incidentes, Pago Predial, Otros Egresos, Neto a Pagar, Estado Recaudo, Estado.
- **Comisión**: Valor monetario calculado a partir del porcentaje de comisión que se descuenta del canon de mandato. Se almacena como monto directo en la base de datos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La columna MONTO COMISIÓN es visible y legible en la tabla de liquidaciones en menos de 1 segundo después de cargar la vista.
- **SC-002**: El NETO A PAGAR mostrado en la tabla refleja correctamente el descuento del MONTO COMISIÓN como egreso en 100% de los registros.
- **SC-003**: Las liquidaciones históricas sin MONTO COMISIÓN muestran el valor por defecto ($0.00) sin alterar el cálculo del NETO A PAGAR existente.

## Assumptions

- El MONTO COMISIÓN es un valor que ya persiste en la base de datos, calculado a partir del porcentaje de comisión que se descuenta del canon de mandato.
- El MONTO COMISIÓN se incorpora como un egreso en el cálculo del NETO A PAGAR (se resta de los ingresos totales), dado que representa un cargo al propietario.
- El campo es opcional para registros históricos y tiene valor por defecto de $0.00.
- La columna se agrega sin afectar el orden existente de las demás columnas.
- No se requiere migración de datos históricos; los registros existentes simplemente mostrarán $0.00 en la nueva columna si no tienen valor calculado.
- No se requiere edición manual del MONTO COMISIÓN desde la interfaz; el valor se calcula automáticamente según la regla de negocio del porcentaje de comisión sobre el canon.

## Clarifications

### Session 2026-07-11

- Q: ¿Cómo se muestra NULL vs $0.00 en MONTO COMISIÓN? → A: Mostrar $0.00 tanto para NULL como para 0.00 (sin distinción visual).
- Q: ¿Qué símbolo de moneda se usa para MONTO COMISIÓN? → A: $ (Pesos Colombianos COP), formato: $1,500.00.
- Q: ¿Cómo se comporta el ancho de la columna en la tabla? → A: Scroll horizontal en la tabla si el contenido excede el viewport.
- Q: ¿La columna MONTO COMISIÓN debe ser ordenable? → A: Sí, ordenable (ascendente/descendente) como las demás columnas numéricas.
- Q: ¿Debe mostrar tooltip con porcentaje de comisión? → A: Sí, tooltip con el porcentaje de comisión aplicado (ej. "15% sobre canon").
