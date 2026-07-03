# Quickstart: Fix Sincronización Incidentes - Liquidaciones

**Date**: 2026-07-02
**Feature**: 004-fix-sincronizacion-incidentes-liquidaciones

## Overview

Guía de validación para verificar que los 5 bugs identificados en la integración Incidentes-Liquidaciones han sido corregidos correctamente.

## Prerrequisitos

- Base de datos PostgreSQL con datos de prueba
- Usuario con rol Administrador
- Incidente con plan de pago activo y cuota pendiente
- Liquidación en estado "En Proceso" o "Aprobada"

## Escenarios de Validación

### Escenario 1: Visualización Correcta del Valor de Incidentes

**Objetivo**: Verificar que el campo "Incidentes" muestra la suma correcta

**Pasos**:
1. Abrir detalle de liquidación con incidente asociado
2. Verificar valor en campo "Incidentes (Plan Pago)"
3. Verificar que `NETO_A_PAGAR = TOTAL_INGRESOS - TOTAL_EGRESOS - VALOR_INCIDENTES`

**Resultado Esperado**:
- Campo "Incidentes" muestra el valor correcto de la cuota
- `NETO_A_PAGAR` es consistente con la fórmula

**Comando de Verificación**:
```sql
-- Verificar valor en BD
SELECT 
    l.VALOR_INCIDENTES,
    l.NETO_A_PAGAR,
    l.TOTAL_INGRESOS,
    l.TOTAL_EGRESOS,
    (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - l.VALOR_INCIDENTES) as NETO_CALCULADO
FROM LIQUIDACIONES l
WHERE l.ID_LIQUIDACION = :id_liquidacion;

-- Verificar que NETO_A_PAGAR = NETO_CALCULADO
```

---

### Escenario 2: Registro de IDs de Incidentes en Observaciones

**Objetivo**: Verificar que las observaciones se actualizan con append

**Pasos**:
1. Asociar incidente #101 a liquidación sin observaciones
2. Verificar observaciones: "Inc #101"
3. Asociar incidente #205 a misma liquidación
4. Verificar observaciones: "Inc #101\nInc #205"

**Resultado Esperado**:
- Observaciones contienen ambos IDs
- Formato correcto: un ID por línea
- No se sobreescriben observaciones anteriores

**Comando de Verificación**:
```sql
-- Verificar observaciones
SELECT OBSERVACIONES
FROM LIQUIDACIONES
WHERE ID_LIQUIDACION = :id_liquidacion;

-- Esperado: "Inc #101\nInc #205"
```

---

### Escenario 3: Persistencia del Estado de Pago

**Objetivo**: Verificar que ESTADO_PAGO se persiste en BD

**Pasos**:
1. Asociar incidente a liquidación pagada
2. Verificar estado_pago del incidente en BD
3. Desasociar incidente
4. Verificar estado_pago se actualiza

**Resultado Esperado**:
- Después de asociar a liquidación pagada: `ESTADO_PAGO = 'Pagado'`
- Después de desasociar: `ESTADO_PAGO = 'Pendiente'`

**Comando de Verificación**:
```sql
-- Verificar estado de pago
SELECT ESTADO_PAGO
FROM INCIDENTES
WHERE ID_INCIDENTE = :id_incidente;

-- Esperado: 'Pagado' o 'Pendiente' según operación
```

---

### Escenario 4: Desasociación Segura

**Objetivo**: Verificar que al desasociar solo se remueve el ID específico

**Pasos**:
1. Liquidación con observaciones "Inc #101\nInc #205"
2. Desasociar incidente #101
3. Verificar observaciones: "Inc #205"
4. Verificar que observaciones del usuario se preservan

**Resultado Esperado**:
- Solo se remueve "Inc #101"
- Se mantiene "Inc #205"
- Se preservan notas del usuario

**Comando de Verificación**:
```sql
-- Verificar observaciones después de desasociar
SELECT OBSERVACIONES
FROM LIQUIDACIONES
WHERE ID_LIQUIDACION = :id_liquidacion;

-- Esperado: "Inc #205" (sin "#101")
```

---

### Escenario 5: Formulario de Edición Correcto

