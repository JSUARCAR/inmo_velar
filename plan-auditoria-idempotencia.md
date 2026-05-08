# Plan Maestro de Auditoría y Remediación — Idempotencia

> **Versión:** 1.0  
> **Fecha:** 2026-05-07  
> **Propietario:** Arquitectura / Senior Full-Stack  
> **Stack:** Python + Reflex + PostgreSQL Nativo

---

## 1. Dashboard de Estado (Implementado vs. Pendiente)

| # | Componente | Archivo(s) | Estado | Prioridad | Esfuerzo |
|---|---|---|---|---|---|
| 1.1 | `IRepositorioIdempotencia` | `src/dominio/interfaces/repositorio_idempotencia.py` | ✅ Completo | — | — |
| 1.2 | `RepositorioIdempotenciaPostgres` | `src/infraestructura/persistencia/repositorio_idempotencia_postgres.py` | ✅ Completo | — | — |
| 1.3 | Migración SQL base | `migraciones/sql/20260506_idempotencia_base.sql` | ✅ Completo | — | — |
| 1.4 | Migración fix key length | `migraciones/sql/20260506_fix_idempotency_key_length.sql` | ✅ Completo | — | — |
| 1.5 | `@idempotent` decorator | `src/aplicacion/decorators/idempotent.py` + `estrategia_idempotencia.py` | ✅ Lock atómico + backoff exp. + Strategy extraída | 🔴 Alta | 2d |
| 1.6 | `IdempotencyStateMixin` | `src/presentacion_reflex/state/idempotency_mixin.py` | ✅ Conectado en UI + botón deshab. por `is_processing_idempotent` | 🟡 Media | 1d |
| 1.7 | `ServicioRecaudo.registrar_pago` protegido | `src/aplicacion/servicios/servicio_recaudo.py` | ✅ Completo + fix double-key (full_key inyectada) | — | — |
| 1.8 | Tests de integración | `tests/integration/test_idempotencia_*.py` | ⚠️ Parcial (< 20 tests, frágiles) | 🟡 Media | 2d |
| 1.9 | Scripts de diagnóstico | `scripts/diagnostico/test_*_idempotencia.py` (3 scripts) | ⚠️ Duplicados, frágiles | 🟢 Baja | 1d |
| 1.10 | **5 servicios con `@idempotent`** | LiquidaciónAsesores, PagosAdmin, SaldosFavor, Contratos, ContratoArrendamiento | ✅ 5 protegidos (Cumplimiento es read-only) | 🔴 Alta | 3d |
| 1.11 | **Middleware API** (`Idempotency-Key` header) | `src/presentacion_reflex/api/idempotency_middleware.py` | ✅ Middleware FastAPI registrado en `app._api` | 🟡 Media | 1d |
| 1.12 | **`IdempotentButton`** / doble-click protection UI | `modal_form.py:347-348` | ✅ Botón deshab. por `is_processing_idempotent` | 🟢 Baja | 1d |
| 1.13 | **`DatabaseIdempotencyStrategy`** | `src/aplicacion/decorators/estrategia_idempotencia.py` | ✅ Clase extraída, decorador delgado | 🟢 Baja | 1d |
| 1.14 | **Factory unificada** | `src/infraestructura/factory/factory_idempotencia.py` | ✅ `crear_repo_idempotencia()` centralizada | 🟢 Baja | 0.5d |
| 1.15 | **Event Sourcing** en servicios adicionales | Solo en ServicioRecaudo | ❌ Pendiente | 🟢 Baja | 2d |

**Progreso general:** ~85% • **Restante:** ~15% (F4: Tests) • **Esfuerzo total estimado restante:** ~4 días hábiles

---

## 2. Fase 0 — Correcciones Críticas (Semana 1 • Días 1-3)

### Tarea 0.1: Eliminar TOCTOU + Spin-Wait en el Decorador
**Archivo:** `src/aplicacion/decorators/idempotent.py`

**Problema:** CHECK-then-INSERT clásico (líneas 51-58) + spin-lock de 15-20 iteraciones con `time.sleep(0.5)` (hasta 10s bloqueante).

**Solución:** Reemplazar con lock atómico vía PostgreSQL:
```python
INSERT INTO IDEMPOTENCY_KEYS (KEY, OPERACION, PARAMETROS, RESULTADO, USUARIO_ID, FECHA_EXPIRA, ESTADO)
VALUES (%s, %s, %s, %s, %s, %s, 'processing')
ON CONFLICT (KEY) DO NOTHING
RETURNING ID_KEY
```
- Si `RETURNING` devuelve fila → este hilo **ganó** el lock → ejecuta lógica
- Si `RETURNING` devuelve 0 filas → otro hilo ganó → `SELECT ... FOR UPDATE NOWAIT` o reintentar con `RETURNING RESULTADO` cada 100ms (máx 30 reintentos = 3s, backoff exponencial)

