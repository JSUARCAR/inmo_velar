# Quickstart: Validación de Elegibilidad Conjunta (Arrendamiento Activo)

**Date**: 2026-09-22
**Feature**: 076-liquidacion-requiere-arrendamiento

## Prerrequisitos

- Entorno de pruebas con datos de producción o copia controlada (se registrarán los IDs TEST en `bitacora_test.json`).
- Al menos una propiedad cubriendo cada una de las 5 combinaciones de la matriz, o capacidad de crearlas (crear/ajustar contratos mandato/arrendamiento + estados).
- Aplicación corriendo en modo debug: `reflex run --env dev`.
- Pytest instalado y entorno activo.

## Escenarios de Validación (obligatorios)

### Matriz 5 combinaciones × 2 rutas (SC-002, 10/10)

Setup de la matriz:

| # | ESTADO_CONTRATO_M | ESTADO_CONTRATO_A (misma ID_PROPIEDAD) | Esperado |
|---|-------------------|----------------------------------------|----------|
| 1 | ACTIVO | ACTIVO | genera |
| 2 | ACTIVO | No existe | no genera (no elegible) |
| 3 | ACTIVO | Inactivo/Finalizado | no genera (no elegible) |
| 4 | No activo | ACTIVO | no genera (no elegible) |
| 5 | No activo | No/inactivo | no genera (no elegible) |

**Ruta A — Generación individual** (para c/u de las 5 combinaciones):
1. Abrir Liquidaciones → "Nueva Liquidación".
2. En el combobox de propiedad buscar la propiedad del caso.
3. **Esperado**: solo la combinación 1 aparece en el combobox (FR-005); combinaciones 2–5 no se ofrecen.
4. Para la combinación 1: seleccionarla, elegir período `YYYY-MM` sin liquidación previa y guardar → liquidación creada.
5. Para combinaciones 2–5: intentar generación directa (si procede por API/evento) y verificar que NO se crea ninguna fila en `LIQUIDACIONES`.

**Ruta B — Generación masiva** (mismo período en cada caso):
1. Liquidaciones → "Generar Masiva" → período.
2. **Esperado**: se genera liquidación SOLO para combinación 1 (FR-006); el sumario/toast refleja `generadas / ya existían / no elegibles / con error` con exactitud; combinaciones 2–5 aparecen en `no elegibles` (con motivo en lenguaje de negocio, FR-010), y el proceso **no aborta**.
3. Verificar en BD (`SELECT ... FROM LIQUIDACIONES l JOIN CONTRATOS_MANDATOS cm ...`) que los `ID_CONTRATO_M` con liquidación pertenecen únicamente a propiedades con arrendamiento ACTIVO de la misma ID.

**Consistencia** (SC-003): con el mismo período y datos, comparar el conjunto de propiedades elegibles de la ruta individual vs. masiva → idéntico.

### Auditoría de solo lectura (FR-007, SC-004)

1. Ejecutar el reporte (vía UI o `ServicioAuditoriaElegibilidad`) para el rango histórico.
2. Esperado:
   - `liquidaciones_auditadas` = 100% de las liquidaciones del período/filtro.
   - `no_elegibles` lista cada liquidación cuya propiedad no cumplía combinación completa **en su `FECHA_GENERACION`**, con `periodo`, propiedad, propietario y `motivo`.
   - Liquidaciones realmente elegibles NO aparecen como afectadas.
3. Verificar que ninguna fila fue modificada/eliminada: comparar `COUNT(*)` y `SUM(NETO_A_PAGAR)` de `LIQUIDACIONES` antes vs. después de la ejecución (idénticos).
4. Re-ejecución: con los mismos `criterios` registrados (fecha de reconstrucción, filtro, período) el reporte es idéntico (Q7).

### Limpieza de datos TEST (FR-008, SC-005)

1. Durante la validación, registrar cada ID creado/ajustado en `bitacora_test.json`.
2. `python src/scripts/limpiar_datos_test_bitacora_pg.py --dry-run` → muestra que se borran SOLO los IDs de la bitácora.
3. `python src/scripts/limpiar_datos_test_bitacora_pg.py --ejecutar` → elimina en orden FK, transacción única.
4. Verificación:
   - `SELECT` por ID: 0 registros TEST en todas las entidades de la bitácora y 0 huérfanas derivadas (Q3).
   - Datos reales intactos (SC-005).
5. Idempotencia: re-ejecutar `--ejecutar` → sale OK sin efectos (los IDs ya no existen y el script los ignora, Q6).
6. Fallo a mitad: (opcional) interrumpir forzadamente → nada eliminado (rollback) y re-ejecución segura, Q6.

### Mensajes de exclusión (FR-010, SC-006)

- En individual y masiva, cada exclusión comunica la causa en lenguaje de negocio, p. ej. "sin contrato de arrendamiento activo en esta propiedad". Sin asistencia técnica.

## Verificación automatizada

```bash
# Aplicacion: elegibilidad en servicios (matriz 5x2 individual + masiva)
pytest tests/aplicacion/test_servicio_financiero_elegibilidad.py -q

# E2E UI (individual + masiva + auditoría si aplica)
pytest tests/e2e/test_liquidaciones.py tests/e2e/test_liquidaciones_playwright.py -q
```

## Criterios de Aceptación

- [ ] 10/10 verificaciones de la matriz (5 combinaciones × 2 rutas).
- [ ] Recombinación individual/masiva produce el mismo conjunto elegible (0 discrepancias).
- [ ] 0 liquidaciones generadas en combinaciones 2–5 (SC-001).
- [ ] Auditoría: 100% cubierta, solo marca históricas no elegibles por su fecha de generación, 0 modificaciones (SC-004), re-generable con criterios registrados.
- [ ] Limpieza: 0 registros TEST y 0 huérfanas; datos reales intactos; re-ejecución idempotente (SC-005).
- [ ] Causa de exclusión identificable sin asistencia técnica (SC-006).