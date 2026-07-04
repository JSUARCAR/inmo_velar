# Service Contracts: Fix Sincronización Incidentes - Liquidaciones

**Date**: 2026-07-02
**Feature**: 004-fix-sincronizacion-incidentes-liquidaciones

## Overview

Este documento define los contratos de servicio para las operaciones de asociación/desasociación de incidentes a liquidaciones, incluyendo los cambios requeridos para corregir los bugs identificados.

---

## 1. ServicioIncidenteLiquidacion

### 1.1 asociar_incidente

**Propósito**: Asociar una cuota de incidente a una liquidación

**Contrato**:
```python
def asociar_incidente(
    self,
    id_incidente: int,
    id_liquidacion: int,
    numero_cuota: int,
    valor_descuento: Decimal,
    asociado_por: str
) -> dict:
    """
    Asocia un incidente a una liquidación.
    
    Args:
        id_incidente: ID del incidente a asociar
        id_liquidacion: ID de la liquidación destino
        numero_cuota: Número de cuota del plan de pago
        valor_descuento: Valor del descuento a aplicar
        asociado_por: Usuario que realiza la asociación
    
    Returns:
        dict con estructura:
        {
            "exito": bool,
            "mensaje": str,
            "valor_incidentes_actualizado": Decimal,
            "neto_a_pagar_actualizado": Decimal,
            "observaciones_actualizadas": str
        }
    
    Raises:
        IncidenteNoEncontradoError: Si el incidente no existe
        LiquidacionNoEncontradaError: Si la liquidación no existe
        CuotaNoEncontradaError: Si la cuota no existe
        CuotaYaAsociadaError: Si la cuota ya está asociada
        PermisoDenegadoError: Si el usuario no es Administrador
    """
```

**Flujo Corregido**:
1. Validar permisos (solo Administradores)
2. Validar existencia de incidente, liquidación y cuota
3. Crear registro en `INCIDENTE_LIQUIDACION`
4. **Trigger ejecuta**: Actualizar `VALOR_INCIDENTES` en BD
5. **FIX**: Ejecutar query para obtener `VALOR_INCIDENTES` fresco
6. **FIX**: Agregar ID de incidente a observaciones (append)
7. **FIX**: Recalcular `NETO_A_PAGAR` con valor fresco
8. Actualizar `ESTADO_PAGO` del incidente
9. Persistir cambios en liquidación
10. Retornar resultado

---

### 1.2 desasociar_incidente

**Propósito**: Desasociar una cuota de incidente de una liquidación

**Contrato**:
```python
def desasociar_incidente(
    self,
    id_relacion: int,
    desasociado_por: str
) -> dict:
    """
    Desasocia un incidente de una liquidación.
    
    Args:
        id_relacion: ID de la relación en INCIDENTE_LIQUIDACION
        desasociado_por: Usuario que realiza la desasociación
    
    Returns:
        dict con estructura:
        {
            "exito": bool,
            "mensaje": str,
            "valor_incidentes_actualizado": Decimal,
            "neto_a_pagar_actualizado": Decimal,
            "observaciones_actualizadas": str
        }
    
    Raises:
        RelacionNoEncontradaError: Si la relación no existe
        PermisoDenegadoError: Si el usuario no es Administrador
    """
```

**Flujo Corregido**:
1. Validar permisos (solo Administradores)
2. Validar existencia de la relación
3. Obtener datos antes de eliminar
4. Eliminar registro de `INCIDENTE_LIQUIDACION`
5. **Trigger ejecuta**: Actualizar `VALOR_INCIDENTES` en BD
6. **FIX**: Ejecutar query para obtener `VALOR_INCIDENTES` fresco
7. **FIX**: Remover ID de incidente de observaciones (mantener otros)
8. **FIX**: Recalcular `NETO_A_PAGAR` con valor fresco
9. Actualizar `ESTADO_PAGO` del incidente
10. Persistir cambios en liquidación
11. Retornar resultado

---

### 1.3 obtener_total_descuentos

**Propósito**: Calcular el total de descuentos de incidentes para una liquidación

**Contrato**:
```python
def obtener_total_descuentos(
    self,
    id_liquidacion: int
) -> Decimal:
    """
    Obtiene el total de descuentos de incidentes para una liquidación.
    
    Args:
        id_liquidacion: ID de la liquidación
    
    Returns:
        Decimal con el total de descuentos
    
    Note:
        Este método consulta la BD directamente (no usa cache)
        para garantizar consistencia con los triggers.
    """
```

