# Contract: Liquidaciones Table Interface

**Date**: 2026-07-11
**Feature**: 048-columnas-financieras-liquidaciones

## Overview

Define el contrato de datos entre el Estado (LiquidacionesState) y la UI (tabla de liquidaciones).

## Table Data Contract

### Column Definition Structure

```python
# Cada columna de la tabla debe seguir esta estructura
ColumnDef = {
    "key": str,              # Identificador único de la columna
    "header": str,           # Texto del encabezado
    "sortable": bool,        # Si permite ordenamiento
    "filterable": bool,      # Si permite filtrado
    "width": str,            # Ancho CSS (ej: "120px", "15%")
    "align": str,            # "left" | "center" | "right"
    "format": str,           # "text" | "currency" | "date" | "badge"
}
```

### Financial Column Specifications

| Column Key | Header | Sortable | Filterable | Width | Align | Format |
|------------|--------|----------|------------|-------|-------|--------|
| otros_ingresos | Otros Ingresos | true | true | "120px" | "right" | "currency" |
| gastos_administracion | Gastos Administración | true | true | "140px" | "right" | "currency" |
| gastos_servicios | Gastos Servicios | true | true | "120px" | "right" | "currency" |
| gastos_reparaciones | Gastos Reparaciones | true | true | "130px" | "right" | "currency" |
| valor_incidentes | Valor Incidentes | true | true | "120px" | "right" | "currency" |
| pago_predial | Pago Predial | true | true | "100px" | "right" | "currency" |
| otros_egresos | Otros Egresos | true | true | "110px" | "right" | "currency" |
| iva_comision | IVA Comisión | true | true | "100px" | "right" | "currency" |

### Column Order (post-Canon)

```
1. ID
2. Periodo
3. Propiedad
4. Ciclo Operativo
5. Canon
6. Otros Ingresos          ← NUEVA
7. Gastos Administración   ← NUEVA
8. Gastos Servicios        ← NUEVA
9. Gastos Reparaciones     ← NUEVA
10. Valor Incidentes       ← NUEVA
11. Pago Predial           ← NUEVA
12. Otros Egresos          ← NUEVA
13. IVA Comisión           ← NUEVA
14. Neto a Pagar
15. Estado Recaudo
16. Estado
17. Acciones
```

## Filter Contract

### Range Filter Structure

```python
# Filtro por rango para columnas monetarias
RangeFilter = {
    "column_key": str,       # Identificador de la columna
    "min_value": float | None,  # Valor mínimo (None = sin límite)
    "max_value": float | None,  # Valor máximo (None = sin límite)
}
```

### Supported Filter Operations

| Operation | Applicable Columns | Description |
|-----------|-------------------|-------------|
| range | All financial columns | Filter by min/max value |
| search | All text columns | Full-text search |
| exact | Estado, Ciclo | Exact match |
| date_range | Periodo | Date range filter |

## Export Contract

### Export Payload Structure

```python
# Payload para exportación
ExportPayload = {
    "columns": List[str],    # Lista de columnas a exportar
    "data": List[Dict],      # Datos formateados
    "format": str,           # "excel" | "pdf" | "csv"
}
```

### Export Column Mapping

| Column Key | Export Header | Export Format |
|------------|---------------|---------------|
| otros_ingresos | Otros Ingresos | Currency |
| gastos_administracion | Gastos Administración | Currency |
| gastos_servicios | Gastos Servicios | Currency |
| gastos_reparaciones | Gastos Reparaciones | Currency |
| valor_incidentes | Valor Incidentes | Currency |
| pago_predial | Pago Predial | Currency |
| otros_egresos | Otros Egresos | Currency |
| iva_comision | IVA Comisión | Currency |

## Sort Contract

### Sort Parameters

```python
# Parámetros de ordenamiento
SortParams = {
    "sort_by": str,          # Column key para ordenar
    "sort_order": str,       # "asc" | "desc"
}
```

### Sort Behavior

- **Currency columns**: Sort by numeric value (not formatted string)
- **Default order**: Descending for financial columns
- **Stable sort**: Maintain existing order for equal values
