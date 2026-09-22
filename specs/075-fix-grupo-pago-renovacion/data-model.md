# Data Model: Grupo de pago correcto y atómico en la renovación de contratos

**Feature**: 075-fix-grupo-pago-renovacion | **Date**: 2026-09-21 | **Fuente**: [spec.md](./spec.md), [research.md](./research.md)

Sin cambios de esquema: el modelo describe entidades y reglas vigentes que la feature corrige y utiliza. Todos los campos de fecha se almacenan como TEXT ISO `YYYY-MM-DD` en contrato/renovación (se usa `NULLIF(campo,'')::date` para comparaciones en PostgreSQL).

---

## 1. ContratoArrendamiento

**Tabla**: `CONTRATOS_ARRENDAMIENTOS` | **Entidad**: `src/dominio/entidades/contrato_arrendamiento.py`

| Campo | Tipo | Regla en esta feature |
|---|---|---|
| `id_contrato_a` | INTEGER (PK) | Identidad |
| `id_propiedad` | INTEGER (FK) | Una propiedad tiene máximo 1 arriendo ACTIVO |
| `fecha_inicio_contrato_a` | TEXT ISO | Inicio del primer período; **no cambia** en renovación (historia) |
| `fecha_fin_contrato_a` | TEXT ISO | Se extiende con `sumar_meses(fecha_fin, duracion)` o fecha personalizada |
| `duracion_contrato_a` | INTEGER (meses) | Determina periodicidad y aplica IPC si ≥ 12 |
| `canon_arrendamiento` | INTEGER | Se incrementa por IPC vigente si duración ≥ 12 |
| `fecha_pago` | TEXT numérico | **Debe ser el día exacto de la fecha efectiva** del período vigente |
| `grupo_operativo` | INTEGER | **Debe ser el tramo V2 (1/2/3) de la fecha efectiva** del período vigente; nunca 0 en ACTIVO |
| `estado_contrato_a` | TEXT/Enum | Solo `ACTIVO` es renovable/auditable |
| `fecha_renovacion_contrato_a` | TEXT ISO | Fecha de ejecución de la última renovación (no base de cálculo) |

**Transición de renovación válida**: `ACTIVO → ACTIVO` (extiende `fecha_fin_contrato_a`, actualiza canon y grupo/día de pago; registra historial).

## 2. ContratoMandato

**Tabla**: `CONTRATOS_MANDATOS` | **Entidad**: `src/dominio/entidades/contrato_mandato.py`

| Campo | Tipo | Regla en esta feature |
|---|---|---|
| `id_contrato_m` | INTEGER (PK) | Identidad; "mandato activo más reciente" = mayor `id_contrato_m` |
| `id_propiedad` | INTEGER (FK) | Comparte propiedad con el arrendamiento |
| `fecha_inicio_contrato_m` | TEXT ISO | Inicio del primer período; **no cambia** en renovación ni por sincronización del arriendo |
| `fecha_fin_contrato_m` | TEXT ISO | Se extiende en renovación y se sincroniza con la nueva fecha fin del arriendo |
| `duracion_contrato_m` | INTEGER (meses) | Periodicidad de la prórroga |
| `canon_mandato` | INTEGER | Sin IPC propio; se sincroniza con el canon del arriendo |
| `fecha_pago` | TEXT numérico | **10 / 20 / 30** según el tramo V2 de la fecha efectiva |
| `grupo_operativo` | INTEGER | **Tramo V2 (1/2/3) de la fecha efectiva**; nunca 0 en ACTIVO |
| `estado_contrato_m` | TEXT/Enum | Solo `ACTIVO` es renovable/auditable |

## 3. RenovacionContrato

**Tabla**: `RENOVACIONES_CONTRATOS` | **Entidad**: `src/dominio/entidades/renovacion_contrato.py`

