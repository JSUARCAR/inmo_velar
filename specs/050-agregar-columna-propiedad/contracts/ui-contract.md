# UI Contract: Tabla de Recaudos - Columna PROPIEDAD

**Date**: 2026-07-11
**Feature**: 050-agregar-columna-propiedad

## Componente: Tabla de Recaudos

### Estructura de Columnas

```typescript
interface ColumnaRecaudo {
  id: string;           // Identificador único de la columna
  label: string;        // Nombre visible en el header
  sortable: boolean;    // Si la columna permite ordenamiento
  width?: string;       // Ancho opcional (ej: "150px", "20%")
  hidden_mobile?: boolean; // Si se oculta en móvil
}

// Columnas definidas
const COLUMNAS: ColumnaRecaudo[] = [
  { id: "id_recaudo", label: "ID", sortable: true },
  { id: "fecha_pago", label: "Fecha Pago", sortable: true },
  { id: "fecha_pago_contrato", label: "Pago Contrato", sortable: true },
  { id: "ciclo_operativo", label: "Ciclo Operativo", sortable: true },
  { id: "direccion", label: "Propiedad", sortable: true },  // ← COLUMNA OBJETIVO
  { id: "arrendatario", label: "Arrendatario", sortable: true },
  { id: "habitante", label: "Habitante", sortable: true, hidden_mobile: true },
  { id: "valor_total", label: "Valor", sortable: true },
  { id: "metodo_pago", label: "Metodo", sortable: false },
  { id: "estado", label: "Estado", sortable: true },
  { id: "acciones", label: "Acciones", sortable: false, width: "120px" },
];
```

### Estado del Componente

```typescript
interface RecaudosState {
  // Datos
  recaudos: Recaudo[];
  recaudo_actual: Recaudo | null;
  
  // Paginación
  current_page: number;
  page_size: number;
  total_items: number;
  
  // Ordenamiento
  sort_by: string;      // Columna actual (ej: "direccion")
  sort_order: string;   // "asc" | "desc"
  
  // Filtros
  search_text: string;
  filter_estado: string;
  filter_dia_pago: string[];
  filter_ciclo_operativo: string[];
  filter_propiedad: string[];  // ← NUEVO: Filtro de propiedad
  filter_fecha_desde: string;
  filter_fecha_hasta: string;
  
  // Opciones de filtro
  estado_options: FilterOption[];
  dias_pago_options: FilterOption[];
  ciclo_operativo_options: FilterOption[];
  propiedad_options: FilterOption[];  // ← NUEVO: Opciones de propiedad
}

interface Recaudo {
  id_recaudo: string;
  fecha_pago: string;
  fecha_pago_contrato: string;
  ciclo_operativo: string;
  direccion: string;        // ← Campo de propiedad
  matricula: string;        // ← Matrícula de propiedad
  arrendatario: string;
  habitante: string;
  valor_total: number;
  valor_total_view: string;
  metodo_pago: string;
  estado: string;
}

interface FilterOption {
  value: string;
  label: string;
}
```

### Eventos

```typescript
// Eventos de la tabla
type RecaudosEvent =
  | { type: "TOGGLE_SORT"; column: string }
  | { type: "SET_PAGE"; page: number }
  | { type: "SET_PAGE_SIZE"; size: number }
  | { type: "FILTER_ESTADO"; value: string }
  | { type: "FILTER_PROPIEDAD"; value: string }  // ← NUEVO
  | { type: "TOGGLE_FILTER_PROPIEDAD"; value: string }  // ← NUEVO
  | { type: "SEARCH"; text: string }
  | { type: "CLEAR_FILTERS" };
```

### API de Datos

```typescript
// Request para listar recaudos
interface ListarRecaudosRequest {
  estado?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  dia_pago?: string[];
  ciclo_operativo?: string[];
  propiedad_ids?: string[];  // ← NUEVO: Filtro por propiedad
  busqueda?: string;
  sort_by?: string;  // "direccion" para ordenar por propiedad
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

// Response
interface ListarRecaudosResponse {
  recaudos: Recaudo[];
  total: number;
  page: number;
  page_size: number;
}
```

### Contrato Visual

```
┌─────┬──────────┬─────────────┬──────────────┬─────────────┬─────────────┬───────┬────────┬──────┬─────────┐
│ ID  │ Fecha    │ Pago        │ Ciclo        │ Propiedad   │ Arrendatario│Valor  │ Metodo │Estado│ Acciones│
├─────┼──────────┼─────────────┼──────────────┼─────────────┼─────────────┼───────┼────────┼──────┼─────────┤
│ 001 │ 01/07/24 │ 01/07/24    │ Jul 2024     │ Carrera 7#  │ Juan Pérez  │$1.5M  │ Transfer│ Pagado│ [PDF] [Edit]│
│     │          │             │              │ 45-12       │             │       │        │      │         │
└─────┴──────────┴─────────────┴──────────────┴─────────────┴─────────────┴───────┴────────┴──────┴─────────┘
```

### Responsive Behavior

| Viewport | Columna PROPIEDAD |
|----------|-------------------|
| Desktop (>1024px) | Visible con dirección completa |
| Tablet (768-1024px) | Visible con dirección truncada |
| Mobile (<768px) | Oculta o colapsada |

### Accesibilidad

- Header de columna debe tener `aria-label="Ordenar por Propiedad"`
- Icono de sort debe tener `aria-hidden="true"`
- Tooltip debe mostrar dirección completa en desktop
