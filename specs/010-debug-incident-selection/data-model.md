# Data Model & Interfaces: debug-incident-selection

Este bugfix no altera el modelo de base de datos, pero interactúa con las siguientes entidades a nivel de estado (Reflex State):

## Entidades Afectadas

### Incidente (Vista / Estado)
- Se requiere consultar la lista de incidentes.
- **Regla de Filtrado**: `estado_pago != 'Pagado'` (Pendiente, Vencido, etc.)
- **Campos mínimos requeridos por la UI**: ID, Descripción, Monto, Estado.

### Liquidación (Vista / Estado)
- Liquidación actual en edición.
- Relación: 1 a N con incidentes (a través de una tabla asociativa o campo).
