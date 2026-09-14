# Auditoría GEMINI CLI — Registro de Hitos de Ingeniería

> Documento de auditoría dinámica (Constitución §5). Registrar decisiones y validaciones por hito.

## 2026-09-14 - Feature 073-fix-renovacion-integer-range

### Causa raíz corregida

- **Overflow `integer × integer` en propagación**: `CAST(%s * comision_porcentaje / 10000.0 AS INTEGER)` evaluaba el producto en int4 antes de dividir; 2.300.000 × 1000 = 2,3e9 > 2.147.483.647 → `integer out of range` con rollback total (contrato 73 bloqueado). Fix: `%s::BIGINT` en las 2 expresiones (comisión e IVA), misma semántica de truncamiento.
- **Gate en dos niveles (FR-003)**: 1.º máximos operativos (canon ≤ $10M, comisión ≤ 1500, rechazo con mensaje campo+valor); 2.º límite int4 como red de seguridad para derivados. El crecimiento legítimo por IPC sobre el máximo operativo usa la red int4 (no se rechaza).
- **Excepción de dominio** `ValorFueraDeRangoError` (campo + valor, sin tecnicismos), mapeada en `ContratosState.execute_renewal`; mismo estándar aplicado a `renovar_mandato` (sin SQL propio que corregir).

### Evidencia de validación

- TDD: T005 (2,3M×1000) falló en RED con `NumericValueOutOfRange` en la línea exacta; en GREEN propaga 230.000 exacto + auditoría. T011 (10M×1500) verde.
- Suites: 59 unit + 12 integración + consecutiva/canon/propagación verdes; T022 falla idéntico al baseline (polución IPC preexistente, sin relación con el fix).
- ruff/mypy PASS en archivos tocados; quickstart Esc1 verificado (forma vieja falla, nueva retorna 230000).
- T010 (renovación real del contrato 73 en producción) queda para el operador: no existe staging y es una operación de negocio.

## 2026-09-13 — Feature 072-renovacion-contratos-debug

### Causas raíz corregidas

1. **Casting de fechas vacías** (regresión de 063): `""::date` rompía la propagación a `LIQUIDACIONES`/`RECAUDOS`. Fix: `NULLIF(campo,'')::date >= date_trunc('month', %s::date)` en las 6 queries (Q1–Q6).
2. **`fecha_inicio_renovacion` vacía**: se poblaba con `sumar_meses(fin, 1)` (matemática de meses incorrecta). Fix: helper de dominio `calcular_fecha_inicio_renovacion = fecha_fin_original + 1 día` (fuente única de verdad, CHK006).
3. **Bordes de fecha**: `sumar_meses` ahora aplica convención fin-de-mes→fin-de-mes (30-Nov+1→31-Dic; 2028-02-29+12→2029-02-28) con fallback de truncado.
4. **IPC condicional**: incremento solo si `duracion >= 12` y existe IPC vigente (`obtener_ultimo()`, mayor ANIO); si no, 0%.
5. **`ValueError` genérico**: sustituido por `ContratoNoRenovableError` (dominio, §2.2) en renovación de arrendamiento y mandato.

### Decisiones de diseño auditadas

- **Atomicidad**: renovación en transacción única (`db.transaccion()`); fallo → rollback total. Verificado con fallo inducido (T022): 0 estado parcial, reintento con misma `idempotency_key` completa sin duplicados.
- **Idempotencia DB-backed** (FR-011): `@idempotent` en `renovar_arrendamiento` y `renovar_mandato`, respaldado en `IDEMPOTENCY_KEYS` (lock atómico, TTL 24h, polling). Fix de `bloquear`: re-adquisición de keys en estado `failed` (`ON CONFLICT DO UPDATE ... WHERE ESTADO='failed'`) — sin este fix el reintento tras fallo hacía polling hasta timeout.
- **Concurrencia** (CHK032): validado con `ThreadPoolExecutor` — doble renovación misma key (1 fila, sin deadlock) y renovación + escritor concurrente sobre `RECAUDOS` (bloqueo de fila esperado, sin `40P01`).
- **Auditoría de propagación** (FR-002): `AUDITORIA_PROPAGACION_CANON` registra SOLO filas con cambio real de canon; con 0% o 0 filas futuras → 0 registros.
- **Caché no bloqueante** (FR-012): invalidación de `cache_estado_cartera` post-commit envuelta en try/except con log; nunca aborta la transacción.
- **Multi-mandato** (FR-009): `obtener_activo_por_propiedad` → `ORDER BY ID_CONTRATO_M DESC LIMIT 1`; sin mandato activo la renovación continúa sin error.

### Bugs extra detectados por los gates (Fase 5) y corregidos

- `renovar_arrendamiento` sin `**kwargs` → TypeError al inyectar `_idempotency_full_key`.
- `logger` undefined en `_invalidar_cache_estado_cartera` (ruff F821, NameError latente).
- Asignación invertida en `renovar_mandato` paso 5 (corrompía `canon_mandato`; restaurada a `propiedad.canon_arrendamiento_estimado = mandato.canon_mandato`, FR-010). Detectada por mypy (0 errores nuevos vs baseline HEAD tras el fix).
- Test preexistente `test_cascada_renovacion_canon` usaba columna inexistente `cm.propiedad_id` → `cm.id_propiedad`.

### Evidencia de validación

- 47 tests de renovación (unit + integración) verdes; E1–E12 del quickstart cubiertos.
- SC-003: 61 passed, 0 failed (suite quickstart contra PostgreSQL Railway).
- Gates: compileall PASS · mypy baseline-diff 0 nuevos · ruff PASS archivos feature · `reflex export --frontend-only --no-zip` PASS (exit 0).
- Desviaciones documentadas en `specs/072-renovacion-contratos-debug/tasks.md` (T026): black repo-wide (74 archivos preexistentes) y cobertura de paquetes legacy (dominio 64.86% / aplicación 30.78%).
