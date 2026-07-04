# Data Model and State Contracts

## Entity/DTO Modificados (Application Layer)

La entidad de dominio de Liquidaciones (`Liquidacion`) no requiere cambios, ya que `ciclo_operativo` (o equivalente, como fecha/período) ya forma parte del modelo base según las asunciones. Los cambios aplican a los objetos de estado y consulta.

### Estado de Reflex (Presentation Layer)
Se ampliará el State de Liquidaciones para albergar los nuevos controles:

```python
class EstadoLiquidacion(rx.State):
    # Valores de ordenamiento
    columna_orden: str = "" # "monto", "fecha", "propietario", etc.
    orden_descendente: bool = False
    
    # Nuevo filtro
    filtro_ciclo_operativo: str = "" 
    
    # ... resto del estado
```

### Parámetros de Consulta (Application/Infrastructure Layer)
La función/método de consulta en el servicio y en el repositorio deberá soportar:

- `ciclo_operativo: Optional[str]`
- `order_by: Optional[str]`
- `order_desc: bool`

Ejemplo conceptual en el repositorio:
```python
def obtener_liquidaciones_filtradas(self, ..., ciclo_operativo: str = None, order_by: str = None, order_desc: bool = False):
    # La validación de order_by debe hacerse contra una lista blanca (whitelist) de columnas 
    # permitidas para evitar SQL Injection en la instrucción ORDER BY.
```

## UI Component Contracts
El componente del encabezado de la tabla (`HeaderCell` o similar) tendrá un contrato visual para invocar el evento:

- **Input**: Nombre interno de la columna (str)
- **Action**: Event handler `EstadoLiquidacion.alternar_orden(columna)`
- **Output**: Renderizar ícono `rx.icon("arrow_down")` o `rx.icon("arrow_up")` si la columna coincide con `columna_orden`.
