# Quickstart: Validación de Sincronización Contratos, Liquidaciones y Recaudos

**Date**: 2026-07-22
**Feature**: 061-reverse-engineer-contracts-sync

## Prerequisites

1. **Python 3.11+** instalado
2. **PostgreSQL** accesible (staging environment)
3. **Dependencias instaladas**: `pip install -r requirements.txt`
4. **Variables de entorno configuradas**: `DATABASE_URL` apuntando a staging

## Quick Validation (30 seconds)

### Ejecutar Auditoría Completa

```bash
# Navegar al directorio del proyecto
cd D:\INMOBILIARIA VELAR SAS\inmobiliaria velar\PYTHON-REFLEX

# Ejecutar script de auditoría
python tests/verification/audit_sincronizacion.py
```

**Expected Output**:
```
========================================
INFORME DE AUDITORÍA - SINCRONIZACIÓN
Fecha: 2026-07-22 13:30:00
========================================

VR-001: Cascada de Renovación - Canon
Estado: PASS

VR-002: Cascada de Renovación - Historial
Estado: PASS

...

========================================
RESUMEN
========================================
Total de reglas: 10
Pasaron: 10
Fallaron: 0
Tasa de éxito: 100%
========================================
```

### Ejecutar Tests de Integración

```bash
# Ejecutar tests de integración de sincronización
pytest tests/integration/test_sincronizacion_contratos.py -v
```

**Expected Output**:
```
tests/integration/test_sincronizacion_contratos.py::test_cascada_renovacion_canon PASSED
tests/integration/test_sincronizacion_contratos.py::test_preservacion_historicos_liquidaciones PASSED
tests/integration/test_sincronizacion_contratos.py::test_generacion_canon_actualizado PASSED
...
============================== 10 passed in 15.23s ==============================
```

### Ejecutar Tests Unitarios de Validación

```bash
# Ejecutar tests unitarios de cascada
pytest tests/unit/test_validacion_cascada.py -v
```

**Expected Output**:
```
tests/unit/test_validacion_cascada.py::test_validar_canon_mandato PASSED
tests/unit/test_validacion_cascada.py::test_validar_canon_propiedad PASSED
...
============================== 8 passed in 5.12s ===============================
```

## Detailed Validation Scenarios

### Scenario 1: Validación de Cascada de Renovación

**Objective**: Verificar que la renovación propaga correctamente el canon a mandato y propiedad.

**Steps**:
1. Crear contrato de arrendamiento activo con canon = 1.000.000
2. Crear mandato asociado con canon_mandato = 1.000.000
3. Crear propiedad con canon_arrendamiento_estimado = 1.000.000
4. Ejecutar renovación con canon_nuevo = 1.100.000
5. Verificar que mandato y propiedad se actualizaron a 1.100.000

**Command**:
```bash
pytest tests/integration/test_sincronizacion_contratos.py::test_cascada_renovacion_canon -v
```

**Expected**: PASS

---

### Scenario 2: Validación de Preservación de Históricos

**Objective**: Verificar que liquidaciones y recaudos antiguos no se modifican.

**Steps**:
1. Crear liquidación en período 2026-06 con canon_bruto = 1.000.000
2. Crear recaudo en período 2026-06 con valor_total = 1.000.000
3. Ejecutar renovación en julio 2026 con canon_nuevo = 1.100.000
4. Verificar que liquidación y recaudo de 2026-06 mantienen valores originales

**Command**:
```bash
pytest tests/integration/test_sincronizacion_contratos.py::test_preservacion_historicos_liquidaciones -v
```

**Expected**: PASS

---

### Scenario 3: Validación de Generación con Canon Actualizado

**Objective**: Verificar que liquidaciones y recaudos futuros usan el nuevo canon.

**Steps**:
1. Crear contrato renovado con canon_nuevo = 1.100.000
2. Generar liquidación para período 2026-08 (después de renovación)
3. Generar recaudo para período 2026-08 (después de renovación)
4. Verificar que ambos usan canon = 1.100.000

**Command**:
```bash
pytest tests/integration/test_sincronizacion_contratos.py::test_generacion_canon_actualizado -v
```

**Expected**: PASS

---

### Scenario 4: Validación de Consistencia entre Módulos

**Objective**: Verificar que no hay discrepancias entre contratos, liquidaciones y recaudos.

**Steps**:
1. Consultar valores de canon en ContratoArrendamiento, ContratoMandato y Propiedad
2. Verificar que todos muestran el mismo valor

**Command**:
```bash
pytest tests/integration/test_sincronizacion_contratos.py::test_consistencia_modulos -v
```

**Expected**: PASS

---

### Scenario 5: Validación de Ausencia de Actualizaciones Retroactivas

**Objective**: Verificar que no existen procesos que modifiquen registros históricos.

**Steps**:
1. Analizar código fuente en busca de procesos de actualización
2. Verificar que no hay procesos que modifiquen canon_bruto o valor_total después de creación

**Command**:
```bash
python tests/verification/audit_sincronizacion.py --check-retroactive
```

**Expected**: PASS

---

### Scenario 6: Validación de Respeto de Fecha de Vigencia

**Objective**: Verificar que la fecha de vigencia de la renovación es respetada.

**Steps**:
1. Ejecutar renovación el 2026-07-15
2. Generar liquidación para período 2026-06 (antes de renovación)
3. Generar liquidación para período 2026-08 (después de renovación)
4. Verificar que 2026-06 usa canon anterior y 2026-08 usa canon nuevo

**Command**:
```bash
pytest tests/integration/test_sincronizacion_contratos.py::test_reseto_fecha_vigencia -v
```

**Expected**: PASS

## Troubleshooting

### Error: "No se pudo conectar a la base de datos"
**Solution**: Verificar que `DATABASE_URL` está configurado correctamente y que PostgreSQL está accesible.

### Error: "Tabla no encontrada"
**Solution**: Ejecutar migraciones: `alembic upgrade head`

### Error: "Test falló con valores inesperados"
**Solution**: Revisar el informe de auditoría para ver valores esperados vs encontrados.

## CI/CD Integration

Para integrar en CI/CD, agregar al pipeline:

```yaml
# Ejemplo para GitHub Actions
- name: Validar sincronización
  run: |
    pip install -r requirements.txt
    python tests/verification/audit_sincronizacion.py
    pytest tests/integration/test_sincronizacion_contratos.py -v
```

## Next Steps

1. Ejecutar auditoría completa
2. Revisar informe de resultados
3. Si hay fallas, investigar causa raíz
4. Crear fixes para issues encontrados
5. Re-ejecutar para verificar corrección
