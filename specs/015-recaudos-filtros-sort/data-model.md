# Data Model: Recaudos - Filtros Avanzados y Ordenamiento de Tabla

**Date**: 2026-07-05
**Feature**: 015-recaudos-filtros-sort

## Overview

Esta feature NO introduce nuevas entidades ni cambios en el esquema de base de datos. Trabaja con entidades existentes y sus relaciones ya establecidas. El modelo documentado aquí es la porción relevante del dominio para esta feature.

## Entities (Existing — No Schema Changes)

### Recaudo

Representa un pago recibido de un arrendatario.

| Field | Type | Description |
|-------|------|-------------|
| id_recaudo | int (PK) | Identificador único del recaudo |
| fecha_pago | date | Fecha en que se realizó el pago |
| fecha_pago_contrato | str | Periodo de pago del contrato (YYYY-MM) |
| valor_total | decimal | Monto total del pago |
| metodo_pago | str | Método utilizado (Efectivo, Transferencia, etc.) |
| estado | enum | Pendiente, Vencido, Aplicado, Reversado |
| id_contrato | int (FK) | Referencia al contrato de arrendamiento |

### Contrato de Arrendamiento

Contrato asociado a un recaudo.

| Field | Type | Description |
|-------|------|-------------|
| id_contrato | int (PK) | Identificador único del contrato |
| fecha_pago | str | Periodo de pago del contrato |

### Relaciones

```
Recaudo ──(id_contrato)──► Contrato de Arrendamiento
                              │
                              ├──► Propiedad (dirección, matrícula)
                              └──► Arrendatario (nombre, teléfono)
                                    └──► Habitante (nombre, teléfono)
```

## State Variables (Frontend — RecaudosState)

### Filtros

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| search_text | str | `""` | Búsqueda libre (propiedad, arrendatario, matrícula) |
| filter_estado | str | `"Todos"` | Filtro por estado del recaudo |
| filter_contrato | str | `""` | Filtro por ID de contrato (**nuevo en UI**) |
| filter_fecha_desde | str | `""` | Fecha de pago desde (YYYY-MM-DD) |
| filter_fecha_hasta | str | `""` | Fecha de pago hasta (YYYY-MM-DD) |

### Ordenamiento

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| sort_by | str | `"fecha_pago"` | Columna activa de ordenamiento |
| sort_order | str | `"desc"` | Dirección: "asc" o "desc" |

### Paginación

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| current_page | int | `1` | Página actual |
| page_size | int | `25` | Registros por página |
| total_items | int | `0` | Total de registros (calculado por backend) |

### Opciones de Filtros

| Variable | Type | Source | Description |
|----------|------|--------|-------------|
| contratos_options | List[Dict] | DB (load_filter_options) | Contratos activos con ID y etiqueta |
| contratos_select_options | List[str] | Derivado | Etiquetas para mostrar en dropdown |
| estado_options | List[str] | Hardcoded | ["Todos", "Pendiente", "Vencido", "Aplicado", "Reversado"] |

## FiltrosRecaudo (Backend — Dataclass Existente)

Estructura de datos que encapsula los filtros para la consulta al repositorio.

```python
@dataclass(frozen=True)
class FiltrosRecaudo:
    estado: Optional[EstadoRecaudo] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    id_contrato: Optional[int] = None    # ← Ya existe, soporta filtro Pago Contrato
    busqueda: Optional[str] = None
    sort_by: str = "fecha_pago"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 25
```

## SORT_COLUMNS Mapping (Backend — Existente)

Mapeo de columnas frontend → columnas SQL para ORDER BY.

| Frontend Key | SQL Column | Type |
|-------------|------------|------|
| id_recaudo | r.ID_RECAUDO | numérico |
| fecha_pago | r.FECHA_PAGO | fecha |
| fecha_pago_contrato | ca.FECHA_PAGO | texto |
| valor_total | r.VALOR_TOTAL | numérico |
| estado | r.ESTADO_RECAUDO | texto |
| arrendatario | per.NOMBRE_COMPLETO | texto |
| habitante | arr.NOMBRE_HABITANTE | texto |
| direccion | p.DIRECCION_PROPIEDAD | texto |

**No ordenable**: metodo_pago, Acciones

## Validation Rules

- `filter_contrato`: Si es `""` o `"Todos"`, se envía `None` al backend (sin filtrado)
- `filter_estado`: Si es `"Todos"`, se envía `None` al backend
- `sort_by`: Debe estar en `SORT_COLUMNS`; si no, el backend usa `"r.FECHA_PAGO"` por defecto
- `sort_order`: Solo `"asc"` o `"desc"`
- `current_page`: Mínimo 1
- `page_size`: Mínimo 1, máximo 100
