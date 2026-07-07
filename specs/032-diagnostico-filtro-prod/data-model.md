# Data Model: Sincronización y Diagnóstico de Filtro de Estado de Pago en Producción

*(Nota: Esta operación no altera el modelo de datos, únicamente expone un filtrado ya implementado en frontend/backend hacia el entorno de producción)*

## Entidades Principales Afectadas (En despliegue)

- **CuotaIncidente**: Los estados ('Pendiente', 'Asociada', 'Pagada') se exponen en la UI.
- **Incidente**: La vista de `incidentes.py` recibe la actualización del componente `Select` (`ComboBox`).
