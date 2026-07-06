# Data Model: move-responsable-deposito

## PostgreSQL Migrations

Se requerirá correr una instrucción SQL directamente sobre la base de datos de producción (usualmente a través del cliente PostgreSQL en Railway) para ajustar el esquema.

```sql
-- Eliminar de Mandatos
ALTER TABLE "CONTRATOS_MANDATOS" DROP COLUMN IF EXISTS responsable_deposito_id;

-- Agregar a Arrendamientos
ALTER TABLE "CONTRATOS_ARRENDAMIENTOS" 
ADD COLUMN IF NOT EXISTS responsable_deposito_id INTEGER REFERENCES "ASESORES"(id) ON DELETE SET NULL;
```

## Domain Entities Updates

### `ContratoMandato`
Se remueve:
```python
responsable_deposito_id: Optional[int] = None
```

### `ContratoArrendamiento`
Se añade:
```python
responsable_deposito_id: Optional[int] = None
```

## Application DTOs Updates

### `ContratoMandatoBase` o Equivalentes (Pydantic)
- Se remueve `responsable_deposito_id`.

### `ContratoArrendamientoBase` o Equivalentes (Pydantic)
- Se añade `responsable_deposito_id: Optional[int] = Field(default=None)`.

## Repositories & SQL Logic

- `repositorio_contrato_mandato_postgres.py`: Remover `responsable_deposito_id` de las listas de columnas en los `INSERT` y `UPDATE`.
- `repositorio_contrato_arrendamiento_postgres.py`: Agregar `responsable_deposito_id` a las consultas `INSERT` y `UPDATE`.
- `servicio_contratos.py` (`obtener_detalle_contrato_ui`): Modificar la lógica para buscar al asesor responsable de depósito únicamente si el contrato es tipo Arrendamiento.
