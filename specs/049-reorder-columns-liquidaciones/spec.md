# Feature Specification: Reordenar Columnas Tabla Liquidaciones

**Feature Branch**: `049-reorder-columns-liquidaciones`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Reestructurar el orden de las columnas de la tabla principal del módulo Liquidaciones, agrupando la información de forma lógica y priorizando la visualización de los conceptos financieros más relevantes, sin afectar la funcionalidad existente del módulo."

## Clarifications

### Session 2026-07-11

- Q: ¿Cómo manejar configuración personalizada de columnas guardada por usuarios? → A: Forzar nuevo orden como default; respetar configuración existente si el usuario no ha personalizado.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Análisis Financiero de Liquidaciones (Priority: P1)

Como administrador o asesor de la inmobiliaria, necesito que la tabla principal del módulo Liquidaciones presente las columnas en un orden lógico que me permita analizar rápidamente la información financiera de cada período, partiendo desde el identificador del registro hasta el resultado final (neto a pagar) y su estado.

**Why this priority**: Este es el uso principal del módulo. El orden actual de las columnas dificulta el análisis financiero al no seguir un flujo lógico de lectura (identificación → conceptos financieros → resultado → estado → acciones). La reorganización optimiza la experiencia de usuario y reduce el tiempo de análisis.

**Independent Test**: Puede ser verificado completamente al navegar al módulo Liquidaciones y confirmar que las 16 columnas aparecen en el orden especificado, con alineación correcta y legibilidad adecuada.

**Acceptance Scenarios**:

1. **Given** el usuario navega al módulo Liquidaciones, **When** se carga la tabla principal, **Then** las columnas se muestran en el orden: ID, Período, Ciclo Operativo, Canon, IVA Comisión, Otros Ingresos, Gastos Administración, Gastos Servicios, Gastos Reparaciones, Valor Incidentes, Pago Predial, Otros Egresos, Neto a Pagar, Estado Recaudo, Estado, Acciones.
2. **Given** la tabla está cargada con datos, **When** el usuario realiza scroll horizontal, **Then** el orden de columnas se mantiene consistente en todas las posiciones de scroll.
3. **Given** la tabla tiene múltiples registros, **When** el usuario revisa cada fila, **Then** la información de cada columna corresponde correctamente al campo de datos esperado (sin mezcla de datos entre columnas).

---

### User Story 2 - Funcionalidades de Tabla No Afectadas (Priority: P1)

Como usuario del módulo Liquidaciones, necesito que todas las funcionalidades existentes de la tabla (ordenamiento, búsqueda, filtros, paginación, exportación) continúen funcionando correctamente después de la reorganización de columnas.

**Why this priority**: La reorganización no debe introducir regresiones funcionales. Mantener la compatibilidad completa es crítico para la operación diaria del negocio.

**Independent Test**: Puede ser verificado ejecutando cada funcionalidad de la tabla (ordenamiento ascendente/descendente, búsqueda rápida, filtros avanzados, paginación, exportación) y confirmando que operan correctamente.

**Acceptance Scenarios**:

1. **Given** la tabla está cargada, **When** el usuario hace clic en el encabezado de una columna financiera (ej. Canon, Neto a Pagar), **Then** la tabla se ordena ascendente/descendente por esa columna sin errores.
2. **Given** la tabla está cargada, **When** el usuario utiliza la búsqueda rápida, **Then** los resultados se filtran correctamente independientemente del orden de columnas.
3. **Given** la tabla está cargada, **When** el usuario aplica filtros avanzados, **Then** los filtros operan sobre los datos correctos y la visualización se actualiza sin problemas.
4. **Given** la tabla está cargada, **When** el usuario exporta los datos (Excel, PDF, CSV), **Then** el archivo exportado contiene todas las columnas en el orden correcto con la información correspondiente.
5. **Given** la tabla está en vista de paginación, **When** el usuario navega entre páginas, **Then** el orden de columnas se mantiene consistente en todas las páginas.

---

### User Story 3 - Responsividad y Legibilidad (Priority: P2)

Como usuario del módulo Liquidaciones en diferentes dispositivos y resoluciones, necesito que la tabla sea legible y usable sin solapamientos, truncamientos innecesarios ni problemas de alineación, incluso con 16 columnas visibles.

**Why this priority**: La tabla contiene numerosas columnas y debe mantenerse legible en diferentes viewports. Una mala distribución visual degrada la experiencia de usuario.

**Independent Test**: Puede ser verificado ajustando el tamaño del navegador en diferentes resoluciones y confirmando que la tabla mantiene legibilidad y alineación correcta.

**Acceptance Scenarios**:

1. **Given** la tabla está cargada con 16 columnas, **When** el usuario visualiza la tabla en una resolución de escritorio amplia (1920px+), **Then** todas las columnas son visibles sin scroll horizontal o con scroll mínimo.
2. **Given** la tabla está cargada, **When** el usuario visualiza la tabla en una resolución media (1280px), **Then** el scroll horizontal funciona correctamente y las columnas mantienen alineación y espaciado adecuados.
3. **Given** la tabla está cargada, **When** el usuario hace hover sobre celdas con contenido largo, **Then** el contenido completo es accesible (tooltip o truncamiento con indicador visual).

---

### Edge Cases

- ¿Qué sucede cuando una columna financiera tiene valores nulos o vacíos? El sistema debe mostrar un valor por defecto (ej. $0 o "-") sin afectar la alineación.
- ¿Qué sucede cuando el usuario tiene configuración personalizada de columnas guardada? El nuevo orden se establece como default. Si el usuario nunca personalizó sus columnas, se le aplica el nuevo orden. Si el usuario tenía una configuración personalizada previa, se respeta su configuración (no se sobrescribe).
- ¿Cómo maneja el sistema el scroll horizontal en pantallas pequeñas con 16 columnas visibles? El scroll debe ser suave y la última columna (Acciones) siempre accesible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST mostrar las columnas de la tabla principal del módulo Liquidaciones en el orden exacto especificado: ID, Período, Ciclo Operativo, Canon, IVA Comisión, Otros Ingresos, Gastos Administración, Gastos Servicios, Gastos Reparaciones, Valor Incidentes, Pago Predial, Otros Egresos, Neto a Pagar, Estado Recaudo, Estado, Acciones.
- **FR-002**: El sistema MUST mantener la reorganización de columnas consistente en todas las vistas del módulo Liquidaciones que reutilicen la estructura de la tabla principal.
- **FR-003**: El sistema MUST preservar la fuente de datos de cada columna (cada columna debe seguir obteniendo su información desde su campo correspondiente en la base de datos).
- **FR-004**: El sistema MUST mantener la funcionalidad de ordenamiento ascendente/descendente para todas las columnas ordenables.
- **FR-005**: El sistema MUST mantener la funcionalidad de búsqueda rápida operando sobre todos los campos visibles.
- **FR-006**: El sistema MUST mantener la funcionalidad de filtros avanzados operando correctamente con el nuevo orden.
- **FR-007**: El sistema MUST mantener la paginación funcionando correctamente con el nuevo orden de columnas.
- **FR-008**: El sistema MUST mantener la exportación (Excel, PDF, CSV) generando archivos con las columnas en el orden correcto.
- **FR-009**: El sistema MUST mantener el scroll horizontal funcionando correctamente con 16 columnas.
- **FR-010**: El sistema MUST mostrar cada columna con alineación, espaciado y legibilidad adecuados, evitando solapamientos o truncamientos innecesarios.
- **FR-011**: La reorganización MUST no modificar la información mostrada en cada columna ni afectar las reglas de negocio existentes.
- **FR-012**: La reorganización MUST no introducir regresiones funcionales ni afectar el rendimiento del módulo.

### Key Entities

- **Liquidación**: Registro financiero que representa el estado de cuentas de un condominio en un período específico. Contiene identificador único, período, ciclo operativo, conceptos de ingresos (Canon, IVA Comisión, Otros Ingresos), conceptos de egresos (Gastos Administración, Gastos Servicios, Gastos Reparaciones, Valor Incidentes, Pago Predial, Otros Egresos), resultado neto (Neto a Pagar), estados de seguimiento (Estado Recaudo, Estado) y acciones disponibles.
- **Tabla Principal**: Componente de interfaz que presenta las liquidaciones en formato tabular con funcionalidades de ordenamiento, búsqueda, filtros, paginación y exportación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Las 16 columnas se visualizan exactamente en el orden especificado en el 100% de las vistas del módulo Liquidaciones.
- **SC-002**: Todas las funcionalidades de la tabla (ordenamiento, búsqueda, filtros, paginación, exportación) operan correctamente sin regresiones.
- **SC-003**: La interfaz mantiene distribución limpia y legible en resoluciones de 1280px y superiores sin solapamientos ni truncamientos innecesarios.
- **SC-004**: La información en cada columna corresponde al 100% a su fuente de datos original (sin mezcla de datos).
- **SC-005**: No se detectan errores en consola del navegador durante la interacción con la tabla reorganizada.

## Assumptions

- La tabla principal del módulo Liquidaciones actualmente existe y contiene columnas con los nombres especificados.
- La reorganización es puramente de presentación (orden visual) y no requiere cambios en la lógica de negocio ni en la capa de persistencia.
- Las columnas existentes mantienen sus fuentes de datos actuales; solo cambia el orden en que se renderizan.
- El módulo Liquidaciones es accesible para usuarios con roles de administrador y asesor.
- La aplicación actualmente soporta scroll horizontal para tablas con numerosas columnas.
- Si el usuario tiene configuración personalizada de columnas guardada, se respeta esa configuración. El nuevo orden solo se aplica como default para usuarios sin configuración personalizada previa.