| Campo | Tipo | Regla en esta feature |
|---|---|---|
| `id_renovacion` | INTEGER (PK) | Desempate del criterio "más reciente" |
| `id_contrato_m` / `id_contrato_a` | INTEGER (FK) | Exactamente uno según `tipo_contrato` |
| `tipo_contrato` | TEXT | `Mandato` / `Arrendamiento` |
| `fecha_inicio_original` | TEXT ISO | Inicio del período previo |
| `fecha_fin_original` | TEXT ISO | Fin del período previo |
| `fecha_inicio_renovacion` | TEXT ISO | **Fecha efectiva del nuevo período** = `fecha_fin_original + 1 día` (base del grupo/día de pago) |
| `fecha_fin_renovacion` | TEXT ISO | Fin del período renovado |
| `fecha_renovacion` | TEXT ISO | Fecha de ejecución; criterio primario de "más reciente" |
| `canon_anterior` / `canon_nuevo` | INTEGER | Encadenamiento entre renovaciones consecutivas |
| `porcentaje_incremento` | INTEGER (base 100) | 0 en mandato; IPC×100 en arriendo cuando aplica |

## 4. Resolución de la fecha efectiva (regla de cálculo)

```
fecha_efectiva(contrato):
  1. si el contrato tiene renovaciones:
       ultima = renovaciones WHERE contrato ORDER BY FECHA_RENOVACION DESC, ID_RENOVACION DESC LIMIT 1
       → ultima.fecha_inicio_renovacion
  2. si es mandato, no tiene renovaciones propias y su propiedad tiene arriendo ACTIVO con renovaciones:
       → fecha_inicio_renovacion de la última renovación de ese arriendo   # herencia FR-005 (R2)
  3. en otro caso:
       → fecha_inicio_contrato del contrato
```

## 5. Regla de grupo y día de pago (tramos V2)

| Tramo de día de la fecha efectiva | Grupo | Día de pago mandato | Día de pago arrendamiento |
|---|---|---|---|
| 28 al 7 (28,29,30,31,1..7) | 1 | 10 | día exacto (28..31 o 1..7) |
| 8 al 17 | 2 | 20 | día exacto (8..17) |
| 18 al 27 | 3 | 30 | día exacto (18..27) |

Sin huecos ni solapes; aplica igual a creación, edición, renovación y auditoría (FR-002/FR-003).

## 6. Reglas de validación (fail-fast)

| Regla | Aplicación |
|---|---|
| Renovación solo si `estado == ACTIVO` | `ContratoNoRenovableError` |
| Canon dentro de máximos operativos | `validar_canon` (feature 073), sin cambios |
| Derivados dentro de int4 | `validar_derivado` (feature 073), sin cambios |
| Grupo ∈ {1,2,3} y `fecha_pago` no vacío para ACTIVO | Auditoría detecta y remedia; renovación nunca persiste 0 |
| Contratos finalizados/cancelados | Excluidos de auditoría/remediación (inmutables) |

## 7. Entidad de reporte: Reporte de auditoría de grupos de pago

**Naturaleza**: artefacto operativo (no tabla nueva) — consola + CSV en `outputs/`.

| Campo | Descripción |
|---|---|
| `tipo` | `Mandato` / `Arrendamiento` |
| `id_contrato` | PK del contrato |
| `id_propiedad` | Propiedad asociada |
| `fecha_efectiva` | Fecha base usada según §4 |
| `grupo_actual` / `dia_pago_actual` | Valores almacenados (antes) |
| `grupo_esperado` / `dia_pago_esperado` | Valores según §5 |
| `discrepancia` | `true/false` |
| `accion` | `Sin cambio` / `Actualizado` / `Omitida (modificada durante la remediación)` (los dos últimos solo con `--commit`) |
| `fecha_reporte` | Timestamp de la corrida |

## 8. Relaciones y volumen

```text
PROPIEDADES 1 ── 0..1 CONTRATOS_ARRENDAMIENTOS (ACTIVO)
PROPIEDADES 1 ── 0..1 CONTRATOS_MANDATOS (ACTIVO)
CONTRATOS_ARRENDAMIENTOS 1 ── N RENOVACIONES_CONTRATOS (ID_CONTRATO_A)
CONTRATOS_MANDATOS       1 ── N RENOVACIONES_CONTRATOS (ID_CONTRATO_M)
CONTRATOS_MANDATOS 1 ── N LIQUIDACIONES / RECAUDOS (lectura del grupo)
```

Volumen estimado: cientos de contratos activos; la auditoría resuelve en una pasada SQL + cálculo en memoria (sin N+1).
