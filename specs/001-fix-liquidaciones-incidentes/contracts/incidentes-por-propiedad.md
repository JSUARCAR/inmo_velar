# Contract: Obtener Incidentes por Propiedad

**Date**: 2026-07-06

## Descripción

Contrato para obtener la lista de incidentes disponibles para una propiedad específica, utilizada por el modal de selección de incidentes.

## Input

### Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| id_propiedad | integer | Sí | ID de la propiedad de la liquidación |
| id_liquidacion | integer | Sí | ID de la liquidación actual (para excluir ya asociados) |

### Ejemplo de Llamada

```python
# Desde liquidaciones_state.py
incidentes = obtener_incidentes_por_propiedad(
    id_propiedad=123,
    id_liquidacion=456
)
```

## Output

### Estructura de Respuesta

```python
{
    "success": bool,
    "data": [
        {
            "id": int,                    # ID del incidente
            "descripcion": str,           # Descripción del incidente
            "costo": float,               # Costo total del incidente
            "costo_view": str,            # Costo formateado (ej: "$1.500.000")
            "estado": str,                # Estado del incidente
            "estado_pago": str,           # Estado de pago
            "propiedad": str,             # Dirección de la propiedad
            "propietario": str,           # Nombre del propietario
            "num_cuota": int,             # Número de cuota disponible
            "valor_cuota": float,         # Valor de la cuota
            "valor_cuota_view": str,      # Valor formateado
            "ya_asociado": bool           # True si ya está asociado a esta liquidación
        }
    ],
    "message": str                        # Mensaje de error (si success=False)
}
```

### Ejemplo de Respuesta Exitosa

```json
{
    "success": true,
    "data": [
        {
            "id": 789,
            "descripcion": "Daño en pared del garaje",
            "costo": 1500000,
            "costo_view": "$1.500.000",
            "estado": "Aprobado",
            "estado_pago": "Pendiente",
            "propiedad": "Calle Falsa 123",
            "propietario": "Juan Pérez",
            "num_cuota": 1,
            "valor_cuota": 500000,
            "valor_cuota_view": "$500.000",
            "ya_asociado": false
        }
    ],
    "message": ""
}
```

### Ejemplo de Respuesta con Error

```json
{
    "success": false,
    "data": [],
    "message": "Propiedad no encontrada"
}
```

## Restricciones

### Filtros Obligatorios

1. **Estado del incidente**: Solo incidentes con estado en `['Aprobado', 'En Reparacion', 'Finalizado']`
2. **Estado de pago**: Solo incidentes con `ESTADO_PAGO != 'Pagado'`
3. **Propiedad**: Solo incidentes con `ID_PROPIEDAD = id_propiedad`
4. **Cuota disponible**: Solo incidentes con al menos una cuota que pueda asociarse

### Ordenamiento

- Por `ID_INCIDENTE` descendente (más recientes primero)

## Casos de Uso

### CU1: Modal de Selección de Incidentes

1. Usuario abre modal de selección de incidentes
2. Sistema obtiene `ID_CONTRATO_M` desde la liquidación
3. Sistema consulta `ID_PROPIEDAD` desde el contrato
4. Sistema llama a `obtener_incidentes_por_propiedad(id_propiedad, id_liquidacion)`
5. Sistema muestra lista filtrada de incidentes
6. Usuario selecciona uno o varios incidentes
7. Sistema asocia incidentes seleccionados a la liquidación

### CU2: Edición de Liquidación

1. Usuario abre formulario de edición
2. Sistema carga datos de la liquidación incluyendo `valor_incidentes`
3. Usuario modifica campos (incluyendo observaciones)
4. Sistema guarda cambios manteniendo `valor_incidentes` existente

## Métricas de Rendimiento

| Métrica | Objetivo |
|---------|----------|
| Tiempo de respuesta | < 3 segundos |
| Throughput | > 100 consultas/segundo |
| Disponibilidad | 99.9% |

## Seguridad

### Autenticación

- Requiere usuario autenticado
- Requiere rol de Administrador o Asesor

### Autorización

- Solo usuarios con permiso de edición pueden modificar liquidaciones
- Solo usuarios con permiso de asociación pueden vincular incidentes

### Auditoría

- Todas las asociaciones quedan registradas con `ASOCIADO_POR` y `CREATED_AT`