# Contrato: propagación del canon en renovación

**Feature**: `073-fix-renovacion-integer-range`

Contrato de comportamiento de `actualizar_canon_liquidaciones_futuras`
(servicio de arrendamientos) tras la corrección. Sin cambios de firma.

## Entradas

| Parámetro | Tipo | Restricción |
|---|---|---|
| id_contrato_a | int | Contrato ACTIVO existente |
| canon_nuevo | int | 0 < canon ≤ 10.000.000 (mayor ⇒ error de dominio, no SQL) |
| fecha_renovacion | str ISO `YYYY-MM-DD` | Solo mes ≥ su mes calendario |
| usuario | str | Auditoría |

## Salidas

- N.º de liquidaciones actualizadas (0 si no hay futuras: éxito igual).
- Por cada fila: `canon_bruto` = canon nuevo;
  `comision_monto = trunc(canon × comision_porcentaje / 10000)` calculado sin
  overflow intermedio; `iva_comision = trunc(comision × 0.19)` si aplica;
  `total_ingresos/egresos/neto` consistentes; fila de auditoría solo si hubo
  cambio real.

## Errores

| Caso | Señal |
|---|---|
| Derivado fuera de rango int4 | Excepción de dominio con campo + valor → mensaje operativo no técnico (nunca error crudo) |
| Fallo a mitad de la renovación | Rollback total (la renovación completa revierte) |
| Reintento / concurrencia | Idempotente: un único registro de historial |

## Invariantes

- Historia (meses pasados, renovaciones previas) intacta.
- `verificar_propagacion_canon` reporta cero inconsistencias tras renovar.