**Criterio de aceptación:** Prueba concurrente con 50 hilos: exactamente 1 ejecuta lógica, 49 reciben caché, 0 errores, 0 spin-wait activo (sin bucles sleep).

---

### Tarea 0.2: Transacción Atómica Cross-Flow
**Archivo:** `src/aplicacion/decorators/idempotent.py`

**Problema:** 3 operaciones separadas sin transacción única (`INSERT processing` → auto-commit, `func()` → ejecuta, `UPDATE resultado` → auto-commit). Si el proceso crashea entre el `INSERT` y el `UPDATE`, queda registro stuck con `status=processing`.

**Solución:**
- 1. `INSERT ... ON CONFLICT DO NOTHING RETURNING ID_KEY` (auto-commit rápido para el lock)
- 2. Si ganó → `BEGIN` transacción, ejecuta lógica de negocio, `UPDATE ... SET ESTADO='completed', RESULTADO=%s`, `COMMIT`
- 3. Si `COMMIT` falla → `ROLLBACK` automático
- 4. Si perdió → espera con `SELECT ... FOR UPDATE NOWAIT` y backoff exponencial (max 2s total)

**Criterio:** `kill -9` simulado durante ejecución → no quedan registros stuck en `processing` (el INSERT que sobrevive se limpia por TTL, pero el ideal es 0 stuck).

---

### Tarea 0.3: Fix `FECHA_CREACION` en UPSERT
**Archivo:** `src/infraestructura/persistencia/repositorio_idempotencia_postgres.py`

**Cambio:**
```sql
-- ANTES (mal): sobreescribe la fecha original
ON CONFLICT (KEY) DO UPDATE SET
    FECHA_CREACION = NOW(),

-- DESPUÉS (bien): preserva el timestamp original (se queda con su DEFAULT de creación)
-- Simplemente eliminar FECHA_CREACION del SET
ON CONFLICT (KEY) DO UPDATE SET
    OPERACION = EXCLUDED.OPERACION,
    RESULTADO = EXCLUDED.RESULTADO,
    FECHA_EXPIRA = EXCLUDED.FECHA_EXPIRA,
    INTENTOS = IDEMPOTENCY_KEYS.INTENTOS + 1;
```

---

## 3. Fase 1 — Refactorización Controlada (Semana 1 • Días 3-5)

### Tarea 1.1: Extraer `DatabaseIdempotencyStrategy`
**Archivo nuevo:** `src/aplicacion/decorators/estrategia_idempotencia.py`
**Refactor:** `src/aplicacion/decorators/idempotent.py`

Extraer la lógica de:
- Lock atómico (INSERT ON CONFLICT RETURNING)
- Resolución de usuario_id
- Serialización determinista
- Manejo de processing/completed

a una clase `DatabaseIdempotencyStrategy` inyectable. El decorador solo orquesta (SRP).

**Beneficio:** Testeable unitariamente con mock, intercambiable.

---

### Tarea 1.2: Conectar `IdempotencyStateMixin` en UI
**Archivos:** 
- `src/presentacion_reflex/state/recaudos_state.py`
- `src/presentacion_reflex/state/idempotency_mixin.py`

**Cambios:**
- `save_recaudo()` debe llamar `self.generate_idempotency_key("recaudo:registrar", form_data)` y pasar el `idempotency_key` al servicio
- `save_recaudo()` debe llamar `start_idempotent_request(key)` / `end_idempotent_request()`
- El template/componente debe leer `self.is_processing_idempotent` para deshabilitar el botón de guardar durante el request

---

### Tarea 1.3: Fix Double Prefix Key
**Archivo:** `src/aplicacion/servicios/servicio_recaudo.py:109`

**Problema:** El servicio reconstruye la key manualmente con `f"recaudo:registrar:{idempotency_key}"`, pero el decorador ya hace el prefijo. Cuando el usuario pasa `idempotency_key="abc"`, el decorador produce `full_key="recaudo:registrar:abc"`. El servicio produce la misma key (coincidencia). Pero si el usuario pasa `idempotency_key="recaudo:registrar:abc"`, el decorador produce `"recaudo:registrar:recaudo:registrar:abc"` (doble prefijo).

**Solución:** Mover el `registrar_evento()` al decorador (que tiene la `full_key` correcta), no al servicio. Alternativamente, pasar `full_key` como kwarg oculto `_idempotency_full_key` desde el decorador.

