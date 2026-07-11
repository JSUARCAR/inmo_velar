# Contrato de Interfaz: Filtros Avanzados Recaudos

**Date**: 2026-07-11

## Contrato: FiltrosRecaudo (Dominio)

```python
@dataclass(frozen=True)
class FiltrosRecaudo:
    """Contrato de filtros para la consulta paginada de recaudos."""
    estado: Optional[EstadoRecaudo] = None
    fecha_desde: Optional[str] = None        # Formato ISO 8601
    fecha_hasta: Optional[str] = None        # Formato ISO 8601
    dia_pago: Optional[List[str]] = None     # Multi-select: ["1", "15"] → IN (1, 15)
    ciclo_operativo: Optional[List[str]] = None  # Multi-select: ["1", "3"] → IN (1, 3)
    busqueda: Optional[str] = None
    sort_by: str = "fecha_pago"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 25
```

**Invariante**: Si `dia_pago` o `ciclo_operativo` es una lista vacía `[]`, se trata como `None` (sin filtro).

## Contrato: RepositorioRecaudo (Infraestructura)

```python
def listar_paginado(
    self,
    filtros: FiltrosRecaudo,
) -> Tuple[List[Dict[str, Any]], int]:
    """Retorna (lista_recaudos, total_registros).

    Filtros:
      - estado: AND exacto
      - dia_pago: OR multi-select (IN clause)
      - ciclo_operativo: OR multi-select (IN clause)
      - fecha_desde/hasta: AND rango
      - busqueda: OR multi-columna
    """
    ...

def contar_con_filtros(
    self,
    filtros: FiltrosRecaudo,
) -> int:
    """Cuenta registros que coinciden con los filtros. Misma lógica que listar_paginado."""
    ...
```

## Contrato: ServicioRecaudo (Aplicación)

```python
def listar_paginado(
    self,
    filtros: FiltrosRecaudo,
) -> Tuple[List[Dict[str, Any]], int]:
    """Orquesta conteo + consulta. Delegate a repo."""
    ...
```

## Contrato: State (Presentación)

```python
class RecaudosState(DocumentosStateMixin, IdempotencyStateMixin):
    # Filtros activos
    filter_estado: str = "Todos"
    filter_dia_pago: List[str] = []           # Multi-select
    filter_ciclo_operativo: List[str] = []    # Multi-select
    filter_fecha_desde: str = ""
    filter_fecha_hasta: str = ""

    # Opciones disponibles
    dias_pago_options: List[str] = ["Todos"] + [str(i) for i in range(1, 32)]
    ciclo_operativo_options: List[str] = ["Todos"]  # Cargadas dinámicamente

    # Handlers
    def set_filter_dia_pago(self, value: List[str]): ...
    def set_filter_ciclo_operativo(self, value: List[str]): ...
```

## Contrato: UI (Presentación)

Los filtros se renderizan en `recaudos_toolbar()` usando `advanced_filter_bar()`:

- **Pago Contrato**: rx.select multi, opciones 1-31, estilo consistente con filtros existentes
- **Ciclo Operativo**: rx.select multi, opciones dinámicas (Grupo 1, Grupo 2, ...), estilo consistente
