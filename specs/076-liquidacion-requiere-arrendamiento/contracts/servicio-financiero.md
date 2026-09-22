# Contrato: Servicio Financiero — Elegibilidad en generación de liquidaciones

**Feature**: 076-liquidacion-requiere-arrendamiento
**Modulo**: `src/aplicacion/servicios/servicio_financiero.py`

## Propósito

Garantizar que toda liquidación de propietario solo se genere cuando la propiedad cumple la combinación **Mandato ACTIVO + Arrendamiento ACTIVO sobre el mismo `ID_PROPIEDAD`** (FR-001, FR-002, FR-003). Es la puerta de entrada obligatoria para generación individual y masiva.

## Funciones modificadas

### `generar_liquidacion_mensual(id_contrato_m, periodo, datos_adicionales, usuario_sistema) -> Liquidacion`

**Cambio**: tras validar existencia del mandato y no duplicidad, se agrega la evaluación de elegibilidad:

1. `contrato = repo_mandato.obtener_por_id(id_contrato_m)`; si no existe → `ValueError` (integridad, se mantiene).
2. Si `not es_activo(contrato.estado_contrato_m)` → `LiquidacionNoElegibleError(motivo="sin mandato activo")`.
3. `arrendamiento = repo_arriendo.obtener_activo_por_propiedad(contrato.id_propiedad)`; si `None` → `LiquidacionNoElegibleError(motivo="sin contrato de arrendamiento activo en esta propiedad")`.
4. No duplicidad por período (existente).
5. Resto del cálculo/cálculo financiero sin cambios (canon, comisión, IVA, gastos, incidentes).

**Excepción nueva de dominio**: `LiquidacionNoElegibleError(motivo: str)` en `src/dominio/excepciones/excepciones_liquidacion.py`; hereda de `ValueError` para compatibilidad con callers actuales, pero con semántica distinta (no es un error de integridad).

**Emisor de excluido**: el motivo DEBE estar en lenguaje de negocio (FR-010).

### `generar_liquidacion_propietario(id_propietario, periodo, datos_adicionales_por_contrato, usuario_sistema) -> ResultadoGeneracionPropietario`

**Cambio**:
- La query de contratos se restringe de
  ```sql
  WHERE ID_PROPIETARIO = %s AND ESTADO_CONTRATO_M = 'ACTIVO'
  ```
  a la versión conjunta con `EXISTS ... CONTRATOS_ARRENDAMIENTOS ... ESTADO_CONTRATO_A = 'ACTIVO'` (mismo ID_PROPIEDAD). Los contratos ACTIVO sin arrendamiento activo pasan al contador `no_elegibles` en vez de intentar generarse.
- `ResultadoGeneracionPropietario` se extiende con `no_elegibles: int = 0`.
- Los `LiquidacionNoElegibleError` de `generar_liquidacion_mensual` (llegada de mandato no activo) se cuentan como `no_elegibles`, nunca como `errores`.

### `ResultadoGeneracionPropietario` (extensión)

```python
@dataclass(frozen=True)
class ResultadoGeneracionPropietario:
    generadas: int = 0
    omitidas: int = 0       # ya existían para el período
    no_elegibles: int = 0   # NUEVO: mandato activo sin arrendamiento activo (o mandato no activo)
    errores: int = 0
```

## Value Objects / excepciones nuevos
- La regla de elegibilidad se materializa directamente en la capa de Aplicacion via LiquidacionNoElegibleError (conteniendo el motivo de negocio), sin recurrir a un Value Object intermedio (eliminado per T049).
- `LiquidacionNoElegibleError` (`src/dominio/excepciones/excepciones_liquidacion.py`).

## Llamadores afectados

- `generar_liquidacion_propietario` → ya captura `LiquidacionNoElegibleError` como `no_elegibles`.
- `LiquidacionesState.generar_liquidacion_masiva` → consolida `total_no_elegibles` y lo muestra en el resumen/toast.
- Formulario individual → consultas de candidatos (ver contrato `servicio-financiero.md` + UI) listan solo combinación 1.

## Restricciones no funcionales

- `%s` en todos los placeholders; sin `except Exception` genérico nuevo.
- Type hints completos; docstring Google Style en las funciones modificadas.
- Cobertura de tests > 90% en la lógica nueva del servicio.