---

## 4. Fase 2 — Ampliación a 7 Servicios (Semana 2 • Días 6-9)

### Tarea 2.1: Catálogo de Servicios Críticos

| Servicio | Método(s) a proteger | Riesgo si duplicado |
|---|---|---|
| `ServicioLiquidacionAsesores` | `liquidar_comisiones()` | Doble pago a asesor |
| `ServicioPagosAdministracion` | `registrar_pago_administracion()` | Doble egreso contable |
| `ServicioCumplimiento` | `registrar_garantia()` | Doble registro de garantía |
| `ServicioSaldosFavor` | `aplicar_abono()`, `crear_saldo()` | Duplicidad financiera |
| `ServicioContratos` | `crear_contrato()`, `renovar()` | Contrato duplicado |
| `ServicioContratoArrendamiento` | `firmar()`, `terminar()` | Estados inconsistentes |

**Checklist por servicio:**
- [ ] Inyectar `repo_idempotencia` en constructor (o usar factory)
- [ ] Agregar `@idempotent(key_prefix="servicio:metodo")` en método(s) crítico(s)
- [ ] Pasar test de concurrencia (10 hilos → 1 ejecución real, 9 hits de caché)
- [ ] (Opcional) Registrar evento de auditoría en `EVENTOS_IDEMPOTENCIA`

---

### Tarea 2.2: Factory Unificada de Repositorio
**Archivo:** `src/infraestructura/factory/factory_idempotencia.py` (nuevo)

Centralizar la creación para evitar `RepositorioIdempotenciaPostgres()` disperso:

```python
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.infraestructura.persistencia.repositorio_idempotencia_postgres import RepositorioIdempotenciaPostgres

def crear_repo_idempotencia() -> IRepositorioIdempotencia:
    return RepositorioIdempotenciaPostgres()
```

Y usarlo en `_crear_servicio()` de `recaudos_state.py` y en las factories de los otros servicios.

---

## 5. Fase 3 — Middleware API (Semana 2 • Días 10-11)

### Tarea 3.1: Investigar Viabilidad de Middleware Reflex
**Acción:** Verificar si Reflex soporta interceptar headers HTTP en eventos `rx.event(background=True)`.

**Ruta alternativa:** Si Reflex no lo soporta nativamente, implementar un endpoint FastAPI independiente que reciba requests con header `Idempotency-Key`, valide contra la BD, y retorne `200 OK` (resultado cacheado), `409 Conflict` (en processing), o `404/转发` (delegar a Reflex).

**Archivos:**
- `src/presentacion_reflex/api/idempotency_proxy.py` (nuevo, opcional)
- O documentar limitación si no es viable.

---

### Tarea 3.2: Implementar Validación de Idempotency-Key en API
Si es viable (Tarea 3.1):
- Middleware captura header y lo inyecta como kwarg en el evento Reflex
- Si la key ya existe con resultado → responder inmediatamente (sin ejecutar el evento)
- Si está en `processing` → `429 Too Many Requests` o `409 Conflict` con `Retry-After`

---

## 6. Fase 4 — Calidad y Tests (Semana 3 • Días 12-14)

### Tarea 4.1: Refactorizar Tests → Fixtures Autocontenidos
**Archivos:** 
- `tests/integration/test_idempotencia_elite.py`
- `tests/integration/test_idempotencia_concurrente.py`

**Principios:**
- Cada test crea sus propios datos (contrato, usuario, comando) en fixtures
- Usa `ROLLBACK` al finalizar (o truncado limpio de tablas)
- No depende de existencia de datos reales en BD
- `pytest.fixture` con `scope="function"` para aislamiento total

---

### Tarea 4.2: Tests de Concurrencia Parametrizados
**Archivo:** `tests/integration/test_idempotencia_concurrente.py`

**Escenarios obligatorios:**
- 10 hilos, misma key → 1 real, 9 cache hits
- 50 hilos, misma key → 1 real, 49 cache hits
- 10 hilos, diferentes keys → 10 reales, 0 cache hits
- Key expirada → ejecuta lógica de nuevo (fresh insert)
- Key en estado `processing` + timeout → `RuntimeError` manejado gracefulmente

**Métrica:** 100% de los tests deben pasar en 3 ejecuciones consecutivas.

---

### Tarea 4.3: Script Único de Stress Test
**Archivo:** `scripts/diagnostico/stress_idempotencia.py` (reemplazar los 3 scripts existentes: `test_concurrencia_idempotencia.py`, `test_idempotencia_fija.py`, `test_final_idempotencia.py`)

