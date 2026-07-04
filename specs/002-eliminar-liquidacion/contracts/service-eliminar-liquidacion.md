# Service Contract: eliminar_liquidacion

**Service**: `ServicioFinanciero`
**Method**: `eliminar_liquidacion()`
**Feature**: 002-eliminar-liquidacion

## Method Signature

```python
def eliminar_liquidacion(
    self,
    id_liquidacion: int,
    usuario_sistema: str,
) -> dict:
    """
    Elimina una liquidación (soft delete) si no está en estado "Pagada".
    
    Args:
        id_liquidacion: ID de la liquidación a eliminar
        usuario_sistema: Usuario que ejecuta la operación
    
    Returns:
        dict con:
            - exitosa (bool): True si la operación fue exitosa
            - mensaje (str): Mensaje descriptivo del resultado
            - id_liquidacion (int): ID de la liquidación
            - estado_anterior (str): Estado antes de la eliminación
            - operacion_id (str): ID único de la operación para trazabilidad
    
    Raises:
        ValueError: Si la liquidación no existe, está en estado "Pagada", 
                    o ya fue eliminada previamente
    """
```

## Business Logic

```
1. VALIDATE liquidation exists → raise ValueError if not found
2. VALIDATE eliminada == False → raise ValueError if already deleted (idempotent: return success instead)
3. VALIDATE estado_liquidacion != "Pagada" → raise ValueError with clear message
4. BEGIN TRANSACTION
5. UPDATE LIQUIDACIONES SET ELIMINADA=TRUE, UPDATED_AT, UPDATED_BY
6. UPDATE DOCUMENTOS SET ID_ENTIDAD_REFERENCIA=NULL WHERE TABLA='LIQUIDACIONES' AND ID=id
7. INSERT AUDITORIA_CAMBIOS record
8. COMMIT TRANSACTION
9. INVALIDATE caches (if applicable)
10. RETURN result dict
```

## Validation Rules

| Check | Condition | Error |
|-------|-----------|-------|
| Exists | `liquidacion is not None` | "No se encontró la liquidación con ID {id}" |
| Not deleted | `liquidacion.eliminada == False` | (idempotent: return success) |
| Not paid | `liquidacion.estado_liquidacion != "Pagada"` | "Las liquidaciones en estado Pagada forman parte del histórico financiero y no pueden eliminarse." |

## Idempotency Behavior

| Scenario | Behavior |
|----------|----------|
| Liquidation not found | ValueError (first attempt) |
| Liquidation already deleted | Return success (no-op) |
| Liquidation in "Pagada" state | ValueError (always blocked) |
| Liquidation in other states | Execute deletion |

## Audit Record

```python
repo_auditoria.guardar_cambio(
    tabla="LIQUIDACIONES",
    id_registro=id_liquidacion,
    tipo_operacion="DELETE",
    valor_anterior=str(liquidacion.estado_liquidacion),
    valor_nuevo="ELIMINADA",
    usuario=usuario_sistema,
    motivo_cambio=f"Eliminación de liquidación - estado anterior: {liquidacion.estado_liquidacion}"
)
```

## Error Responses

| Error | HTTP-like | Message |
|-------|-----------|---------|
| Not found | 404 | "No se encontró la liquidación con ID {id}" |
| Already deleted | 200 | "La liquidación ya fue eliminada previamente" (idempotent) |
| Paid state | 403 | "Las liquidaciones en estado Pagada forman parte del histórico financiero y no pueden eliminarse." |
| DB error | 500 | "Error al eliminar la liquidación: {str(e)}" |

## Success Response

```python
{
    "exitosa": True,
    "mensaje": "Liquidación eliminada correctamente",
    "id_liquidacion": 123,
    "estado_anterior": "En Proceso",
    "operacion_id": "DEL-LIQ-123-20260630143022"
}
```

## Repository Method

```python
def eliminar(self, id_liquidacion: int, usuario_sistema: str) -> None:
    """
    Soft delete: sets ELIMINADA=TRUE.
    Idempotent: no-op if already deleted.
    """
    conn = self.db.obtener_conexion()
    cursor = conn.cursor()
    placeholder = self.db.get_placeholder()
    
    cursor.execute(f"""
        UPDATE LIQUIDACIONES SET
            ELIMINADA = TRUE,
            UPDATED_AT = {placeholder},
            UPDATED_BY = {placeholder}
        WHERE ID_LIQUIDACION = {placeholder} AND ELIMINADA = FALSE
    """, (datetime.now().isoformat(), usuario_sistema, id_liquidacion))
    
    conn.commit()
```
