# Phase 1: Data Model & Entities

## Entity: CuotaIncidente (Existing)

Ubicada en `src/dominio/entidades/cuota_incidente.py`.

### Atributos relevantes para el filtro:

- `estado_pago` (str): Estado de la cuota. Valores válidos actualmente:
  - `"Pendiente"`
  - `"Asociada"`
  - `"Pagada"`

### Integración con Filtro UI

El componente Select/ComboBox de Reflex requiere recibir una lista de opciones de tipo `list[str]`. 

La lista dinámica se compondrá de:
```python
OPCIONES_FILTRO_PAGO = ["Todos", "Pendiente", "Asociada", "Pagada"]
```

*Nota:* Si el dominio evoluciona para usar `Enum` en el futuro, el filtro simplemente deberá mapear `[e.value for e in EstadoPago]` más `"Todos"`. De momento, como son strings quemados en los métodos de la entidad, se consolidarán para inyectarlos en la UI.
