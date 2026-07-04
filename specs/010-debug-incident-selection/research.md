# Research & Decisions: debug-incident-selection

## Unknown 1: ¿Por qué no se abre el modal "Seleccionar Incidentes"?
- **Decision**: Revisar dos posibles causas raíz: 
  1) Problema de estado en Reflex: El manejador del clic no está cambiando la variable booleana que controla la visibilidad (`is_open = True`).
  2) Problema de anidamiento Radix UI / CSS: Según la Constitución (Sección 16), un modal dentro de un *Portal* o *Dialog* hereda `pointer-events: none` y puede quedar bloqueado o detrás del modal principal por falta de un `z-index` adecuado.
- **Rationale**: Los errores más comunes en Reflex relacionados con diálogos que no se abren radican en fallos de mutación de estado o restricciones de Radix UI cuando se anidan popovers/dialogs.
- **Alternatives considered**: Error de red. Sin embargo, si no hay indicador visual de red ni errores de log evidentes, es más probable un fallo de estado/CSS.

## Unknown 2: Filtrado de incidentes
- **Decision**: El backend o el estado debe asegurar que los incidentes devueltos a la UI excluyan aquellos con `estado_pago == 'Pagado'`.
- **Rationale**: Requerimiento funcional FR-003.