---

## 2. ServicioEstadoPago

### 2.1 recalcular_estado_pago_incidente

**Propósito**: Recalcular y persistir el estado de pago de un incidente

**Contrato**:
```python
def recalcular_estado_pago_incidente(
    self,
    id_incidente: int
) -> str:
    """
    Recalcula el estado de pago de un incidente basado en sus liquidaciones.
    
    Args:
        id_incidente: ID del incidente
    
    Returns:
        str con el nuevo estado de pago:
        - "Pendiente"
        - "Asociada"
        - "Parcialmente Pagado"
        - "Pagado"
    
    Raises:
        IncidenteNoEncontradoError: Si el incidente no existe
    """
```

**Lógica de Cálculo**:
```python
def _calcular_estado_pago(self, incidente: Incidente) -> str:
    """Calcula el estado de pago basado en liquidaciones asociadas."""
    liquidaciones = self.repo_relacion.obtener_liquidaciones_por_incidente(
        incidente.id
    )
    
    if not liquidaciones:
        return "Pendiente"
    
    # Obtener estados de las liquidaciones
    estados = []
    for liq in liquidaciones:
        liquidacion = self.repo_liquidacion.obtener_por_id(liq.id_liquidacion)
        estados.append(liquidacion.estado)
    
    # Calcular estado
    if all(estado == "Pagada" for estado in estados):
        return "Pagado"
    elif any(estado == "Pagada" for estado in estados):
        return "Parcialmente Pagado"
    elif any(estado == "En Proceso" for estado in estados):
        return "Asociada"
    else:
        return "Pendiente"
```

---

### 2.2 actualizar_estado_pago

**Propósito**: Persistir el estado de pago en la base de datos

**Contrato**:
```python
def actualizar_estado_pago(
    self,
    id_incidente: int,
    nuevo_estado: str
) -> bool:
    """
    Actualiza el estado de pago de un incidente en la base de datos.
    
    Args:
        id_incidente: ID del incidente
        nuevo_estado: Nuevo estado de pago
    
    Returns:
        bool indicando si la actualización fue exitosa
    
    Note:
        Este método DEBE incluir ESTADO_PAGO en el UPDATE SQL.
    """
```

---

## 3. RepositorioLiquidacionPostgres

### 3.1 obtener_por_id (actualizado)

**Propósito**: Obtener una liquidación por ID con todos sus campos

**Contrato**:
```python
def obtener_por_id(
    self,
    id_liquidacion: int
) -> Optional[Liquidacion]:
    """
    Obtiene una liquidación por su ID.
    
    Args:
        id_liquidacion: ID de la liquidación
    
    Returns:
        Liquidacion o None si no existe
    
    Note:
        DEBE incluir VALOR_INCIDENTES y NETO_A_PAGAR en el SELECT.
    """
```

**Query Requerido**:
```sql
SELECT 
    ID_LIQUIDACION,
    ID_CONTRATO,
    PERIODO,
    FECHA_GENERACION,
    CANON_BRUTO,
    IVA_CANON,
    TOTAL_INGRESOS,
    COMISION_MONTO,
    IVA_COMISION,
    GASTOS_ADMINISTRACION,
    GASTOS_SERVICIOS,
    GASTOS_REPARACIONES,
    PAGO_PREDIAL,
    OTROS_EGRESOS,
    TOTAL_EGRESOS,
    VALOR_INCIDENTES,
    NETO_A_PAGAR,
    ESTADO,
    FECHA_APROBACION,
    FECHA_PAGO,
    FECHA_CANCELACION,
    OBSERVACIONES,
    CREATED_AT,
    UPDATED_AT
FROM LIQUIDACIONES
WHERE ID_LIQUIDACION = %s;
```

---

### 3.2 actualizar (actualizado)

**Propósito**: Actualizar una liquidación existente

**Contrato**:
```python
def actualizar(
    self,
    liquidacion: Liquidacion
) -> bool:
    """
    Actualiza una liquidación existente.
    
    Args:
        liquidacion: Objeto Liquidacion con los campos actualizados
    
    Returns:
        bool indicando si la actualización fue exitosa
    
    Note:
        NO debe incluir VALOR_INCIDENTES en el UPDATE (lo maneja el trigger).
        DEBE incluir NETO_A_PAGAR y OBSERVACIONES.
    """
```

