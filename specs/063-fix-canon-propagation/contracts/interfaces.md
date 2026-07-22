# Contracts: Corrección de Propagación de Canon en Renovaciones

**Date**: 2026-07-22
**Feature**: 063-fix-canon-propagation

## Interface: ServicioContratoArrendamiento

### Método: renovar_contrato

**Descripción**: Renueva un contrato de arrendamiento con un nuevo canon y propaga los cambios a módulos dependientes.

**Parámetros de entrada**:
```python
{
    "contrato_id": int,           # ID del contrato a renovar
    "canon_nuevo": Decimal,       # Nuevo canon de arrendamiento
    "fecha_renovacion": date      # Fecha de efectividad de la renovación
}
```

**Parámetros de salida**:
```python
{
    "exito": bool,
    "contrato_id": int,
    "canon_anterior": Decimal,
    "canon_nuevo": Decimal,
    "registros_liquidaciones_actualizados": int,
    "registros_recaudos_actualizados": int,
    "mensaje": str
}
```

**Comportamiento esperado**:
1. Actualizar `canon_arrendamiento` en CONTRATOS_ARRENDAMIENTOS
2. Propagar a CONTRATOS_MANDATOS (`canon_mandato`)
3. Propagar a PROPIEDADES (`canon_arrendamiento_estimado`)
4. **NUEVO**: Propagar a LIQUIDACIONES (`canon_bruto`) donde `fecha_generacion::date > fecha_renovacion`
5. **NUEVO**: Propagar a RECAUDOS (`valor_total`) donde `fecha_pago::date > fecha_renovacion`
6. Registrar en RENOVACIONES_CONTRATOS
7. Todo en una transacción atómica con rollback completo

**Errores posibles**:
- `ErrorContratoNoEncontrado`: El contrato especificado no existe
- `ErrorRenovacionFallida`: La propagación falló (rollback ejecutado)
- `ErrorBaseDeDatos`: Error de conexión o consulta

## Interface: RepositorioContrato

### Método: actualizar_canon_liquidaciones_futuras

**Descripción**: Actualiza el campo `canon_bruto` en liquidaciones futuras de un contrato.

**Parámetros de entrada**:
```python
{
    "contrato_id": int,           # ID del contrato
    "canon_nuevo": Decimal,       # Nuevo canon a aplicar
    "fecha_corte": date           # Fecha de corte (solo actualizar después de esta fecha)
}
```

**Parámetros de salida**:
```python
{
    "registros_actualizados": int
}
```

**Consulta SQL**:
```sql
UPDATE LIQUIDACIONES
SET canon_bruto = %s
WHERE id_contrato_m = (
    SELECT id_contrato_m FROM CONTRATOS_MANDATOS
    WHERE id_contrato_a = %s LIMIT 1
)
AND fecha_generacion::date > %s;
```

### Método: actualizar_valor_recaudos_futuros

**Descripción**: Actualiza el campo `valor_total` en recaudos futuros de un contrato.

**Parámetros de entrada**:
```python
{
    "contrato_id": int,           # ID del contrato
    "canon_nuevo": Decimal,       # Nuevo valor a aplicar
    "fecha_corte": date           # Fecha de corte (solo actualizar después de esta fecha)
}
```

**Parámetros de salida**:
```python
{
    "registros_actualizados": int
}
```

**Consulta SQL**:
```sql
UPDATE RECAUDOS
SET valor_total = %s
WHERE id_contrato_a = %s
AND fecha_pago::date > %s;
```

## Interface: VerificadorIntegridad

### Método: verificar_propagacion_canon

**Descripción**: Verifica que el canon en liquidaciones y recaudos coincida con el canon del contrato.

**Parámetros de entrada**:
```python
{
    "contrato_id": int            # ID del contrato a verificar (opcional, None = todos)
}
```

**Parámetros de salida**:
```python
{
    "total_verificados": int,
    "inconsistencias_encontradas": int,
    "detalles": [
        {
            "contrato_id": int,
            "tabla": str,          # "LIQUIDACIONES" o "RECAUDOS"
            "registro_id": int,
            "canon_esperado": Decimal,
            "canon_encontrado": Decimal,
            "severidad": str       # "ALTA", "MEDIA", "BAJA"
        }
    ]
}
```
