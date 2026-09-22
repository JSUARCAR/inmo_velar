# Contrato: Auditoría de Elegibilidad (solo lectura y re-generable)

**Feature**: 076-liquidacion-requiere-arrendamiento
**Modulo**: `src/aplicacion/servicios/servicio_auditoria_elegibilidad.py`

## Propósito

Reporte de SOLO LECTURA de liquidaciones históricas generadas bajo la regla anterior (sin exigir arrendamiento activo). Evalúa cada liquidación contra el estado de Mandato/Arrendamiento VIGENTE EN SU `FECHA_GENERACION` (Q2), marca las que incumplen y las describe con período, propiedad, propietario y motivo (FR-007, SC-004). No persiste resultados: es re-generable a demanda con los mismos criterios registrados (Q7).

## Contrato de la consulta

### `AuditoriaElegibilidadResultado`

```python
@dataclass(frozen=True)
class AuditoriaElegibilidadResultado:
    criterios: CriteriosAuditoria      # fecha_reconstruccion, filtro_regla, periodo
    liquidaciones_auditadas: int
    no_elegibles: List[LiquidacionInelegible]
```

```python
@dataclass(frozen=True)
class CriteriosAuditoria:
    fecha_reconstruccion: str   # ISO; permite re-generar con los mismos criterios
    filtro_regla: str           # "mandato_activo + arrendamiento_activo (misma ID_PROPIEDAD)"
    periodo: str                # "Todos" o YYYY-MM
```

```python
@dataclass(frozen=True)
class LiquidacionInelegible:
    id_liquidacion: int
    periodo: str
    fecha_generacion: str
    id_propiedad: int
    direccion_propiedad: str
    id_propietario: int
    nombre_propietario: str
    motivo: str                 # lenguaje de negocio (FR-010)
```

### `auditar(periodo: Optional[str] = None, fecha_reconstruccion: Optional[str] = None) -> AuditoriaElegibilidadResultado`

Comportamiento:
1. Toma una SOLA pasada de lectura: liquidaciones (+ mandato → propiedad → propietario + datos del arrendamiento de esa propiedad).
2. Para cada liquidación, determina si en `fecha_generacion` se cumplía la combinación completa usando intervalos `[FECHA_INICIO_*, FECHA_FIN_*]` de mandato/arrendamiento vigentes y su estado (ver nota técnica en `research.md` Decision 6).
3. Devuelve solo las `no_elegibles` en `no_elegibles` (100% auditadas en `liquidaciones_auditadas`).
4. NO inserta, NO actualiza, NO elimina ninguna fila.
5. Registra `criterios` (fecha de reconstrucción, filtro, período) en el log de ejecución para permitir re-generación idéntica a demanda; no se almacenan copias de resultados en BD.

## Motivo por combinación

| Combinación | motivo (lenguaje de negocio) |
|-------------|------------------------------|
| Mandato ACTIVO sin arrendamiento ACTIVO en la misma propiedad (no existe / inactivo / finalizado) | `sin contrato de arrendamiento activo en esta propiedad` |
| Mandato no ACTIVO en la fecha de generación | `sin contrato de mandato activo` |
| Ambos incumplidos | `sin contrato de mandato activo y sin contrato de arrendamiento activo` |

## Regla de oro

100% SOLO LECTURA. Prohibida toda escritura a `LIQUIDACIONES`, `CONTRATOS_*`, `PROPIEDADES` o tablas derivadas desde este servicio (FR-007, SC-004). Cualquier remediación futura es decisión de negocio separada.

## Restricciones no funcionales

- SQL solo `SELECT` con `%s`; sin `except Exception` genérico.
- Rendimiento: < 60s sobre el volumen histórico actual (Decisión 8 en `research.md`).
- Type hints completos; docstring Google Style.