**Query Requerido**:
```sql
UPDATE LIQUIDACIONES SET
    FECHA_GENERACION = %s,
    CANON_BRUTO = %s,
    IVA_CANON = %s,
    TOTAL_INGRESOS = %s,
    COMISION_MONTO = %s,
    IVA_COMISION = %s,
    GASTOS_ADMINISTRACION = %s,
    GASTOS_SERVICIOS = %s,
    GASTOS_REPARACIONES = %s,
    PAGO_PREDIAL = %s,
    OTROS_EGRESOS = %s,
    TOTAL_EGRESOS = %s,
    NETO_A_PAGAR = %s,
    ESTADO = %s,
    FECHA_APROBACION = %s,
    FECHA_PAGO = %s,
    FECHA_CANCELACION = %s,
    OBSERVACIONES = %s,
    UPDATED_AT = NOW()
WHERE ID_LIQUIDACION = %s;
```

---

## 4. RepositorioIncidentesPostgres

### 4.1 actualizar (actualizado)

**Propósito**: Actualizar un incidente existente

**Contrato**:
```python
def actualizar(
    self,
    incidente: Incidente
) -> bool:
    """
    Actualiza un incidente existente.
    
    Args:
        incidente: Objeto Incidente con los campos actualizados
    
    Returns:
        bool indicando si la actualización fue exitosa
    
    Note:
        DEBE incluir ESTADO_PAGO en el UPDATE SQL.
    """
```

**Query Requerido**:
```sql
UPDATE INCIDENTES SET
    ESTADO = %s,
    DESCRIPCION = %s,
    ESTADO_PAGO = %s,
    FECHA_MODIFICACION = NOW()
WHERE ID_INCIDENTE = %s;
```

---

## 5. Formulario de Edición

### 5.1 liquidacion_edit_form (corregido)

**Propósito**: Formulario de edición de liquidación

**Cambio Requerido**:
```python
# ANTES (INCORRECTO):
form_field_editable(
    "Incidentes",
    "gastos_reparaciones",  # ← Mapeo incorrecto
    LiquidacionesState.form_data["valor_incidentes"],
)

# DESPUÉS (CORRECTO):
form_field_editable(
    "Incidentes",
    "valor_incidentes",  # ← Mapeo correcto
    LiquidacionesState.form_data["valor_incidentes"],
)
```

---

## 6. Utilidades de Observaciones

### 6.1 agregar_id_incidente

**Propósito**: Agregar ID de incidente a observaciones

**Contrato**:
```python
def agregar_id_incidente(
    observaciones: Optional[str],
    id_incidente: int
) -> str:
    """
    Agrega ID de incidente a observaciones existentes.
    
    Args:
        observaciones: Observaciones actuales (puede ser None o vacío)
        id_incidente: ID del incidente a agregar
    
    Returns:
        str con observaciones actualizadas
    
    Note:
        - Preserva observaciones existentes del usuario
        - No duplica IDs ya existentes
        - Formato: "Inc #{id}"
    """
```

### 6.2 remover_id_incidente

**Propósito**: Remover ID de incidente de observaciones

**Contrato**:
```python
def remover_id_incidente(
    observaciones: str,
    id_incidente: int
) -> str:
    """
    Remueve ID de incidente de observaciones.
    
    Args:
        observaciones: Observaciones actuales
        id_incidente: ID del incidente a remover
    
    Returns:
        str con observaciones actualizadas
    
    Note:
        - Solo remueve la línea específica del incidente
        - Preserva otras observaciones
        - Si no quedan IDs, retorna observaciones originales sin la línea
    """
```

### 6.3 truncar_observaciones

**Propósito**: Truncar observaciones cuando exceden la capacidad

**Contrato**:
```python
def truncar_observaciones(
    observaciones: str,
    max_longitud: int = 500
) -> str:
    """
    Trunca observaciones manteniendo IDs más recientes.
    
    Args:
        observaciones: Observaciones a truncar
        max_longitud: Longitud máxima permitida
    
    Returns:
        str con observaciones truncadas
    
    Note:
        - Mantiene observaciones del usuario
        - Mantiene IDs de incidentes más recientes
        - Descarta IDs más antiguos si es necesario
    """
```
