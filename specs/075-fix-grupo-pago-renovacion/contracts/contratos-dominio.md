# Contrato: Calculadora de dominio (grupo y día de pago)

**Componente**: `src/dominio/servicios/calculadora_contratos.py` (`CalculadoraContratos`)
**Tipo**: interfaz interna de dominio (sin dependencias externas)

## Superficie del contrato

```python
@staticmethod
def calcular_grupo_operativo(fecha: Union[date, str]) -> int:
    """Retorna 1, 2 o 3 según el tramo V2 del día de la fecha (28-7, 8-17, 18-27)."""

@staticmethod
def calcular_dia_pago_mandato(fecha: Union[date, str]) -> int:
    """Retorna 10, 20 o 30 según el tramo V2 del día de la fecha."""

@staticmethod
def calcular_dia_pago_arrendamiento(fecha: Union[date, str]) -> int:
    """Retorna el día exacto de la fecha (regla propia de arrendamiento)."""

@staticmethod
def calcular_ciclo_pago_mandato(fecha: Union[date, str]) -> Tuple[int, int]:
    """Fachada de compatibilidad: (calcular_grupo_operativo, calcular_dia_pago_mandato)."""

@staticmethod
def calcular_fecha_inicio_renovacion(fecha_fin_original: str) -> str:
    """Fecha efectiva del período renovado = fecha_fin_original + 1 día (sin cambios)."""
```

## Precondiciones

- `fecha` es `date` o string ISO `YYYY-MM-DD` (se acepta prefijo de hasta 10 caracteres).
- Fecha parseable; en caso contrario se propaga `ValueError` (no se silencia).

## Postcondiciones (tabla de verdad)

| Día de la fecha | `calcular_grupo_operativo` | `calcular_dia_pago_mandato` | `calcular_dia_pago_arrendamiento` |
|---|---|---|---|
| 1..7 | 1 | 10 | 1..7 |
| 8..17 | 2 | 20 | 8..17 |
| 18..27 | 3 | 30 | 18..27 |
| 28..31 | 1 | 10 | 28..31 |

## Invariantes

- `calcular_grupo_operativo(f) in {1, 2, 3}` para toda fecha válida (determinístico).
- `calcular_ciclo_pago_mandato(f) == (calcular_grupo_operativo(f), calcular_dia_pago_mandato(f))`.
- Sin "magic numbers": límites expresados como constantes nombradas del módulo.
- Sin acceso a base de datos, hora del sistema ni estado global.

## Compatibilidad

- Las firmas existentes (`calcular_ciclo_pago_mandato`, `calcular_dia_pago_mandato`, `calcular_dia_pago_arrendamiento`) se conservan; los llamadores actuales no requieren cambios obligatorios.
- `calcular_ciclo_pago_arrendamiento` (referida en scripts obsoletos) **no** se reintroduce; la regla de arriendo es grupo V2 + día exacto.
