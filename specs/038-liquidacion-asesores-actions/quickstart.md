# Quickstart Validation: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Feature**: 038-liquidacion-asesores-actions
**Date**: 2026-07-08

## Prerequisites

- Python 3.11+
- Base de datos con tablas LIQUIDACIONES_ASESORES, DESCUENTOS_ASESORES, PAGOS_ASESORES
- Al menos una liquidación de prueba en cada estado (Pendiente, Aprobada, Pagada, Anulada)

## Validation Scenarios

### Scenario 1: UI - Acciones Visibles Según Estado

**Setup**: Tener liquidaciones en cada estado

**Steps**:
1. Navegar a `/liquidacion-asesores`
2. Verificar acciones en tabla para cada registro

**Expected**:

| Estado | Acción Visible | Acción Oculta |
|--------|---------------|---------------|
| Pendiente | Eliminar | Reversar |
| Aprobada | Reversar | Eliminar |
| Pagada | Reversar | Eliminar |
| Anulada | Reversar | Eliminar |

**Validation Command**:
```bash
# Verificar en consola del navegador
# Cada fila debe mostrar SOLO la acción correspondiente
```

---

### Scenario 2: Eliminar - Liquidación Pendiente

**Setup**: Liquidación en estado "Pendiente" sin descuentos ni pagos

**Steps**:
1. Hacer clic en "Eliminar" de la liquidación Pendiente
2. Verificar que aparece modal de confirmación
3. Confirmar eliminación
4. Verificar toast de éxito
5. Verificar que la liquidación desaparece del listado

**Expected**:
- Modal de confirmación visible
- Toast: "Liquidación eliminada correctamente"
- Registro no visible en tabla (filtrado por ELIMINADA=TRUE)
- BD: ELIMINADA = TRUE

**Validation Query**:
```sql
SELECT ELIMINADA, UPDATED_AT 
FROM LIQUIDACIONES_ASESORES 
WHERE ID_LIQUIDACION_ASESOR = :id;
-- ELIMINADA debe ser TRUE
```

---

### Scenario 3: Eliminar - Rechazo por Estado No Permitido

**Setup**: Liquidación en estado "Aprobada"

**Steps**:
1. Verificar que NO existe botón "Eliminar" para esta liquidación
2. Intentar llamada directa a API (curl/script)

**Expected**:
- UI: No se muestra botón Eliminar
- API: Error 400 con mensaje "Solo se pueden eliminar liquidaciones Pendientes"

**Validation Command**:
```bash
# Si se pudiera invocar directamente:
curl -X POST /api/liquidaciones-asesores/eliminar \
  -H "Content-Type: application/json" \
  -d '{"id_liquidacion": 123}'
# Response: {"exitosa": false, "mensaje": "Solo se pueden eliminar liquidaciones Pendientes"}
```

---

### Scenario 4: Eliminar - Rechazo por Entidades Relacionadas

**Setup**: Liquidación Pendiente con descuentos registrados

**Steps**:
1. Hacer clic en "Eliminar"
2. Confirmar eliminación
3. Verificar mensaje de error

**Expected**:
- Toast/Error: "No se puede eliminar: tiene descuentos registrados"
- Liquidación permanece intacta

---

### Scenario 5: Reversar - Aprobada → Pendiente

**Setup**: Liquidación en estado "Aprobada"

**Steps**:
1. Hacer clic en "Reversar"
2. Verificar modal de confirmación (sin campo motivo)
3. Confirmar reversión
4. Verificar toast de éxito
5. Verificar cambio de estado

**Expected**:
- Modal sin campo de motivo
- Toast: "Liquidación reversada a Pendiente"
- BD: ESTADO_LIQUIDACION = "Pendiente", FECHA_APROBACION = NULL, USUARIO_APROBADOR = NULL

**Validation Query**:
```sql
SELECT ESTADO_LIQUIDACION, FECHA_APROBACION, USUARIO_APROBADOR
FROM LIQUIDACIONES_ASESORES 
WHERE ID_LIQUIDACION_ASESOR = :id;
-- Debe mostrar: Pendiente, NULL, NULL
```

---

### Scenario 6: Reversar - Pagada → Aprobada (con motivo)

**Setup**: Liquidación en estado "Pagada"

**Steps**:
1. Hacer clic en "Reversar"
2. Verificar modal con campo de motivo
3. Ingresar motivo < 10 caracteres → verificar botón deshabilitado
4. Ingresar motivo ≥ 10 caracteres
5. Confirmar reversión
6. Verificar cambio de estado

**Expected**:
- Modal con campo "Motivo" obligatorio
- Botón "Reversar" deshabilitado si motivo < 10 chars
- Toast: "Liquidación reversada a Aprobada"
- BD: ESTADO_LIQUIDACION = "Aprobada"

---

### Scenario 7: Reversar - Anulada → Pendiente (con motivo)

**Setup**: Liquidación en estado "Anulada"

**Steps**:
1. Hacer clic en "Reversar"
2. Verificar modal con campo de motivo
3. Ingresar motivo ≥ 10 caracteres
4. Confirmar reversión
5. Verificar cambio de estado

**Expected**:
- Modal con campo "Motivo" obligatorio
- Toast: "Liquidación reversada a Pendiente"
- BD: ESTADO_LIQUIDACION = "Pendiente", MOTIVO_ANULACION = NULL

---

### Scenario 8: Reversar - Rechazo por Estado Pendiente

**Setup**: Liquidación en estado "Pendiente"

**Steps**:
1. Verificar que NO existe botón "Reversar"
2. Intentar llamada directa a API

**Expected**:
- UI: No se muestra botón Reversar
- API: Error 400 con mensaje "No se pueden reversar liquidaciones Pendientes"

---

### Scenario 9: Consistencia UI-Backend

**Setup**: Liquidación en cualquier estado

**Steps**:
1. Verificar acciones visibles en UI
2. Intentar ejecutar acción opuesta vía API
3. Verificar que backend rechaza

**Expected**:
- UI y Backend en 100% de acuerdo
- 0 violaciones de reglas de negocio

---

### Scenario 10: Idempotencia de Eliminar

**Setup**: Liquidación ya eliminada

**Steps**:
1. Intentar eliminar nuevamente

**Expected**:
- Respuesta exitosa (idempotente)
- Sin cambios adicionales en BD

---

## Automated Tests

```bash
# Ejecutar tests del módulo
pytest tests/test_liquidacion_asesores.py -v

# Ejecutar tests de servicios
pytest tests/test_servicio_liquidacion_asesores.py -v

# Ejecutar linting
ruff check src/aplicacion/servicios/servicio_liquidacion_asesores.py
ruff check src/presentacion_reflex/state/liquidacion_asesores/form_state.py
```

## Manual Validation Checklist

- [ ] Liquidación Pendiente muestra solo "Eliminar"
- [ ] Liquidación Aprobada muestra solo "Reversar"
- [ ] Liquidación Pagada muestra solo "Reversar"
- [ ] Liquidación Anulada muestra solo "Reversar"
- [ ] Eliminar muestra modal de confirmación
- [ ] Eliminar con dependencias muestra error claro
- [ ] Reversar Aprobada→Pendiente funciona
- [ ] Reversar Pagada→Aprobada con motivo funciona
- [ ] Reversar Anulada→Pendiente con motivo funciona
- [ ] Motivo < 10 chars deshabilita botón
- [ ] Toast de éxito/error se muestra
- [ ] Grid se recarga después de operación
- [ ] Backend rechaza acciones inválidas
