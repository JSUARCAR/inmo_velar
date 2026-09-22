# Contrato: Servicios de renovación y persistencia

**Componentes**: `ServicioContratoArrendamiento`, `ServicioContratoMandato`, `RepositorioRenovacionPostgres`, `RepositorioContratoArrendamientoPostgres`
**Tipo**: interfaces internas de aplicación e infraestructura

## 1. `ServicioContratoArrendamiento.renovar_arrendamiento(id_contrato, usuario_sistema, nueva_fecha_fin=None)`

**Precondiciones**
- Contrato existe y `estado_contrato_a == ACTIVO` (si no → `ContratoNoRenovableError`).
- Canon dentro de máximos operativos (`validar_canon`).

**Postcondiciones (misma transacción)**
1. Historia en `RENOVACIONES_CONTRATOS` con `fecha_inicio_renovacion = fecha_fin_original + 1 día`.
2. `fecha_fin_contrato_a` = fecha calculada o personalizada; `canon_arrendamiento` actualizado por IPC si aplica.
3. `fecha_renovacion_contrato_a` = fecha de ejecución.
4. `grupo_operativo` = `calcular_grupo_operativo(fecha_inicio_renovacion)`.
5. `fecha_pago` = `calcular_dia_pago_arrendamiento(fecha_inicio_renovacion)`.
6. Propiedad: `canon_arrendamiento_estimado` sincronizado.
7. Mandato activo más reciente de la propiedad (si existe): `fecha_fin_contrato_m` sincronizada; `grupo_operativo` y `fecha_pago` recalculados con la regla de mandato sobre la **misma fecha efectiva** adoptada (FR-005).
8. Liquidaciones y recaudos futuros propagados (sin cambios en su lógica).
9. Commit único al salir del bloque; cualquier excepción → rollback total (FR-008).
10. Invalidación de caché `cache_estado_cartera` **después** del commit; su fallo no revierte (FR-012).

## 2. `ServicioContratoMandato.renovar_mandato(id_contrato, usuario_sistema, nueva_fecha_fin=None)`

**Precondiciones**: contrato existe y `estado_contrato_m == ACTIVO`; canon validado.

**Postcondiciones (misma transacción)**
1. Historia en `RENOVACIONES_CONTRATOS` (`fecha_inicio_renovacion = fecha_fin_original + 1 día`).
2. `fecha_fin_contrato_m` extendida; `fecha_renovacion_contrato_m` = fecha de ejecución.
3. `grupo_operativo` = tramo V2 de `fecha_inicio_renovacion`; `fecha_pago` = 10/20/30.
4. Propiedad: `canon_arrendamiento_estimado` sincronizado (sin cambios).
5. Commit único / rollback total; idempotencia `@idempotent` (TTL 24 h) conservada.
6. Invalidación de caché post-commit tolerante.

**Cambio estructural**: se introduce `_ejecutar_renovacion_mandato` y `renovar_mandato` abre `db.transaccion()` (R3).

## 3. Consulta determinista de la última renovación (extracción masiva)

- No se expone método por contrato en repositorios (R7). El script resuelve el historial en **una consulta SQL única**:
  - Mandatos: subconsulta `RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_M = cm.ID_CONTRATO_M ORDER BY FECHA_RENOVACION DESC, ID_RENOVACION DESC LIMIT 1`.
  - Arriendos: idem con `ID_CONTRATO_A`.
  - Fechas TEXT comparadas con `NULLIF(campo,'')::date` cuando aplique.
- Resultado por contrato: `fecha_inicio_renovacion` de la renovación más reciente o `NULL`; el script aplica el fallback de fecha efectiva (data-model §4), incluida la **herencia del período del arrendamiento activo renovado para mandatos sin renovaciones propias** (R2, Spec §FR-001).

## 4. `RepositorioContratoArrendamientoPostgres._row_to_entity`

- **Debe** materializar `grupo_operativo` desde `GRUPO_OPERATIVO` (0 si nulo/ausente).
- Invariante: `obtener_por_id` → `actualizar` no altera el grupo almacenado salvo que el servicio lo recalcule explícitamente (FR-007).

## 5. Contrato de errores (UI)

| Situación | Excepción | Resultado visible |
|---|---|---|
| Contrato inexistente o no ACTIVO | `ContratoNoRenovableError` | Mensaje de dominio en `error_message` |
| Canon/derivado fuera de rango | `ValorFueraDeRangoError` | Mensaje operativo (campo + valor, sin tecnicismos) |
| Fallo en cualquier paso transaccional | Excepción original propagada tras rollback | "No se aplicó ningún cambio; es seguro reintentar" alineado en `execute_renewal` |
| Reintento dentro de TTL 24 h | — | Devuelve el resultado existente sin duplicar |

## 6. Contrato: script de auditoría/remediación

Ver [cli-remediacion.md](./cli-remediacion.md).
