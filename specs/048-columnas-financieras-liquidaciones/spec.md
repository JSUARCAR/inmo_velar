# Feature Specification: Columnas Financieras Liquidaciones

**Feature Branch**: `048-columnas-financieras-liquidaciones`

**Created**: 2026-07-11

**Status**: Draft

**Input**: User description: "Ingeniería inversa del módulo Liquidaciones para incorporar 8 nuevas columnas financieras después de Canon: Otros Ingresos, Gastos Administración, Gastos Servicios, Gastos Reparaciones, Valor Incidentes, Pago Predial, Otros Egresos, IVA Comisión"

## Clarifications

### Session 2026-07-11

- Q: ¿Cuál es el comportamiento exacto para valores monetarios vacíos o nulos? → A: Mostrar $0,00 (formato monetario estándar con decimales)
- Q: ¿En qué tabla de PostgreSQL se almacenan los datos de las nuevas columnas financieras? → A: Los 8 campos están en la misma tabla de liquidaciones (columnas existentes)
- Q: ¿Cuál es el tiempo máximo aceptable para cargar la tabla con todas las columnas financieras? → A: 3 segundos o menos para cargar la tabla completa
- Q: ¿Cómo deben mostrarse los valores vacíos ($0,00) en los archivos exportados? → A: Mostrar $0,00 en todos los formatos (consistente con tabla)
- Q: ¿Cómo debe funcionar el filtro para las columnas financieras? → A: Filtro por rango (monto mínimo y máximo) - estándar financiero

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización Completa de Datos Financieros (Priority: P1)

Como analista financiero de Inmobiliaria Velar, necesito ver una tabla de liquidaciones con información financiera detallada (incluyendo ingresos adicionales, gastos administrativos, servicios, reparaciones, incidentes, predial, otros egresos e IVA de comisión) para poder realizar análisis financieros precisos sin necesidad de consultar múltiples fuentes.

**Why this priority**: Es la funcionalidad core que justifica todo el feature. Sin la visualización correcta de todas las columnas, el resto de funcionalidades no tiene sentido.

**Independent Test**: Se puede probar cargando la tabla de liquidaciones y verificando que las 8 nuevas columnas aparecen después de "Canon" con los datos correctos de PostgreSQL.

**Acceptance Scenarios**:

1. **Given** que existen liquidaciones con datos completos en la base de datos, **When** el usuario carga la tabla de liquidaciones, **Then** las 8 nuevas columnas aparecen inmediatamente después de la columna "Canon" en el orden especificado.
2. **Given** que una liquidación tiene valores en todos los campos financieros, **When** el usuario visualiza la fila, **Then** cada columna muestra el valor correspondiente al campo financiero de esa liquidación.
3. **Given** que una liquidación no tiene valores en campos adicionales, **When** el usuario visualiza la fila, **Then** las columnas vacías muestran $0,00 o el comportamiento definido por las reglas de negocio.

---

### User Story 2 - Funcionalidades de Interacción con Columnas (Priority: P2)

Como administrador del sistema, necesito que las nuevas columnas participen en todas las funcionalidades existentes de la tabla (ordenamiento, búsqueda, filtros, paginación y exportación) para mantener una experiencia de usuario consistente.

**Why this priority**: Garantiza que las nuevas columnas no rompan la experiencia existente y que los usuarios puedan interactuar con la información de la misma forma que con las columnas actuales.

**Independent Test**: Se puede probar ordenando por cada una de las nuevas columnas, aplicando filtros y exportando a Excel/PDF/CSV para verificar que los datos se mantienen consistentes.

**Acceptance Scenarios**:

1. **Given** que la tabla tiene datos con las nuevas columnas, **When** el usuario ordena por cualquier columna financiera, **Then** los registros se ordenan correctamente de forma ascendente o descendente.
2. **Given** que existen liquidaciones con diferentes valores financieros, **When** el usuario aplica un filtro en una columna financiera, **Then** solo se muestran los registros que coinciden con el criterio de filtro.
3. **Given** que la tabla tiene múltiples páginas de datos, **When** el usuario exporta a Excel, **Then** todas las columnas financieras se incluyen en el archivo exportado con los valores correctos.

---

### User Story 3 - Consistencia y Calidad Visual (Priority: P3)

Como usuario del sistema, necesito que el formato de presentación de los valores monetarios sea uniforme en todas las nuevas columnas (separadores de miles, decimales, alineación y formato de moneda) para una fácil lectura y comparación de datos.

**Why this priority**: Asegura una experiencia visual profesional y consistente con el resto del sistema.

**Independent Test**: Se puede probar verificando que todos los valores monetarios muestran el formato correcto ($XX.XXX,XX) y están alineados consistentemente.

**Acceptance Scenarios**:

1. **Given** que existen valores monetarios diferentes en las columnas, **When** el usuario visualiza la tabla, **Then** todos los valores muestran formato monetario uniforme (ej: $1.250.000,00).
2. **Given** que una columna tiene valores de diferentes magnitudes, **When** el usuario compara visualmente, **Then** los valores están alineados correctamente para facilitar la comparación.
3. **Given** que el usuario cambia el tamaño de la ventana del navegador, **When** la tabla se redimensiona, **Then** las columnas mantienen su formato y legibilidad.

