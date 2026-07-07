# Phase 0: Outline & Research

## Research Findings

Dado que el entorno técnico, de dominio y de base de datos están completamente especificados y mapeados, no se detectan "NEEDS CLARIFICATION" que ameriten una investigación profunda. La fuente de verdad para los estados ha sido validada.

### Decision: Extraer estados directamente de `CuotaIncidente`
- **Rationale**: En la entidad `CuotaIncidente` ubicada en `src/dominio/entidades/cuota_incidente.py`, los estados se manejan como cadenas de texto ("Pendiente", "Asociada", "Pagada") y métodos (`esta_pendiente()`, etc.). Para alimentar el `ComboBox` de Reflex de manera idiomática, se utilizará una lista de opciones que incluya "Todos" junto con las extraídas del dominio.
- **Alternatives considered**: Hardcodear las listas en la presentación. Fue rechazado por la regla de oro de Clean Architecture, donde la presentación debe depender del dominio para evitar discrepancias futuras.

### Decision: Flujo de Estado en `estado_incidentes.py`
- **Rationale**: El estado centralizado del módulo de Incidentes (probablemente `EstadoIncidentes` o similar en la capa de presentación) debe almacenar la variable reactiva `filtro_estado_pago`. Este valor será recolectado y enviado a la capa de aplicación/infraestructura.
- **Alternatives considered**: Estado local en el componente de filtros. Rechazado por el mandato de tener "State management centralizado usando mutaciones atómicas".
