# Data Model: Columnas Financieras Liquidaciones

**Date**: 2026-07-11
**Feature**: 048-columnas-financieras-liquidaciones

## Entity: Liquidación

**Tabla PostgreSQL**: `LIQUIDACIONES`

### Campos Financieros (existentes en BD)

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| otros_ingresos | INTEGER | 0 | Ingresos adicionales al canon |
| gastos_administracion | INTEGER | 0 | Gastos de administración del inmueble |
| gastos_servicios | INTEGER | 0 | Gastos de servicios públicos |
| gastos_reparaciones | INTEGER | 0 | Gastos de reparaciones y mantenimiento |
| valor_incidentes | INTEGER | 0 | Valor total de incidentes asociados |
| pago_predial | INTEGER | 0 | Pago de impuesto predial |
| otros_egresos | INTEGER | 0 | Egresos adicionales |
| iva_comision | INTEGER | 0 | IVA sobre comisión de administración |

### Campos Calculados (en UI)

| Campo | Fórmula | Formato |
|-------|---------|---------|
| total_ingresos | canon_bruto + otros_ingresos | $XX.XXX,XX |
| total_egresos | gastos_admin + gastos_serv + gastos_rep + valor_inc + pago_pred + otros_egr + iva_com | $XX.XXX,XX |
| neto_a_pagar | total_ingresos - total_egresos - comision - impuesto_4x1000 | $XX.XXX,XX |

## DTO: LiquidacionDict

**File**: `src/presentacion_reflex/state/liquidaciones_state.py`

### Estructura Actual

```python
class LiquidacionDict(BaseModel):
    id: int
    periodo: str
    propiedad_nombre: str
    ciclo_operativo: str
    canon: float
    canon_view: str
    neto: float
    neto_view: str
    estado_recaudo: str
    estado: str
```

### Estructura Requerida (aggiorna)

```python
class LiquidacionDict(BaseModel):
    # Campos existentes
    id: int
    periodo: str
    propiedad_nombre: str
    ciclo_operativo: str
    canon: float
    canon_view: str
    neto: float
    neto_view: str
    estado_recaudo: str
    estado: str
    
    # Nuevos campos financieros
    otros_ingresos: float = 0.0
    otros_ingresos_view: str = "$0,00"
    gastos_administracion: float = 0.0
    gastos_administracion_view: str = "$0,00"
    gastos_servicios: float = 0.0
    gastos_servicios_view: str = "$0,00"
    gastos_reparaciones: float = 0.0
    gastos_reparaciones_view: str = "$0,00"
    valor_incidentes: float = 0.0
    valor_incidentes_view: str = "$0,00"
    pago_predial: float = 0.0
    pago_predial_view: str = "$0,00"
    otros_egresos: float = 0.0
    otros_egresos_view: str = "$0,00"
    iva_comision: float = 0.0
    iva_comision_view: str = "$0,00"
```

## Validación de Datos

### Reglas de Negocio

1. **Valores nulos/vacíos**: Mostrar $0,00 (FR-004)
2. **Formato monetario**: Separadores de miles con puntos, decimales con coma (formato colombiano)
3. **Alineación**: Derecha para valores monetarios
4. **Sincronización**: Datos de PostgreSQL → Backend → UI sin cálculos duplicados

### Mapeo de Campos

| UI Column | DTO Field | BD Column | Format |
|-----------|-----------|-----------|--------|
| Otros Ingresos | otros_ingresos | otros_ingresos | format_currency() |
| Gastos Administración | gastos_administracion | gastos_administracion | format_currency() |
| Gastos Servicios | gastos_servicios | gastos_servicios | format_currency() |
| Gastos Reparaciones | gastos_reparaciones | gastos_reparaciones | format_currency() |
| Valor Incidentes | valor_incidentes | valor_incidentes | format_currency() |
| Pago Predial | pago_predial | pago_predial | format_currency() |
| Otros Egresos | otros_egresos | otros_egresos | format_currency() |
| IVA Comisión | iva_comision | iva_comision | format_currency() |

## Relaciones

```
LIQUIDACIONES (1) ←→ (N) INCIDENTES
    ↓
    └── valor_incidentes = SUM(incidentes.valor)
```

**Nota**: El campo `valor_incidentes` es una agregación de la tabla INCIDENTES. Se calcula en el repositorio al momento de la consulta.