---

### Edge Cases

- ¿Qué sucede cuando una liquidación no tiene valor en "Valor Incidentes" pero tiene incidentes asociados?
- ¿Cómo maneja el sistema liquidaciones con múltiples incidentes que afectan el mismo concepto financiero?
- ¿Qué ocurre cuando el usuario exporta a diferentes formatos y hay columnas con valores vacíos?
- ¿Cómo se comporta la búsqueda rápida cuando el usuario busca por un valor monetario específico?
- ¿Qué sucede cuando la tabla tiene miles de registros y se ordena por una columna financiera?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La tabla principal de Liquidaciones DEBE mostrar las 8 nuevas columnas inmediatamente después de la columna "Canon" en el siguiente orden: Otros Ingresos, Gastos Administración, Gastos Servicios, Gastos Reparaciones, Valor Incidentes, Pago Predial, Otros Egresos, IVA Comisión.
- **FR-002**: Cada columna DEBE mostrar únicamente la información correspondiente al registro de liquidación, proveniente directamente de la fuente oficial en PostgreSQL.
- **FR-003**: Los valores monetarios DEBEN presentarse utilizando el formato financiero definido por el sistema (separadores de miles, decimales, alineación y formato de moneda).
- **FR-004**: En caso de que un valor no exista o sea nulo, la interfaz DEBE mostrar **$0,00** (formato monetario estándar con decimales).
- **FR-005**: Las nuevas columnas DEBEN participar en las funcionalidades de ordenamiento ascendente y descendente.
- **FR-006**: Las nuevas columnas DEBEN participar en la búsqueda rápida del sistema.
- **FR-007**: Las nuevas columnas DEBEN participar en los filtros avanzados de la tabla utilizando filtro por rango (monto mínimo y máximo) para columnas monetarias.
- **FR-008**: Las nuevas columnas DEBEN incluirse en la paginación de la tabla.
- **FR-009**: Las nuevas columnas DEBEN incluirse en todas las exportaciones soportadas (Excel, PDF, CSV), mostrando $0,00 para valores vacíos (consistente con la visualización en tabla).
- **FR-010**: La información DEBE mantenerse sincronizada entre PostgreSQL, el backend y la UI/UX.
- **FR-011**: El rendimiento de la tabla NO DEBE degradarse de manera perceptible tras la incorporación de las nuevas columnas.
- **FR-012**: La implementación DEBE mantener la consistencia visual y funcional con el resto de tablas del sistema.
- **FR-013**: NO DEBEN introducirse regresiones en ninguna funcionalidad existente del módulo.
- **FR-014**: Las columnas DEBEN ser compatibles con scroll horizontal y vertical.
- **FR-015**: Si existe carga diferida (Lazy Loading o Virtual Scrolling), las nuevas columnas DEBEN ser compatibles con esta funcionalidad.

### Key Entities

- **Liquidación**: Representa un registro financiero que contiene múltiples conceptos económicos (canon, ingresos adicionales, gastos, incidentes, etc.). Cada liquidación está asociada a un contrato y ciclo operativo específico.
- **Columna Financiera**: Campo de datos monetario que representa un concepto económico específico dentro de una liquidación. Cada columna tiene un nombre, un tipo de dato (monetario) y un comportamiento de presentación definido.
- **Fuente Oficial**: Los 8 campos financieros están almacenados como columnas directas en la tabla de liquidaciones de PostgreSQL. No requieren joins ni cálculos adicionales.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La tabla de liquidaciones muestra las 8 nuevas columnas con datos correctos en menos de 2 segundos de carga.
- **SC-002**: El 100% de las columnas financieras participan correctamente en ordenamiento, búsqueda, filtros y exportación.
- **SC-003**: El formato monetario es uniforme en todas las columnas (verificado visualmente en 100% de los casos de prueba).
- **SC-004**: No hay regresiones en funcionalidades existentes del módulo Liquidaciones (verificado por tests de regresión).
- **SC-005**: La exportación a Excel/PDF/CSV incluye todas las nuevas columnas con los valores correctos.
- **SC-006**: La tabla completa con las 8 columnas financieras adicionales carga en 3 segundos o menos.
- **SC-007**: Los valores en la UI coinciden al 100% con los datos almacenados en PostgreSQL.
- **SC-008**: La tabla es visualmente consistente con el resto de tablas del sistema en diferentes resoluciones de pantalla.

## Assumptions

- La estructura actual de la tabla de liquidaciones ya existe y es funcional.
- Las columnas solicitadas corresponden a campos existentes en la base de datos PostgreSQL.
- El formato monetario del sistema ya está definido y es consistente en otras partes de la aplicación.
- Las funcionalidades de ordenamiento, búsqueda, filtros, paginación y exportación ya están implementadas para las columnas existentes.
- El módulo Liquidaciones es accesible solo para usuarios con permisos específicos (administradores y analistas financieros).
- Los datos en PostgreSQL son la fuente oficial y no deben ser calculados en la interfaz.
- La arquitectura del sistema sigue el patrón Clean Architecture definido en la constitución del proyecto.
- El sistema utiliza Reflex para la presentación y PostgreSQL para la persistencia.
