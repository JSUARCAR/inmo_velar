# Research: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Feature**: 038-liquidacion-asesores-actions
**Date**: 2026-07-08

## R1: Soft Delete vs Hard Delete para Liquidaciones

**Decision**: Soft delete (marcar eliminada con flag)

**Rationale**: 
- Preserva integridad referencial con tablas hijas (DESCUENTOS_ASESORES, PAGOS_ASESORES)
- Cumple con requisito de auditoría financiera
- Permite recuperación si es necesario
- Consistente con patrón ya usado en Liquidaciones de Propietarios

**Alternatives considered**:
- Hard delete: Requiere CASCADE en foreign keys, pierde historial, riesgo de datos huérfanos
- Archivado: Más complejo, innecesario para este caso de uso

## R2: Estrategia de Eliminación Lógica

**Decision**: Agregar columna `ELIMINADA` (BOOLEAN DEFAULT FALSE) a LIQUIDACIONES_ASESORES

**Rationale**:
- Simple y explícito
- Compatible con queries existentes (agregar `WHERE eliminada = FALSE`)
- No requiere cambiar estado existente
- Fácil de reversar si se necesita

**Alternatives considered**:
- Usar estado "Eliminada": Conflictua con flujo de estados existente
- Usar timestamp `FECHA_ELIMINACION`: Menos explícito

## R3: Transiciones de Reversión

**Decision**: Implementar método `reversar` en servicio con lógica por estado

**Transitions**:
```
Aprobada → Pendiente  (revertir aprobación)
Pagada → Aprobada     (revertir pago, requiere motivo)
Anulada → Pendiente   (revertir anulación, requiere motivo)
```

**Rationale**:
- Aprobada→Pendiente: Operación simple, solo cambia estado y limpia campos de aprobación
- Pagada→Aprobada: Ya existe `reversar_pago_liquidacion` en módulo de propietarios como referencia
- Anulada→Pendiente: Requiere motivo para auditoría

**Alternatives considered**:
- Todas las reversiones a Pendiente: Pierde información de aprobación para Pagadas
- Reversión sin motivo: No cumple requisitos de auditoría

## R4: Validación de Integridad Referencial

**Decision**: Verificar existencia de registros relacionados antes de eliminar

**Checks**:
- DESCUENTOS_ASESORES: Si existen, rechazar eliminación
- PAGOS_ASESORES: Si existen pagos, rechazar eliminación
- LIQUIDACIONES_CONTRATOS: Si existen, rechazar eliminación

**Rationale**:
- Previene datos huérfanos
- Mensaje claro al usuario sobre por qué no se puede eliminar
- ON DELETE CASCADE ya existe en algunas tablas pero no se debe depender de ello

## R5: UI Action Visibility Logic

**Decision**: Renderizado condicional basado en `estado_liquidacion`

**Rules**:
```python
# En grid y detail modal
if estado == "Pendiente":
    show_eliminar = True
    show_reversar = False
else:  # Aprobada, Pagada, Anulada
    show_eliminar = False
    show_reversar = True
```

**Rationale**:
- Simple y claro
- Consistente con reglas de negocio
- Fácil de mantener

## R6: Modal de Confirmación

**Decision**: Reutilizar patrón existente de modales (show_annul_modal)

**Implementation**:
- Para Eliminar: Modal de confirmación simple (sí/no)
- Para Reversar: Modal con campo de motivo obligatorio (si estado es Pagada o Anulada)

**Rationale**:
- Consistencia con UX existente
- Menos código nuevo
- Usuarios ya familiarizados con el patrón

## R7: Backend Validation

**Decision**: Validar estado en capa de servicio antes de ejecutar

**Rules**:
```python
def eliminar_liquidacion(id, usuario):
    liq = repo.obtener_por_id(id)
    if liq.estado_liquidacion != "Pendiente":
        raise ValueError("Solo se pueden eliminar liquidaciones Pendientes")
    if liq.eliminada:
        return {"exitosa": True, "mensaje": "Ya fue eliminada"}
    # Proceed with soft delete

def reversar_liquidacion(id, motivo, usuario):
    liq = repo.obtener_por_id(id)
    if liq.estado_liquidacion == "Pendiente":
        raise ValueError("No se pueden reversar liquidaciones Pendientes")
    if liq.estado_liquidacion == "Pagada" and len(motivo) < 10:
        raise ValueError("Motivo requerido (mínimo 10 caracteres)")
    if liq.estado_liquidacion == "Anulada" and len(motivo) < 10:
        raise ValueError("Motivo requerido (mínimo 10 caracteres)")
    # Proceed with state transition
```

**Rationale**:
- Reglas de negocio en capa servidor (no depende de UI)
- Validación idempotente
- Mensajes de error claros
