# Research: Fix Sincronización Incidentes - Liquidaciones

**Date**: 2026-07-02
**Feature**: 004-fix-sincronizacion-incidentes-liquidaciones

## Decision Log

### D1: Estrategia de Sincronización Triggers vs Aplicación

**Decision**: Mantener triggers como fuente primaria de `VALOR_INCIDENTES`, sincronizar cálculos en capa de aplicación después del commit.

**Rationale**: 
- Los triggers ya funcionan correctamente para actualizar `VALOR_INCIDENTES`
- Mover toda la lógica a aplicación aumentaría riesgo de regresión
- La sincronización post-commit permite usar el valor fresco de la BD

**Alternatives Considered**:
- Eliminar triggers y mover todo a aplicación: Rechazado por alto riesgo de regresión
- Mantener triggers solo para auditoría: Rechazado por duplicación innecesaria

**Implementation**:
```python
# Después del commit de la transacción:
# 1. Ejecutar query para obtener VALOR_INCIDENTES actualizado
# 2. Llamar calcular_totales() con el nuevo valor
# 3. Actualizar liquidación con neto_a_pagar correcto
```

---

### D2: Manejo de Observaciones - Append vs Reemplazo

**Decision**: Implementar lógica de append para IDs de incidentes, preservando observaciones existentes del usuario.

**Rationale**:
- Permite trazabilidad completa de todos los incidentes asociados
- Preserva notas manuales del usuario
- Formato consistente: "Inc #101\nInc #205"

**Alternatives Considered**:
- Reemplazo simple: Rechazado por pérdida de información
- Campo separado para IDs de incidentes: Rechazado por requerir cambio de schema

**Implementation**:
```python
def agregar_id_incidente_observaciones(observaciones: str, id_incidente: int) -> str:
    """Agrega ID de incidente a observaciones existentes."""
    nuevo_id = f"Inc #{id_incidente}"
    if not observaciones:
        return nuevo_id
    if nuevo_id in observaciones:
        return observaciones  # Ya existe, no duplicar
    return f"{observaciones}\n{nuevo_id}"
```

---

### D3: Manejo de Overflow de Observaciones

**Decision**: Cuando las observaciones excedan la capacidad del campo, mantener solo los IDs de incidentes más recientes.

**Rationale**:
- Las asociaciones más recientes son las que impactan el estado financiero actual
- Los IDs más antiguos pueden recuperarse del histórico de auditoría
- Evita rechazar operaciones válidas por límite de espacio

**Alternatives Considered**:
- Truncar manteniendo los primeros N caracteres: Rechazado por cortar IDs incompletos
- Rechazar operación con error: Rechazado por impacto en UX

**Implementation**:
```python
def truncar_observaciones(observaciones: str, max_longitud: int = 500) -> str:
    """Trunca observaciones manteniendo IDs más recientes."""
    if len(observaciones) <= max_longitud:
        return observaciones
    lineas = observaciones.split('\n')
    # Mantener solo líneas que empiecen con "Inc #"
    ids_incidentes = [l for l in lineas if l.startswith('Inc #')]
    otros = [l for l in lineas if not l.startswith('Inc #')]
    # Reconstruir con IDs más recientes primero
    resultado = '\n'.join(otros)
    for id_inc in reversed(ids_incidentes):
        candidato = f"{id_inc}\n{resultado}" if resultado else id_inc
        if len(candidato) <= max_longitud:
            resultado = candidato
        else:
            break
    return resultado
```

---

### D4: Persistencia de ESTADO_PAGO

**Decision**: Agregar `ESTADO_PAGO` al UPDATE SQL del repositorio de incidentes.

**Rationale**:
- El servicio calcula correctamente el estado en memoria
- El repositorio no lo persiste porque no está en el UPDATE
- Solución simple: agregar el campo al query

**Alternatives Considered**:
- Usar trigger para actualizar ESTADO_PAGO: Rechazado por complejidad innecesaria
- Crear método separado para actualizar solo ESTADO_PAGO: Rechazado por overhead

