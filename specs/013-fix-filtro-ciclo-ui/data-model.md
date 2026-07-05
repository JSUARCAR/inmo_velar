# Data Model: fix-filtro-ciclo-ui

*Nota: Este proyecto no introduce nuevos modelos de datos. Sólo se corrige la referencia a una entidad existente.*

## Entities

### `Propiedad` (Existente)
Contiene la información de los inmuebles.

**Fields Relevantes:**
- `id_propiedad`: Primary Key.
- `grupo_operativo`: String/Varchar que indica el ciclo (ej. 'Ciclo 1', 'Ciclo 2'). Es la columna sobre la que se debe aplicar el filtro.

### `Liquidacion` (Existente)
Contiene la información de los pagos.

**Fields Relevantes:**
- `id_liquidacion`: Primary Key.
- `id_propiedad`: Foreign Key referenciando a `Propiedad`.

## Relationships
- **Liquidacion -> Propiedad**: Relación *Many-to-One* vinculada mediante el campo `id_propiedad`.

## Query Modification
La cláusula `WHERE` que filtra por `grupo_operativo` debe apuntar al alias `p` (de `Propiedad`), modificando `prop.GRUPO_OPERATIVO` a `p.GRUPO_OPERATIVO` para hacer join correcto dentro del motor de PostgreSQL en el repositorio `RepositorioLiquidacionPostgres`.
