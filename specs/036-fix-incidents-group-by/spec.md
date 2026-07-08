# Feature Specification: Corrección GROUP BY en Módulo Incidentes

**Feature Branch**: `036-fix-incidents-group-by`

**Created**: 2026-07-08

**Status**: Draft

**Input**: User description: "Corregir error de PostgreSQL GROUP BY en el módulo Incidentes que impide la carga de información. El error indica que la columna cot.cotizaciones debe aparecer en GROUP BY o usarse en una función de agregación."

## Clarifications

### Session 2026-07-08

- Q: ¿Qué visibilidad se necesita cuando la consulta falla o tiene bajo rendimiento en producción? → A: Log de errores de consulta + tiempo de ejecución al sistema de logging existente.
- Q: ¿Cuántos módulos adicionales deben verificarse durante las pruebas de regresión? → A: Verificación de módulos que consumen datos de incidentes (Liquidaciones, Reportes).
- Q: ¿Existe una preferencia por la estrategia de agregación JSON para resolver el GROUP BY? → A: LATERAL JOIN + JSON_AGG como estrategia preferida.
- Q: ¿Cómo debe validarse el criterio de rendimiento durante las pruebas? → A: EXPLAIN ANALYZE directo en PostgreSQL para evidencia técnica objetiva.
- Q: ¿Cuál es el alcance esperado de la búsqueda de la consulta defectuosa? → A: Toda la cadena: repository → service → state de Reflex.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carga Exitosa de Incidentes (Priority: P1)

Como usuario del sistema inmobiliario, quiero acceder al módulo de Incidentes y visualizar la lista completa de incidentes con su información asociada (cotizaciones, estados, fechas) para poder gestionar y dar seguimiento a los casos.

**Why this priority**: Esta es la funcionalidad core del módulo. Sin ella, el módulo es completamente inutilizable. Es un bloqueador total de operación.

**Independent Test**: Puede ser probada independientemente al navegar al módulo Incidentes y verificar que la lista carga sin errores y muestra registros con sus cotizaciones.

**Acceptance Scenarios**:

1. **Given** que el usuario está autenticado en el sistema, **When** navega al módulo Incidentes, **Then** se muestra la lista de incidentes sin errores de carga.
2. **Given** que existen incidentes con cotizaciones asociadas, **When** se carga el módulo, **Then** las cotizaciones aparecen correctamente asociadas a cada incidente.
3. **Given** que no existen incidentes registrados, **When** se carga el módulo, **Then** se muestra un mensaje indicando que no hay incidentes disponibles.
4. **Given** que un incidente tiene múltiples cotizaciones, **When** se visualiza en la lista, **Then** todas las cotizaciones se muestran sin duplicación de registros.

---

### User Story 2 - Integridad de Datos en Consulta (Priority: P1)

Como administrador del sistema, quiero que la consulta SQL del módulo Incidentes sea completamente válida y cumpla con las reglas de PostgreSQL, para garantizar la consistencia y confiabilidad de los datos mostrados.

**Why this priority**: La corrección técnica es requisito indispensable para que la funcionalidad operé correctamente. Sin esto, el sistema expone errores técnicos al usuario final.

**Independent Test**: Puede ser probada ejecutando la consulta SQL directamente contra la base de datos y verificando que retorna resultados sin errores de GROUP BY.

**Acceptance Scenarios**:

1. **Given** que la consulta incluye la tabla de cotizaciones, **When** se ejecuta contra PostgreSQL, **Then** no se genera error de GROUP BY.
2. **Given** que se usan funciones de agregación para datos JSON, **When** se procesan las cotizaciones, **Then** los resultados son consistentes y sin duplicación.
3. **Given** que existen incidentes sin cotizaciones asociadas, **When** se ejecuta la consulta, **Then** se retornan los incidentes con un array vacío de cotizaciones.

---

### User Story 3 - Rendimiento de Consulta (Priority: P2)

