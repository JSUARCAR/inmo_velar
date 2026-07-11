# Quickstart Validation Guide: Corrección valor_incidentes en Reportes

**Date**: 2026-07-11
**Feature**: 044-fix-valor-incidentes-reportes

## Prerequisites

1. Base de datos PostgreSQL con al menos una liquidación que tenga `valor_incidentes > 0`
2. Servidor de desarrollo funcionando (`reflex run --env dev`)
3. Acceso al módulo de Reportes en la UI

## Validation Scenarios

### Scenario 1: Reporte de Liquidaciones incluye valor_incidentes

**Steps:**
1. Navegar a la página de Liquidaciones
2. Seleccionar una liquidación con incidentes asociados
3. Generar el Reporte de Liquidaciones (PDF o Excel)
4. Verificar que la columna `Valor_Incidentes` aparece en el reporte

**Expected Outcome:**
- Columna `Valor_Incidentes` visible con valor formateado (ej: `$1,500.00`)
- Valor coincide con el mostrado en el modal de detalle de la liquidación

**Test Command:**
```bash
# Verificar que el campo existe en la consulta SQL
grep -n "VALOR_INCIDENTES" src/infraestructura/persistencia/repositorio_reportes.py
```

### Scenario 2: Reporte Financiero Consolidado incluye valor_incidentes

**Steps:**
1. Navegar a Reportes → Reporte Financiero Consolidado
2. Aplicar filtros para un período específico
3. Generar el reporte (CSV/Excel)
4. Verificar que la columna `VALOR_INCIDENTES` aparece

**Expected Outcome:**
- Columna `VALOR_INCIDENTES` presente en el CSV
- Valores numéricos correctos (sin formato de moneda en CSV raw)
- `NETO_A_PAGAR` incluye el descuento de `VALOR_INCIDENTES`

**Test Command:**
```python
# Verificar headers actualizados
python -c "from src.aplicacion.servicios.servicio_reportes import HEADERS_REPORTE_CONSOLIDADO; print('VALOR_INCIDENTES' in HEADERS_REPORTE_CONSOLIDADO)"
# Expected: True
```

### Scenario 3: Liquidaciones sin incidentes muestran $0.00

**Steps:**
1. Seleccionar una liquidación SIN incidentes asociados
2. Generar reporte
3. Verificar que `Valor_Incidentes` muestra `$0.00` o `0`

**Expected Outcome:**
- Campo presente pero con valor 0
- No muestra NULL ni campo vacío

### Scenario 4: Consistencia de formato monetario

**Steps:**
1. Generar reporte con liquidaciones de diferentes valores
2. Comparar formato de `Valor_Incidentes` con `Comision_Monto` u otro campo monetario

**Expected Outcome:**
- Ambos campos usan el mismo formato (separadores de miles, 2 decimales)
- Prefijo de moneda consistente

### Scenario 5: Performance no degradada

**Steps:**
1. Medir tiempo de generación antes del cambio (baseline)
2. Aplicar cambios
3. Medir tiempo después del cambio

**Expected Outcome:**
- Incremento < 5% en tiempo de generación
- Tiempo total < 30 segundos

**Test Command:**
```bash
# Benchmark rápido
time python -c "
from src.infraestructura.persistencia.repositorio_reportes import RepositorioReportes
repo = RepositorioReportes()
import time
start = time.time()
repo.obtener_reporte_consolidado(page=1, limit=100)
print(f'Tiempo: {time.time() - start:.2f}s')
"
```

### Scenario 6: Valores altos sin truncamiento

**Steps:**
1. Crear liquidación con `valor_incidentes` > $1,000,000
2. Generar reporte
3. Verificar que el valor se muestra completo

**Expected Outcome:**
- Valor completo sin truncamiento
- Separadores de miles correctos (ej: `$1,250,000.00`)

## Regression Tests

### Test de regresión existentes
```bash
# Ejecutar tests de unit del dominio
pytest tests/unit/dominio/test_liquidacion.py -v

# Ejecutar tests de integración de reportes
pytest tests/integration/test_reportes.py -v
```

### Validación manual post-cambio
1. Generar PDF de liquidación individual → Verificar campo visible
2. Generar CSV de reporte consolidado → Verificar columna presente
3. Comparar valores con consulta SQL directa a PostgreSQL
4. Verificar que NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES

## Rollback Plan

Si el cambio introduce regresiones:
1. Revertir los cambios en `repositorio_reportes.py` (restaurar SELECTs originales)
2. Revertir cambio en `servicio_reportes.py` (restaurar HEADERS originales)
3. Ejecutar pruebas de regresión
4. Investigar causa raíz antes de re-intentar

## Success Criteria Checklist

- [ ] `VALOR_INCIDENTES` visible en Reporte de Liquidaciones (PDF)
- [ ] `VALOR_INCIDENTES` visible en Reporte Financiero Consolidado (CSV)
- [ ] Valores NULL se muestran como 0
- [ ] Formato monetario consistente con otros campos
- [ ] `NETO_A_PAGAR` calculado correctamente (descuenta valor_incidentes)
- [ ] Performance dentro de umbrales aceptables (< 30s, < 5% incremento)
- [ ] No hay regresiones en reportes existentes
