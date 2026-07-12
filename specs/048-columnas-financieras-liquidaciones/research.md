# Research: Columnas Financieras Liquidaciones

**Date**: 2026-07-11
**Feature**: 048-columnas-financieras-liquidaciones

## Research Summary

Investigación completa del módulo Liquidaciones para identificar la arquitectura actual y los puntos de implementación necesarios.

## Findings

### 1. Entidad de Dominio - CAMPOS YA EXISTEN

**File**: `src/dominio/entidades/liquidacion.py`

La entidad `Liquidacion` ya contiene los 8 campos financieros solicitados:

```python
otros_ingresos: int = 0
gastos_administracion: int = 0
gastos_servicios: int = 0
gastos_reparaciones: int = 0
valor_incidentes: int = 0
pago_predial: int = 0
otros_egresos: int = 0
iva_comision: int = 0
```

**Decision**: No se requieren migraciones de base de datos. Los campos ya existen en la tabla LIQUIDACIONES.

### 2. Modelo DTO - NECESITA ACTUALIZACIÓN

**File**: `src/presentacion_reflex/state/liquidaciones_state.py`

El modelo `LiquidacionDict` actual solo tiene:
- `canon: float`
- `canon_view: str`
- `neto: float`
- `neto_view: str`

**Decision**: Agregar los 8 campos financieros con sus versiones formateadas (_view).

### 3. Consultas del Repositorio - NECESITA ACTUALIZACIÓN

**File**: `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

Las consultas actuales SELECT no incluyen los nuevos campos. Se requiere:
- Actualizar query individual para incluir los 8 campos
- Actualizar query agrupada para incluir sumatorias
- Mantener el rendimiento con índices apropiados

### 4. UI de Tabla - NECESITA ACTUALIZACIÓN

**File**: `src/presentacion_reflex/pages/liquidaciones.py`

Columnas actuales en tabla individual (línea 282):
- ID, Periodo, Propiedad, Ciclo Operativo, Canon, Neto a Pagar, Estado Recaudo, Estado, Acciones

**Decision**: Insertar 8 nuevas columnas después de Canon en el orden especificado.

### 5. Formateo Monetario - UTILIDAD EXISTENTE

**File**: `src/presentacion_reflex/utils/formatters.py`

Función `format_currency(amount)` ya implementada:
- Formato: `$10.176.000` (separadores de miles con puntos)
- Locale colombiano

**Decision**: Reutilizar `format_currency()` para las nuevas columnas.

### 6. Filtros Avanzados - COMPONENTE REUTILIZABLE

**File**: `src/presentacion_reflex/components/shared/advanced_filter_bar.py`

Componente reutilizable con filtros: Periodo, Estado, Ciclo, Asesor.

**Decision**: Agregar filtros por rango (mín/máx) para las 8 columnas financieras.

### 7. Exportación - MODAL EXISTENTE

**File**: `src/presentacion_reflex/components/liquidaciones/export_modal.py`

Exportación ZIP por período. Incluye datos de liquidaciones.

**Decision**: Agregar los 8 campos al payload de exportación.

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Crear vistas SQL separadas | Campos ya existen en tabla principal |
| Usar SQLAlchemy ORM | Proyecto usa queries raw con psycopg2 |
| Agregar columnas calculadas | Requisito: usar fuente oficial sin duplicidad |

## Implementation Order

1. **Domain Layer**: Entity already complete - no changes needed
2. **DTO Layer**: Update `LiquidacionDict` with new fields
3. **Repository Layer**: Update SQL queries to SELECT new fields
4. **State Layer**: Add formatting logic for new fields
5. **UI Layer**: Add columns to table component
6. **Filters**: Add range filters for monetary columns
7. **Export**: Include new fields in export payload