Como usuario del sistema, quiero que la carga del módulo Incidentes sea rápida y eficiente, para no perder productividad al interactuar con la plataforma.

**Why this priority**: El rendimiento impacta directamente la experiencia del usuario y la productividad operativa. Una consulta optimizada evita tiempos de espera innecesarios.

**Independent Test**: Puede ser probada ejecutando EXPLAIN ANALYZE directamente en PostgreSQL y verificando que el tiempo de ejecución está dentro de umbrales aceptables (< 3 segundos para 1000 registros).

**Acceptance Scenarios**:

1. **Given** que existen 1000 incidentes en el sistema, **When** se carga el módulo, **Then** la información se muestra en menos de 3 segundos.
2. **Given** que la consulta utiliza subconsultas o LATERAL JOIN, **When** se analiza el plan de ejecución, **Then** se utilizan índices adecuados y no se realizan escaneos completos de tablas.

---

### Edge Cases

- ¿Qué sucede cuando un incidente tiene más de 100 cotizaciones asociadas? La consulta debe manejar este escenario sin degradación significativa.
- ¿Cómo maneja el sistema incidentes con cotizaciones que tienen datos JSON malformados o nulos? El COALESCE debe manejar estos casos correctamente.
- ¿Qué ocurre cuando se eliminan cotizaciones mientras se está cargando el módulo? La consulta debe ser consistente (snapshot consistente).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load the Incidents module without SQL errors related to GROUP BY clause.
- **FR-002**: System MUST correctly aggregate JSON data from the cotizaciones table using LATERAL JOIN with JSON_AGG to avoid duplication and handle One-to-Many relationships.
- **FR-003**: System MUST handle incidents with zero associated cotizaciones, returning an empty JSON array for those cases.
- **FR-004**: System MUST ensure no duplicate records are returned when an incident has multiple cotizaciones.
- **FR-005**: System MUST maintain data integrity across all entity relationships (incidentes, cotizaciones, and related entities).
- **FR-006**: System MUST optimize the query to use available indexes and avoid full table scans.
- **FR-007**: System MUST handle NULL values in cotizaciones column gracefully using COALESCE.
- **FR-008**: System MUST not introduce regressions in other modules that depend on incident data.

### Key Entities

- **Incidente**: Representa un caso o incidencia inmobiliaria. Contiene información base como ID, descripción, estado, fechas y relaciones con otras entidades.
- **Cotización**: Representa una propuesta comercial asociada a un incidente. Contiene datos JSON con detalles de la cotización.
- **Relación Incidente-Cotización**: Un incidente puede tener múltiples cotizaciones (relación uno-a-muchos).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Incidents module loads successfully without any SQL exceptions in 100% of attempts.
- **SC-002**: The query returns results in under 3 seconds for up to 1000 incident records, validated via EXPLAIN ANALYZE in PostgreSQL.
- **SC-003**: All cotizaciones are displayed correctly without duplication for incidents with multiple associated cotizaciones.
- **SC-004**: Incidents without cotizaciones show an empty array (not null or missing data).
- **SC-005**: No regressions detected in Liquidaciones and Reportes modules that query incident data.
- **SC-006**: PostgreSQL query plan uses indexed lookups instead of sequential scans for the main query path.
- **SC-007**: Query errors and execution time are logged to the existing logging system for production monitoring.
- **SC-008**: The defect is located by tracing the full data chain: repository → service → Reflex state.

## Assumptions

- The PostgreSQL database is accessible and properly configured in the production environment.
- The existing entity relationships (incidentes to cotizaciones) are correctly modeled in the database schema.
- The error is isolated to the query layer and does not indicate broader data corruption.
- The fix should be applied at the repository/data access layer without requiring changes to the UI components.
- Performance requirements assume standard hardware configuration (Railway Pro plan or equivalent).
- The solution must maintain backward compatibility with existing API consumers.
- The defect search scope covers the full data chain: repository → service → Reflex state.