**Objetivo**: Verificar que el campo "Incidentes" se mapea correctamente

**Pasos**:
1. Abrir formulario de edición de liquidación
2. Verificar que campo "Incidentes" muestra valor correcto
3. Editar campo "Incidentes"
4. Verificar que campo "Gastos Reparaciones" no cambió

**Resultado Esperado**:
- Campo "Incidentes" muestra `valor_incidentes`
- Editar "Incidentes" no afecta `gastos_reparaciones`
- Guardar cambios actualiza correctamente

**Comando de Verificación**:
```sql
-- Verificar valores después de editar
SELECT 
    VALOR_INCIDENTES,
    GASTOS_REPARACIONES
FROM LIQUIDACIONES
WHERE ID_LIQUIDACION = :id_liquidacion;

-- Verificar que GASTOS_REPARACIONES no cambió
```

---

### Escenario 6: Script de Diagnóstico

**Objetivo**: Identificar liquidaciones con valores inconsistentes

**Comando**:
```sql
-- Identificar liquidaciones con NETO_A_PAGAR incorrecto
SELECT 
    l.ID_LIQUIDACION,
    l.VALOR_INCIDENTES,
    l.NETO_A_PAGAR,
    (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - l.VALOR_INCIDENTES) as NETO_CORRECTO,
    ABS(l.NETO_A_PAGAR - (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - l.VALOR_INCIDENTES)) as DIFERENCIA
FROM LIQUIDACIONES l
WHERE ABS(l.NETO_A_PAGAR - (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - l.VALOR_INCIDENTES)) > 0.01
ORDER BY DIFERENCIA DESC;
```

**Resultado Esperado**:
- Lista de liquidaciones con valores inconsistentes
- Diferencia calculada para cada una

---

## Ejecución de Tests

### Tests Unitarios

```bash
# Ejecutar tests unitarios
pytest tests/unit/test_servicio_incidente_liquidacion.py -v
pytest tests/unit/test_servicio_estado_pago.py -v

# Con cobertura
pytest tests/unit/ --cov=src/aplicacion/servicios --cov-report=html
```

### Tests de Integración

```bash
# Ejecutar tests de integración
pytest tests/integration/test_repositorio_incidentes.py -v
pytest tests/integration/test_repositorio_liquidacion.py -v

# Con cobertura
pytest tests/integration/ --cov=src/infraestructura/persistencia --cov-report=html
```

### Verificación Manual

```bash
# Iniciar servidor en modo debug
reflex run --env dev

# Abrir navegador y seguir escenarios de validación
```

## Criterios de Aceptación

- [ ] Todos los tests unitarios pasan
- [ ] Todos los tests de integración pasan
- [ ] Cobertura >90% para lógica nueva
- [ ] Escenario 1: Valor de incidentes se muestra correctamente
- [ ] Escenario 2: Observaciones se actualizan con append
- [ ] Escenario 3: ESTADO_PAGO se persiste
- [ ] Escenario 4: Desasociación segura funciona
- [ ] Escenario 5: Formulario de edición correcto
- [ ] Escenario 6: Script de diagnóstico identifica inconsistencias
- [ ] Consola del navegador sin errores
- [ ] Sin regresiones en funcionalidad existente

## Troubleshooting

### Problema: NETO_A_PAGAR no se actualiza
**Causa**: El trigger actualiza VALOR_INCIDENTES pero la aplicación no sincroniza
**Solución**: Verificar que el servicio consulta VALOR_INCIDENTES fresco después del trigger

### Problema: Observaciones se sobreescriben
**Causa**: Lógica de reemplazo en lugar de append
**Solución**: Verificar uso de `agregar_id_incidente()` en lugar de asignación directa

### Problema: ESTADO_PAGO no se persiste
**Causa**: Campo no incluido en UPDATE SQL
**Solución**: Verificar que repositorio incluye ESTADO_PAGO en query

### Problema: Campo Incidentes mapeado incorrectamente
**Causa**: Nombre de campo incorrecto en form_data
**Solución**: Verificar mapeo a `valor_incidentes` en lugar de `gastos_reparaciones`
