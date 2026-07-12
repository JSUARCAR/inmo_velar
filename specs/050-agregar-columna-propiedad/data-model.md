# Data Model: Agregar Columna PROPIEDAD a Tabla de Recaudos

**Date**: 2026-07-11
**Feature**: 050-agregar-columna-propiedad

## Entidades Existentes

### Recaudo

**Tabla**: `recaudos` (PostgreSQL)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_recaudo | UUID | Identificador único |
| fecha_pago | DATE | Fecha de pago |
| fecha_pago_contrato | DATE | Fecha de pago según contrato |
| ciclo_operativo | VARCHAR | Ciclo operativo del recaudo |
| propiedad_id | UUID | FK → propiedades.id (campo existente) |
| valor_total | DECIMAL | Valor total del recaudo |
| metodo_pago | VARCHAR | Método de pago |
| estado | VARCHAR | Estado del recaudo |

### Propiedad

**Tabla**: `propiedades` (PostgreSQL)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único |
| direccion | VARCHAR | Dirección de la propiedad (nombre visible) |
| propietario | VARCHAR | Nombre del propietario |
| matricula | VARCHAR | Matrícula inmobiliaria |

## Relación

```
recaudos.propiedad_id → propiedades.id (FK)
```

**Tipo**: Muchos a uno (muchos recaudos pueden pertenecer a una propiedad)

## Campos para la Columna PROPIEDAD

### Campo Principal
- **direccion**: Se muestra como nombre de la propiedad en la columna

### Campo Secundario (opcional)
- **matricula**: Se muestra debajo de la dirección como referencia

## Queries Necesarias

### Listar Recaudos con Propiedad (ya existente)

```sql
SELECT 
    r.*,
    p.direccion AS propiedad_direccion,
    p.matricula AS propiedad_matricula
FROM recaudos r
LEFT JOIN propiedades p ON r.propiedad_id = p.id
WHERE [filtros]
ORDER BY [sort_by] [sort_order]
LIMIT [limit] OFFSET [offset];
```

### Filtrar por Propiedad

```sql
WHERE p.direccion ILIKE '%busqueda%'
   OR p.id = :propiedad_id
```

### Opciones de Filtro (para dropdown)

```sql
SELECT DISTINCT p.id, p.direccion
FROM propiedades p
INNER JOIN recaudos r ON r.propiedad_id = p.id
ORDER BY p.direccion;
```

## Validaciones

1. **propiedad_id nullable**: Un recaudo puede no tener propiedad asociada
2. **direccion nullable**: Una propiedad puede no tener dirección registrada
3. **Fallback**: Si `direccion` es NULL, mostrar `propiedad_id` o "Sin dirección"

## Impacto en Estado (RecaudosState)

### Variables Existentes (no requieren cambios)
- `sort_by`: Ya soporta `direccion` como valor
- `sort_order`: Ya funciona con asc/desc

### Variables Nuevas (requieren agregar)
- `filter_propiedad: List[str]` - IDs de propiedades seleccionadas
- `propiedad_options: List[Dict]` - Opciones para el dropdown de filtro

### Métodos Nuevos
- `set_filter_propiedad(value: str)` - Establece filtro de propiedad
- `toggle_filter_propiedad(value: str)` - Agrega/quita propiedad del filtro
- `load_propiedad_options()` - Carga opciones de propiedad para filtro
