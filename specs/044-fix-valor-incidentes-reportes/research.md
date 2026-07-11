# Research: Corrección valor_incidentes en Reportes

**Date**: 2026-07-11
**Feature**: 044-fix-valor-incidentes-reportes

## Decision: Agregar VALOR_INCIDENTES a consultas SQL de reportes

### Rationale

El campo `valor_incidentes` existe en la tabla `LIQUIDACIONES` de PostgreSQL y está correctamente almacenado. Sin embargo, las consultas SQL utilizadas para generar los reportes de Liquidaciones y Financiero Consolidado no incluyen este campo en sus statementes SELECT.

**Causa raíz identificada:**
- `obtener_reporte_liquidaciones()` en `repositorio_reportes.py:259` - SELECT omite `VALOR_INCIDENTES`
- `obtener_reporte_consolidado()` en `repositorio_reportes.py:601` - SELECT omite `VALOR_INCIDENTES`
- `HEADERS_REPORTE_CONSOLIDADO` en `servicio_reportes.py:6` - Lista de 46 headers no incluye el campo
- Cálculo de `NETO_A_PAGAR` en reporte consolidado (línea 671) no descuenta `VALOR_INCIDENTES`

### Alternatives Considered

1. **Alternativa A: Modificar solo las consultas SQL** - Más simple pero no actualiza los headers del CSV
2. **Alternativa B: Modificar SQL + headers + cálculo NETO_A_PAGAR** - Solución completa que garantiza consistencia
3. **Alternativa C: Crear vistas materializadas** - Sobrediseñado para este caso de uso

**Decisión: Alternativa B** - Solución completa que toca todos los puntos necesarios.

## Finding: Estructura actual de datos

### Entidad Liquidacion (dominio)
```python
# src/dominio/entidades/liquidacion.py:45
valor_incidentes: int = 0  # Descuentos por incidentes (nuevo)
```

### Cálculo en dominio
```python
# src/dominio/entidades/liquidacion.py:121-123
self.neto_a_pagar = self.total_ingresos - self.total_egresos - self.valor_incidentes
```

### Población de datos
- Durante creación de liquidación: `servicio_financiero.py:223-248` - Suma cuotas pendientes de incidentes
- Después de asociar/desasociar incidente: `servicio_incidente_liquidacion.py:323-333` - Recalcula desde `INCIDENTE_LIQUIDACION`

### Archivos a modificar
1. `src/infraestructura/persistencia/repositorio_reportes.py` - Agregar `VALOR_INCIDENTES` a ambos SELECTs
2. `src/aplicacion/servicios/servicio_reportes.py` - Agregar header a `HEADERS_REPORTE_CONSOLIDADO`
3. Ajustar cálculo de `NETO_A_PAGAR` en reporte consolidado

## Finding: Formato monetario

El sistema ya utiliza formato monetario consistente con separadores de miles y 2 decimales. El campo se muestra como `$X,XXX.XX` en la UI (ver `liquidaciones_state.py:733`). Los reportes CSV exportan valores numéricos raw que Excel formatea automáticamente.

## Finding: Rendimiento

Agregar una columna adicional al SELECT no impacta significativamente el rendimiento ya que:
- La tabla `LIQUIDACIONES` ya está siendo consultada en ambos queries
- No se agregan nuevos JOINs
- No se modifican filtros ni condiciones WHERE

## Resolución de NEEDS CLARIFICATION

No hay NEEDS CLARIFICATION restantes. Todos los aspectos técnicos están claros:
- Fuente de datos: Campo pre-calculado en tabla LIQUIDACIONES
- Formatos: PDF y Excel (ambos)
- Error handling: Cancelar generación y mostrar error
- Performance: 30 segundos máximo
- Acceso: Todos los usuarios con permisos de reportes
