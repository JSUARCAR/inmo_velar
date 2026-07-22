# Quickstart Validation: Corrección de Propagación de Canon en Renovaciones

**Date**: 2026-07-22
**Feature**: 063-fix-canon-propagation

## Prerrequisitos

1. PostgreSQL ejecutándose (Railway o local)
2. Variables de entorno configuradas:
   - `DATABASE_URL`: URL de conexión a PostgreSQL
3. Python 3.11+ con dependencias instaladas
4. Script de auditoría existente: `scripts/diagnostico/audit_renovaciones_2026.py`

## Escenarios de Validación

### Escenario 1: Propagación Exitosa

**Objetivo**: Verificar que la renovación propaga correctamente el canon a Liquidaciones y Recaudos.

**Pasos**:
1. Seleccionar un contrato existente con liquidaciones y recaudos futuros
2. Ejecutar renovación con nuevo canon
3. Verificar que liquidaciones futuras tienen el nuevo canon
4. Verificar que recaudos futuros tienen el nuevo valor
5. Verificar que registros históricos no cambiaron

**Comandos**:
```bash
# 1. Verificar estado actual
python -c "
from src.infraestructura.repositorios.repositorio_contrato import RepositorioContrato
repo = RepositorioContrato()
contrato = repo.obtener_por_id(80)
print(f'Canon actual: {contrato.canon_arrendamiento}')
"

# 2. Ejecutar renovación
python -c "
from src.aplicacion.servicios.servicio_contrato_arrendamiento import ServicioContratoArrendamiento
servicio = ServicioContratoArrendamiento()
resultado = servicio.renovar_contrato(
    contrato_id=80,
    canon_nuevo=893350,
    fecha_renovacion='2026-07-17'
)
print(f'Resultado: {resultado}')
"

# 3. Verificar propagación
python scripts/diagnostico/audit_renovaciones_2026.py
```

**Resultado esperado**:
- `registros_liquidaciones_actualizados` > 0
- `registros_recaudos_actualizados` > 0
- Auditoría muestra 0 inconsistencias

### Escenario 2: Preservación de Historial

**Objetivo**: Verificar que registros históricos no son modificados.

**Pasos**:
1. Obtener valor de liquidaciones históricas (fecha <= fecha_renovacion)
2. Ejecutar renovación
3. Verificar que valores históricos no cambiaron

**Comandos**:
```bash
# 1. Obtener valores históricos antes de renovación
python -c "
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('''
    SELECT id_liquidacion, canon_bruto, fecha_generacion
    FROM LIQUIDACIONES
    WHERE id_contrato_m = (SELECT id_contrato_m FROM CONTRATOS_MANDATOS WHERE id_contrato_a = 80 LIMIT 1)
    AND fecha_generacion::date <= '2026-07-01'
''')
for row in cur.fetchall():
    print(f'ID: {row[0]}, Canon: {row[1]}, Fecha: {row[2]}')
"

# 2. Ejecutar renovación y verificar
```

**Resultado esperado**:
- Valores históricos permanecen unchanged

### Escenario 3: Rollback en Caso de Error

**Objetivo**: Verificar que si la propagación falla, se revierten todos los cambios.

**Pasos**:
1. Simular un error durante la propagación (ej: constraint violation)
2. Verificar que no se aplicaron cambios parciales

**Resultado esperado**:
- Transacción completa revertida
- Mensaje de error informativo
- Datos en estado consistente (pre-renovación)

### Escenario 4: Verificación de Integridad

**Objetivo**: Verificar que el mecanismo de verificación detecta inconsistencias.

**Pasos**:
1. Crear una inconsistencia manual (actualizar solo contrato, no liquidaciones)
2. Ejecutar verificación de integridad
3. Verificar que detecta la inconsistencia

**Comandos**:
```bash
# 1. Ejecutar script de auditoría
python scripts/diagnostico/audit_renovaciones_2026.py

# 2. Revisar resultados
cat scripts/diagnostico/audit_renovaciones_2026_*.json | python -m json.tool
```

**Resultado esperado**:
- Inconsistencia detectada en `inconsistencias_liquidaciones` o `inconsistencias_recaudos`
- Detalle incluye contrato_id, tabla, registro_id, valores

## Métricas de Validación

| Métrica | Objetivo | Cómo medir |
|---------|----------|------------|
| SC-001: Liquidaciones futuras con canon correcto | 100% | Auditoría: inconsistencias_liquidaciones = 0 |
| SC-002: Recaudos futuros con canon correcto | 100% | Auditoría: inconsistencias_recaudos = 0 |
| SC-003: Registros históricos preservados | 100% | Comparar valores antes/después |
| SC-004: Tiempo de verificación < 30s | < 30s | Cronómetro con 100 registros |
| SC-005: Corrección de 500 registros | Sin errores | Ejecutar corrección masiva |

## Troubleshooting

### Error: "column r.updated_at does not exist"
**Causa**: La tabla RENOVACIONES_CONTRATOS no tiene columna `updated_at`
**Solución**: Usar solo `created_at` en queries de auditoría

### Error: "operator does not exist: text >= date"
**Causa**: Comparación de tipo text con date
**Solución**: Usar casting `::date` en comparaciones de fecha

### Error: "current transaction is aborted"
**Causa**: Query anterior falló y dejó la transacción en estado abortado
**Solución**: Ejecutar `ROLLBACK` antes de la siguiente query

## Referencias

- Script de auditoría: `scripts/diagnostico/audit_renovaciones_2026.py`
- Especificación: `specs/063-fix-canon-propagation/spec.md`
- Modelo de datos: `specs/063-fix-canon-propagation/data-model.md`