Script parametrizable:
```bash
python scripts/diagnostico/stress_idempotencia.py --workers 100 --mode fixed
python scripts/diagnostico/stress_idempotencia.py --workers 50 --mode random
python scripts/diagnostico/stress_idempotencia.py --workers 10 --mode sequential
```

**Salida:** Reporte JSON con:
- Duración total
- Requests exitosos / fallidos
- Call count real (debe ser 1 en modo `fixed` y `workers` en modo `random`)
- IDs únicos generados

---

### Tarea 4.4: Cleanup de Scripts Legacy
**Eliminar:** 
- `scripts/diagnostico/test_concurrencia_idempotencia.py`
- `scripts/diagnostico/test_idempotencia_fija.py`
- `scripts/diagnostico/test_final_idempotencia.py`
- `scripts/diagnostico/check_idempotency.py`
- `scripts/diagnostico/cleanup_idempotency.py`

Migrar funcionalidad útil al nuevo `stress_idempotencia.py`.

---

## 7. Cronograma

| Semana | Días | Fase | Descripción | Entregables |
|---|---|---|---|---|
| **1** | 1-3 | **F0** | Correcciones críticas | Decorador sin TOCTOU + transacción atómica + fix FECHA_CREACION |
| **1** | 3-5 | **F1** | Refactorización controlada | Strategy extraída + Mixin conectado + double-key fix |
| **2** | 6-9 | **F2** | Ampliación a 7 servicios | 6 servicios adicionales protegidos + factory unificada |
| **2** | 10-11 | **F3** | Middleware API | Middleware Idempotency-Key o alternativa documentada |
| **3** | 12-14 | **F4** | Calidad y tests | Tests autocontenidos + tests parametrizados + stress test único |
| **3** | 15 | — | Buffer / documentación | Plan actualizado, AGENTS.md, cleanup scripts legacy |

**Total estimado:** 15 días hábiles • **Riesgo general:** Medio

---

## 8. Riesgos y Mitigaciones

| ID | Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | TOCTOU reintroducido en refactor del decorador | Media | Alto | Code review obligatorio + test de 100 hilos concurrentes como gate |
| R2 | Decorador incompatible con SQLite en dev local | Alta | Medio | Tests unitarios del strategy con mock DB; tests de integración solo en PG |
| R3 | Reflex no soporta middleware de headers HTTP | Alta | Alto | Validar en docs de Reflex antes de implementar F3; tener plan B (FastAPI) |
| R4 | Servicios legacy sin constructor con inyección de dependencias | Media | Medio | Refactor gradual con wrapper/adaptador; no romper APIs existentes |
| R5 | DB pool insuficiente para 100 hilos concurrentes | Baja | Alto | Verificar `maxconn=50-100` en `ThreadedConnectionPool`; probar con métricas |
| R6 | Dependencia de datos reales en tests → CI bloqueada | Alta | Medio | Tarea 4.1 desbloquea CI: tests autocontenidos sin depender de BD real |

---

## 9. Métricas de Éxito

| Métrica | Objetivo | Cómo se mide |
|---|---|---|
| Duplicados financieros | 0 | Constraints `UNIQUE` en PostgreSQL + tests de concurrencia |
| Overhead de latencia | < 15ms por request | `timeit` en decorador (fase 0 vs actual) |
| Cobertura de servicios críticos | 7/7 protegidos | `grep @idempotent src/aplicacion/servicios/ | wc -l` |
| Tests de concurrencia | 100% passing x3 runs | `pytest tests/integration/test_idempotencia_*.py -x --count=3` |
| Tiempo de resolución de conflictos | < 3s (antes 10s) | Benchmark con 100 hilos concurrentes |
| Tests autocontenidos | Sin dependencia de BD real | Revisión de fixtures (no SELECT * FROM tablas reales) |
| Scripts legacy eliminados | 0 legacy scripts | `ls scripts/diagnostico/test_*.py` (solo `stress_idempotencia.py`) |

---

## 10. Comandos de Referencia

```bash
# Contar servicios protegidos
grep -rn "@idempotent" src/aplicacion/servicios/ | wc -l

# Ejecutar tests de idempotencia
pytest tests/integration/test_idempotencia_*.py -v --tb=short

# Limpiar tabla IDEMPOTENCY_KEYS (dev)
python scripts/diagnostico/stress_idempotencia.py --clean

# Stress test
python scripts/diagnostico/stress_idempotencia.py --workers 100 --mode fixed --report json

# Verificar registros stuck en processing
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM IDEMPOTENCY_KEYS WHERE ESTADO = 'processing' AND FECHA_EXPIRA > NOW();"
```