**Implementation**:
```sql
-- ANTES:
UPDATE INCIDENTES SET
    ESTADO = ..., DESCRIPCION = ..., FECHA_MODIFICACION = ...
WHERE ID_INCIDENTE = %s;

-- DESPUÉS:
UPDATE INCIDENTES SET
    ESTADO = ..., DESCRIPCION = ..., ESTADO_PAGO = ..., FECHA_MODIFICACION = ...
WHERE ID_INCIDENTE = %s;
```

---

### D5: Mapeo de Campo en Formulario de Edición

**Decision**: Corregir el mapeo del campo "Incidentes" para que apunte a `valor_incidentes` en lugar de `gastos_reparaciones`.

**Rationale**:
- El bug causa que editar "Incidentes" modifique "Gastos Reparaciones"
- Solución simple: cambiar el nombre del campo en el diccionario del formulario

**Alternatives Considered**:
- Crear campo separado en form_data: Rechazado por overhead innecesario
- Renombrar campo existente: Rechazado por impacto en otras partes del código

**Implementation**:
```python
# ANTES (liquidacion_edit_form.py):
form_field_editable(
    "Incidentes",
    "gastos_reparaciones",  # ← INCORRECTO
    LiquidacionesState.form_data["valor_incidentes"],
)

# DESPUÉS:
form_field_editable(
    "Incidentes",
    "valor_incidentes",  # ← CORRECTO
    LiquidacionesState.form_data["valor_incidentes"],
)
```

---

### D6: Recálculo de NETO_A_PAGAR

**Decision**: After each association/disassociation, query the database for the updated `VALOR_INCIDENTES` and recalculate `NETO_A_PAGAR`.

**Rationale**:
- El trigger actualiza `VALOR_INCIDENTES` pero no `NETO_A_PAGAR`
- La aplicación debe sincronizarse con el valor fresco de la BD
- Evita inconsistencias entre capas

**Alternatives Considered**:
- Modificar trigger para también calcular NETO_A_PAGAR: Rechazado por acoplamiento excesivo
- Calcular en memoria sin consultar BD: Rechazado por riesgo de desincronización

**Implementation**:
```python
def despues_asociar_incidente(id_liquidacion: int) -> None:
    """Recalcula NETO_A_PAGAR después de asociar incidente."""
    # 1. Obtener VALOR_INCIDENTES fresco de la BD (post-trigger)
    valor_incidentes = repositorio.calcular_total_descuentos(id_liquidacion)
    
    # 2. Obtener liquidación actualizada
    liquidacion = repositorio.obtener_por_id(id_liquidacion)
    
    # 3. Asignar valor fresco
    liquidacion.valor_incidentes = valor_incidentes
    
    # 4. Recalcular totales
    liquidacion.calcular_totales()
    
    # 5. Persistir (sin tocar VALOR_INCIDENTES, eso lo hace el trigger)
    repositorio.actualizar(liquidacion)
```

---

### D7: Estrategia de Testing

**Decision**: Unit tests para lógica de negocio + integration tests para persistencia.

**Rationale**:
- Cumple con constitución (>90% cobertura)
- Valida lógica aislada y sincronización con BD
- Cubre los 5 bugs identificados

**Test Cases**:
1. **Unit**: `test_agregar_id_incidente_observaciones` - append correcto
2. **Unit**: `test_truncar_observaciones` - overflow handling
3. **Unit**: `test_calcular_totales_con_valor_incidentes` - recálculo
4. **Integration**: `test_persistencia_estado_pago` - UPDATE incluye campo
5. **Integration**: `test_sincronizacion_neto_a_pagar` - valor fresco de BD

---

## Research Summary

| # | Decision | Impact | Risk |
|---|----------|--------|------|
| D1 | Triggers como fuente primaria | Alto | Bajo |
| D2 | Append de observaciones | Alto | Bajo |
| D3 | Overflow de observaciones | Medio | Bajo |
| D4 | Persistencia ESTADO_PAGO | Alto | Bajo |
| D5 | Mapeo campo edición | Alto | Bajo |
| D6 | Recálculo NETO_A_PAGAR | Alto | Medio |
| D7 | Estrategia testing | Alto | Bajo |

**Total decisiones**: 7
**Ambigüedades residuales**: 0
**Listo para fase de diseño**: ✅ Sí
