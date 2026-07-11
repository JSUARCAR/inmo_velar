# Implementation Plan: Corrección valor_incidentes en Reportes

**Branch**: `044-fix-valor-incidentes-reportes` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/044-fix-valor-incidentes-reportes/spec.md`

## Summary

Corregir la omisión del campo `valor_incidentes` en los reportes de Liquidaciones y Financiero Consolidado. El campo existe en PostgreSQL pero no se incluye en las consultas SQL de los reportes ni en los headers del CSV.

**Causa raíz**: Las consultas `obtener_reporte_liquidaciones()` y `obtener_reporte_consolidado()` en `repositorio_reportes.py` no seleccionan la columna `VALOR_INCIDENTES`. Además, el cálculo de `NETO_A_PAGAR` en el reporte consolidado no descuenta este valor.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Reflex (frontend), psycopg2 (PostgreSQL), ReportLab (PDF)
**Storage**: PostgreSQL
**Testing**: pytest
**Target Platform**: Web application (Linux server + browser)
**Project Type**: Web application (Reflex + PostgreSQL)
**Performance Goals**: < 30 segundos generación de reportes
**Constraints**: Sin cambios en esquema de BD, sin regresiones
**Scale/Scope**: ~1000 liquidaciones por período

## Constitution Check

*GATE: Passed*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture | ✅ | Cambio en capa de Infraestructura (repositorios) y Aplicación (servicios) |
| PostgreSQL Native | ✅ | Usa placeholders `%s`, sin ORM |
| Idioma Español | ✅ | Comentarios y nombres en español |
| Zero Guessing | ✅ | Problema identificado con evidencia |
| Contract-First | ✅ | Headers definidos como constante |
| Atomic Changes | ✅ | Cambio pequeño (~50 líneas) |

## Project Structure

### Documentation (this feature)

```text
specs/044-fix-valor-incidentes-reportes/
├── plan.md              # Este archivo
├── research.md          # Fase 0: Análisis de causa raíz
├── data-model.md        # Fase 1: Modelo de datos y queries
├── quickstart.md        # Fase 1: Guía de validación
└── tasks.md             # Fase 2: Tareas de implementación
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       └── liquidacion.py          # Entidad (sin cambios)
├── aplicacion/
│   └── servicios/
│       └── servicio_reportes.py    # ✅ MODIFICAR: Agregar header
├── infraestructura/
│   └── persistencia/
│       └── repositorio_reportes.py # ✅ MODIFICAR: Agregar a SELECTs
└── presentacion_reflex/
    └── state/
        └── reportes_state.py       # Sin cambios (usa servicio_reportes)
```

## Implementation Tasks

### Tarea 1: Agregar VALOR_INCIDENTES a obtener_reporte_liquidaciones()

**Archivo**: `src/infraestructura/persistencia/repositorio_reportes.py`
**Línea**: 269 (después de `l.TOTAL_EGRESOS`)

**Cambio**:
```python
# Agregar después de la línea:
l.OTROS_EGRESOS, l.TOTAL_EGRESOS, l.NETO_A_PAGAR,

# Cambiar a:
l.OTROS_EGRESOS, l.TOTAL_EGRESOS, 
COALESCE(l.VALOR_INCIDENTES, 0) AS "Valor_Incidentes",
l.NETO_A_PAGAR,
```

### Tarea 2: Agregar VALOR_INCIDENTES a obtener_reporte_consolidado()

**Archivo**: `src/infraestructura/persistencia/repositorio_reportes.py`
**Línea**: 668 (después de `TOTAL_EGRESOS`)

**Cambio**:
```python
# Agregar después de TOTAL_EGRESOS:
COALESCE(l.VALOR_INCIDENTES, 0) AS "VALOR_INCIDENTES",
```

### Tarea 3: Corregir cálculo de NETO_A_PAGAR en reporte consolidado

**Archivo**: `src/infraestructura/persistencia/repositorio_reportes.py`
**Línea**: 671-678

**Cambio**:
```python
# Agregar COALESCE(l.VALOR_INCIDENTES, 0) al cálculo:
(COALESCE(l.TOTAL_INGRESOS, 0) - 
 (COALESCE(l.COMISION_MONTO, 0) + 
  COALESCE(l.IVA_COMISION, 0) + 
  COALESCE(l.GASTOS_ADMINISTRACION, 0) + 
  COALESCE(l.GASTOS_SERVICIOS, 0) + 
  COALESCE(l.GASTOS_REPARACIONES, 0) + 
  COALESCE(l.PAGO_PREDIAL, 0) + 
  COALESCE(l.OTROS_EGRESOS, 0) +
  COALESCE(l.VALOR_INCIDENTES, 0))) AS "NETO_A_PAGAR",
```

### Tarea 4: Actualizar HEADERS_REPORTE_CONSOLIDADO

**Archivo**: `src/aplicacion/servicios/servicio_reportes.py`
**Línea**: 55 (después de `TOTAL_EGRESOS`)

**Cambio**:
```python
# Agregar en la lista:
"TOTAL_EGRESOS",
"VALOR_INCIDENTES",  # Nuevo campo
"NETO_A_PAGAR",
```

### Tarea 5: Ejecutar pruebas de regresión

**Commands**:
```bash
# Syntax check
python -m py_compile src/infraestructura/persistencia/repositorio_reportes.py
python -m py_compile src/aplicacion/servicios/servicio_reportes.py

# Unit tests
pytest tests/unit/dominio/test_liquidacion.py -v

# Integration tests
pytest tests/integration/test_reportes.py -v

# Type checking
mypy src/infraestructura/persistencia/repositorio_reportes.py
```

### Tarea 6: Validación manual en navegador

**Steps**:
1. Ejecutar `reflex run --env dev`
2. Navegar a Liquidaciones → Generar PDF → Verificar campo
3. Navegar a Reportes → Consolidado → Generar CSV → Verificar columna
4. Comparar con consulta SQL directa

## Complexity Tracking

No aplica - cambio de complejidad baja sin violaciones constitucionales.

## Risk Assessment

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Regresión en cálculo NETO_A_PAGAR | Media | Alto | Pruebas de integración + validación manual |
| Performance degradada | Baja | Medio | Solo se agrega columna, no nuevos JOINs |
| Headers desalineados con SQL | Media | Medio | Verificar correspondencia 1:1 |

## Commit Strategy

```
fix(reportes): agregar valor_incidentes a reportes de liquidaciones y consolidado

- Agregar VALOR_INCIDENTES a obtener_reporte_liquidaciones()
- Agregar VALOR_INCIDENTES a obtener_reporte_consolidado()
- Corregir calculo de NETO_A_PAGAR en reporte consolidado
- Actualizar HEADERS_REPORTE_CONSOLIDADO

Closes #044
```
