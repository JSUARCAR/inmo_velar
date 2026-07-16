# Contract: ServicioFinanciero - Generación de Liquidaciones

**Date**: 2026-07-15
**Feature**: 056-fix-liquidaciones-generation

## Interface: `generar_liquidacion_propietario`

### Firma Actual (ANTES)

```python
def generar_liquidacion_propietario(
    self,
    id_propietario: int,
    periodo: str,
    datos_adicionales_por_contrato: Optional[Dict],
    usuario_sistema: str,
) -> int:
```

**Retorno**: `int` - Cantidad de liquidaciones generadas.
**Excepciones**: `ValueError` cuando todas las liquidaciones ya existían.

### Firma Nueva (DESPUÉS)

```python
def generar_liquidacion_propietario(
    self,
    id_propietario: int,
    periodo: str,
    datos_adicionales_por_contrato: Optional[Dict],
    usuario_sistema: str,
) -> ResultadoGeneracionPropietario:
```

**Retorno**: `ResultadoGeneracionPropietario` - Dataclass con tres contadores.
**Excepciones**: Ninguna (los errores se encapsulan en el resultado).

### Contrato de Retorno

```python
@dataclass(frozen=True)
class ResultadoGeneracionPropietario:
    """Resultado de la generación de liquidaciones para un propietario."""
    generadas: int = 0
    omitidas: int = 0
    errores: int = 0
```

**Invariantes**:
- `generadas >= 0`
- `omitidas >= 0`
- `errores >= 0`
- `generadas + omitidas + errores` = cantidad total de contratos activos del propietario

### Cambios Comportamentales

| Escenario | Comportamiento Actual | Comportamiento Nuevo |
|-----------|----------------------|---------------------|
| Todos los contratos ya tienen liquidación | `raise ValueError` | `ResultadoGeneracionPropietario(generadas=0, omitidas=N, errores=0)` |
| Algunos contratos generados, otros ya existían | `return N` (solo cuenta generadas) | `ResultadoGeneracionPropietario(generadas=X, omitidas=Y, errores=0)` |
| Error real en un contrato | `ValueError` (se pierde en el catch) | `ResultadoGeneracionPropietario(generadas=X, omitidas=Y, errores=1)` |
| Contrato no encontrado | `raise ValueError` | `ResultadoGeneracionPropietario(generadas=X, omitidas=Y, errores=1)` |

## Interface: `generar_liquidacion_masiva` (State Handler)

### Cambios en el Handler

**ANTES**:
```python
generadas = 0
errores = 0
for id_propietario in id_propietarios_activos:
    try:
        servicio.generar_liquidacion_propietario(...)
        generadas += 1
    except Exception as e:
        errores += 1
```

**DESPUÉS**:
```python
total_generadas = 0
total_omitidas = 0
total_errores = 0
for id_propietario in id_propietarios_activos:
    resultado = servicio.generar_liquidacion_propietario(...)
    total_generadas += resultado.generadas
    total_omitidas += resultado.omitidas
    total_errores += resultado.errores
```

### Toast de Resultado

**ANTES**:
```python
if generadas == 0 and errores > 0:
    raise ValueError("Hubo errores generando todas las liquidaciones.")
# ...
mensaje = f"Se generaron {generadas} liquidaciones exitosamente."
if errores > 0:
    mensaje += f" (Omitidas/Error: {errores})"
```

**DESPUÉS**:
```python
if total_errores == 0 and total_generadas == 0 and total_omitidas > 0:
    # Todos ya existían - toast informativo
    yield rx.toast.info(f"0 generadas, {total_omitidas} ya existían", ...)
elif total_errores == 0:
    # Sin errores reales - toast de éxito
    yield rx.toast.success(f"{total_generadas} generadas, {total_omitidas} ya existían", ...)
else:
    # Con errores reales - toast de warning
    yield rx.toast.warning(f"{total_generadas} generadas, {total_omitidas} ya existían, {total_errores} con error", ...)
```

## Interface: `generar_liquidacion_mensual` (sin cambios)

La función `generar_liquidacion_mensual` no cambia. Sigue lanzando `ValueError` para duplicados y contratos no encontrados. Estas excepciones se capturan internamente en `generar_liquidacion_propietario` y se clasifican en el `ResultadoGeneracionPropietario`.
