# Service Contract: reversar_pago_liquidacion

**Module**: ServicioFinanciero
**Method**: `reversar_pago_liquidacion(id_liquidacion: int, motivo: str, usuario_sistema: str) -> dict`

## Signature

```python
def reversar_pago_liquidacion(
    self,
    id_liquidacion: int,
    motivo: str,
    usuario_sistema: str,
) -> dict:
    """
    Reverses a payment on a liquidation (Pagada → Aprobada).
    
    Args:
        id_liquidacion: ID of the liquidation to reverse
        motivo: Justification (min 10 characters)
        usuario_sistema: Username performing the operation
    
    Returns:
        dict with keys:
            - exitosa (bool): Whether reversal was executed
            - mensaje (str): Human-readable result message
            - id_liquidacion (int): The liquidation ID
            - estado_anterior (str): State before operation
            - estado_nuevo (str): State after operation
    
    Raises:
        ValueError: If motivo < 10 chars, liquidation not found,
                    or liquidation in incompatible state (Cancelada)
    
    Idempotency:
        If liquidation is already in 'Aprobada' state, returns
        exitosa=True with mensaje indicating no changes were needed.
    """
```

## Preconditions

1. `len(motivo.strip()) >= 10`
2. Liquidation exists in database
3. Liquidation `ESTADO_LIQUIDACION` is either 'Pagada' (execute) or 'Aprobada' (no-op)

## Postconditions

- If executed: state changes to 'Aprobada', payment fields cleared, audit records inserted
- If no-op: no changes, returns success
- If failed: transaction rolled back, original state preserved

## Repository Method

```python
def reversar_pago(
    self,
    id_liquidacion: int,
    motivo: str,
    usuario_sistema: str,
) -> dict:
    """
    Reverses payment on a liquidation.
    
    Performs within a single transaction:
    1. Check state is 'Pagada'
    2. UPDATE: state → 'Aprobada', clear payment fields
    3. INSERT: AUDITORIA_CAMBIOS record with motivo
    
    Returns same dict as service layer.
    """
```
