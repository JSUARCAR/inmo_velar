# Data Model: Liquidaciones & Incidentes

This bugfix operates on the existing data model. No database schema changes are introduced.

## Entities Involved

### `LIQUIDACIONES`
- Primary Key: `id_liquidacion`
- Contains:
  - `id_contrato_m`
  - `periodo`
  - `estado` (e.g., 'En Proceso', 'Pagada')

### `INCIDENTES`
- Primary Key: `id_incidente`
- Contains:
  - `descripcion_incidente`
  - `costo_incidente`
  - `estado`
  - `estado_pago`
  - `id_propiedad`

### `INCIDENTE_LIQUIDACION` (Join Table)
- Primary Key: `id_relacion`
- Foreign Keys: `id_incidente`, `id_liquidacion`
- Contains:
  - `valor_descuento`

## State Objects (Reflex)

### `incidentes_asociados_liquidacion`
A list of dictionaries representing the incidents associated with the currently editing liquidation:
```python
{
    "id": int,
    "descripcion": str,
    "estado": str,
    "estado_pago": str,
    "valor_descuento": float,
    "valor_descuento_view": str,
}
```

### `seleccion_incidentes_disponibles`
A list of dictionaries representing incidents eligible to be associated to the current liquidation:
```python
{
    "id": int,
    "descripcion": str,
    "costo": float,
    "costo_view": str,
    "estado": str,
    "estado_pago": str,
    "propiedad": str,
    "propietario": str,
    "num_cuota": int,
    "valor_cuota": float,
    "valor_cuota_view": str,
    "ya_asociado": bool,
}
```
