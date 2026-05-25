# PLAN MAESTRO DE REMEDIACIÓN TÉCNICA

## Sincronización Contratos de Arrendamiento ↔ Estados de Propiedades

| Campo | Valor |
|-------|-------|
| **Cliente** | Inmobiliaria Velar |
| **Sistema** | Reflex + PostgreSQL (Railway) |
| **Versión** | 1.0 |
| **Clasificación** | Crítica / Producción |
| **Fecha** | 2026-05-25 |

---

- [x] Fase 0 — Auditoría y Línea Base
- [x] Fase 1 — Corrección Crítica
- [x] Fase 2 — Sincronización y Transaccionalidad
- [x] Fase 3 — Eliminación de Triggers y Refactor DB
- [x] Fase 4 — Normalización de Estados
- [x] Fase 5 — Refactor de Validaciones UI → Service
- [x] Fase 6 — Data Remediation
- [x] Fase 7 — Testing y QA

---

## 1. RESUMEN EJECUTIVO

Se identificaron **8 defectos críticos** en el subsistema de sincronización entre `CONTRATOS_ARRENDAMIENTOS` y `PROPIEDADES`. La arquitectura actual presenta **doble fuente de escritura** (app layer + triggers SQL), **dependencia implícita en triggers de BD** para la liberación de propiedades durante desocupaciones, y **omisión total de sincronización** en el flujo de actualización de contratos.

El riesgo operativo inmediato es la **corrupción silenciosa del estado de ocupación**: propiedades que permanecen `OCUPADA` tras la finalización de contratos, y propiedades `DISPONIBLE` con contratos activos. Esto impacta KPIs, dashboards, disponibilidad comercial, liquidaciones y recaudos.

La estrategia propuesta centraliza toda la lógica de sincronización en la capa de aplicación, elimina triggers de negocio en PostgreSQL (manteniendo solo auditoría), normaliza estados mediante enums fuertemente tipados, y establece un `Single Source of Truth` con validación transaccional atómica.

---

## 2. DIAGNÓSTICO TÉCNICO VALIDADO

### 2.1 Mapa de Arquitectura Actual

```
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND REFLEX                                                     │
│  contratos_state.py          propiedades_state.py                   │
│  ├─ save_contrato()          ├─ save_propiedad()                   │
│  ├─ toggle_estado()          ├─ toggle_disponibilidad()            │
│  └─ execute_renewal()        └─ toggle_activa()                    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│ SERVICIOS APLICACIÓN                                                │
│                                                                     │
│  servicio_contrato_arrendamiento.py                                 │
│  ├─ crear_arrendamiento()       → propiedad OCUPADA  ✅ (app)      │
│  ├─ _ejecutar_actualizacion()   → NO sincroniza      ❌            │
│  ├─ terminar_arrendamiento()    → solo Cancelado      ⚠️            │
│  └─ renovar_arrendamiento()     → NO toca propiedad   ❌            │
│                                                                     │
│  servicio_desocupaciones.py                                        │
│  └─ finalizar_desocupacion()    → confía en trigger   ❌❌❌        │
│                                                                     │
│  servicio_propiedades.py                                           │
│  └─ actualizar_propiedad()      → sincroniza canon    ✅           │
│                                                                     │
│  servicio_contrato_mandato.py                                      │
│  └─ terminar_mandato()          → NO toca propiedad   ❌           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│ REPOSITORIOS POSTGRES                                               │
│  repositorio_contrato_arrendamiento_postgres.py                     │
│  repositorio_propiedad_postgres.py                                  │
│  → No contienen lógica de sincronización (solo CRUD puro)          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│ POSTGRESQL (Railway)                                                │
│                                                                     │
│  TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA  → INSERT → OCUPADA  ⚠️     │
│  TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE    → UPDATE → DISPONIBLE ⚠️   │
│  trg_sync_fechas_mandato                → DROPPED          🟢      │
│  trg_sync_canon_arrendamiento           → DROPPED          🟢      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Defectos Identificados

| ID | Defecto | Archivo | Línea | Severidad | Scope |
|----|---------|---------|-------|-----------|-------|
| C‑01 | Desocupación no libera propiedad desde app layer | `servicio_desocupaciones.py` | 271-283 | **CRÍTICA** | La propiedad queda OCUPADA si el trigger no existe/falla |
| C‑02 | `actualizar_arrendamiento` ignora transición de estado → disponibilidad | `servicio_contrato_arrendamiento.py` | 149-266 | **CRÍTICA** | Cambiar estado no actualiza propiedad |
| C‑03 | `terminar_arrendamiento` solo maneja `Cancelado`, omite `Finalizado` | `servicio_contrato_arrendamiento.py` | 435-453 | **ALTA** | Estados terminales huérfanos |
| C‑04 | Sincronización duplicada app + trigger para creación | `servicio_contrato_arrendamiento.py:117-121` + trigger | ambos | **MEDIA** | Race condition potencial |
| C‑05 | Estados denormalizados: string `"Activo"` vs `EstadoContrato.ACTIVO` | `contrato_arrendamiento.py:40` / `estados_contrato.py:22` | — | **MEDIA** | Inconsistencias, bugs de comparación |
| C‑06 | Validación de negocio en State/UI (no en Service) | `propiedades_state.py:695-706, 743-753` | — | **ALTA** | Bypass via API directa |
| C‑07 | Dependencia heredada de SQLite: `repositorio_propiedad_sqlite` | `servicio_desocupaciones.py:35` | 35 | **ALTA** | Incompatibilidad Railway |
| C‑08 | Cache invalidation incompleta: propiedades no se invalidan al terminar contrato | `servicio_contrato_arrendamiento.py:435` | — | **MEDIA** | Stale data en UI |
| C‑09 | `terminar_mandato` no sincroniza disponibilidad de propiedad | `servicio_contrato_mandato.py:303-321` | — | **MEDIA** | Mandato no debería tocar disponibilidad (diseño), pero debe validarse |
| C‑10 | Sin constraint CHECK en `DISPONIBILIDAD_PROPIEDAD` | `PROPIEDADES` (BD) | — | **BAJA** | Valores fuera de rango |

### 2.3 Mapa de Flujos de Transición de Estado

```
ESTADOS ACTUALES (entidad ContratoArrendamiento):
  "Activo" → "Finalizado" | "Cancelado"

FLUJOS:

  CREACIÓN:
    Crear Contrato → estado="Activo" → propiedad=OCUPADA (app + trigger)  ⚠️ duplicado

  ACTUALIZACIÓN (genérica):
    Actualizar Contrato → estado="Finalizado" → propiedad=NO CAMBIA        ❌ BUG
    Actualizar Contrato → estado="Cancelado"  → propiedad=NO CAMBIA        ❌ BUG

  TERMINACIÓN DIRECTA (toggle_estado UI):
    Terminar Contrato → estado="Cancelado" → propiedad=DISPONIBLE (app)    ✅ funciona
    Terminar Contrato → estado="Finalizado" → NO EXISTE                    ❌ no implementado

  DESOCUPACIÓN:
    Finalizar Desocupación → contrato="Finalizado" → propiedad=SOLO TRIGGER ❌❌

  RENOVACIÓN:
    Renovar Contrato → estado="Activo" → propiedad=NO CAMBIA               ✅ correcto
```

---

## 3. ANÁLISIS DE CAUSA RAÍZ

### RCA‑01: Dependencia implícita en triggers de BD

**Causa**: Durante la migración de SQLite a PostgreSQL (Railway), se crearon funciones/triggers (`trg_actualizar_disponibilidad_ocupada`, `trg_actualizar_disponibilidad_libre`). Paralelamente, el servicio de desocupación fue implementado asumiendo que el trigger liberaría la propiedad automáticamente. Posteriormente, otros triggers (`trg_sync_fechas_mandato`, `trg_sync_canon_arrendamiento`) fueron explícitamente eliminados (`20260519_drop_business_triggers.sql`), pero la desocupación nunca fue actualizada para manejar la sincronización desde app layer.

**Cadena de fallo**:
1. Usuario completa desocupación → servicio de desocupación marca contrato como `Finalizado`
2. Servicio **confía** en trigger `TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE`
3. Si el trigger no existe en Railway, o la función no fue migrada → **propiedad nunca se libera**
4. La propiedad queda `OCUPADA` permanentemente (inconsistencia silenciosa)

### RCA‑02: Omisión de sincronización en actualización genérica

**Causa**: `_ejecutar_actualizacion_arrendamiento` fue diseñado para sincronizar canon y fechas (cascada a mandato/propiedad), pero nunca se implementó la detección de transiciones de estado. El método acepta `datos.get("estado")` y lo asigna ciegamente sin reaccionar al cambio semántico.

### RCA‑03: Erosión arquitectónica por crecimiento incremental

**Causa**: El sistema creció agregando capas sin refactorizar las existentes:
- Triggers SQLite → migrados a PostgreSQL (parcialmente)
- Nueva capa de servicios de aplicación → agregada sin eliminar triggers redundantes
- UI State validations → agregadas como parche temporal sin mover al service layer
- Dependencias heredadas SQLite → nunca reemplazadas por Postgres

---

## 4. ARQUITECTURA ACTUAL VS PROPUESTA

### 4.1 Actual (Anti-Patrones)

| Aspecto | Actual |
|---------|--------|
| **Source of Truth** | Dual (app + triggers) |
| **Sincronización** | Distribuida, duplicada, implícita |
| **Estados** | Strings mágicos: `"Activo"`, `"Finalizado"` |
| **Validaciones negocio** | UI State (bypassable) |
| **Transacciones** | Parciales (algunos servicios, no todos) |
| **Triggers** | De negocio + auditoría mezclados |
| **Cache** | Invalidación incompleta |
| **Compatibilidad BD** | SQLite + Postgres híbrido (deprecated paths) |

### 4.2 Propuesta (Target Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND REFLEX (sin lógica de negocio)                      │
│  • Solo llama servicios                                      │
│  • Sin validaciones de dominio                               │
│  • Cache invalidada desde service layer                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│ SINGLE SOURCE OF TRUTH                                      │
│ ServicioContratoArrendamiento (único orquestador)            │
│                                                             │
│  crear_arrendamiento()    → propiedad=OCUPADA  (app only)   │
│  actualizar_arrendamiento() → detecta transición estado     │
│  terminar_arrendamiento() → propiedad=DISPONIBLE (todo)     │
│  renovar_arrendamiento() → extiende, no cambia ocupación   │
│                                                             │
│ ServicioDesocupaciones (orquestador c/consciencia)          │
│  finalizar_desocupacion() → marca Finalizado + LIBERA app   │
│                                                             │
│ ServicioPropiedades (receptor de cascada)                   │
│  actualizar_propiedad() → canon change → cascada contratos  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│ REPOSITORIOS (PostgreSQL puro)                               │
│  • Sin lógica de negocio (CRUD puro)                         │
│  • Sin triggers de negocio                                   │
│  • Solo triggers de auditoría                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│ POSTGRESQL (Railway)                                         │
│  • CHECK constraints en DISPONIBILIDAD_PROPIEDAD             │
│  • Unique constraint: 1 contrato activo por propiedad        │
│  • Foreign keys con ON DELETE RESTRICT                       │
│  • Trigger de auditoría (solo INSERT/UPDATE/DELETE log)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. ESTRATEGIA DE REMEDIACIÓN DETALLADA

### 5.1 Centralización de Sincronización (Patrón: Single Writer)

**Objetivo**: Toda escritura de `disponibilidad_propiedad` pasa por un único método en `ServicioContratoArrendamiento`.

**Implementación**:

```python
# NUEVO método privado en ServicioContratoArrendamiento
def _sincronizar_disponibilidad_por_estado(
    self,
    contrato: ContratoArrendamiento,
    estado_anterior: str,
    estado_nuevo: str,
    usuario: str
) -> None:
    """
    Único punto de sincronización de disponibilidad.
    Detecta transiciones de estado y actualiza propiedad atómicamente.
    """
    ESTADOS_TERMINALES = {"Finalizado", "Cancelado", "Inactivo", "Vencido"}

    # Transición: Activo → Terminal → Liberar propiedad
    if estado_anterior == "Activo" and estado_nuevo in ESTADOS_TERMINALES:
        propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
        if propiedad and propiedad.disponibilidad_propiedad != 1:
            propiedad.disponibilidad_propiedad = 1  # DISPONIBLE
            self.repo_propiedad.actualizar(propiedad, usuario)
            self._invalidar_cache_propiedad(contrato.id_propiedad)

    # Transición: Terminal → Activo → Ocupar propiedad (re-activación)
    elif estado_anterior in ESTADOS_TERMINALES and estado_nuevo == "Activo":
        propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
        if propiedad and propiedad.disponibilidad_propiedad != 0:
            propiedad.disponibilidad_propiedad = 0  # OCUPADA
            self.repo_propiedad.actualizar(propiedad, usuario)
            self._invalidar_cache_propiedad(contrato.id_propiedad)
```

### 5.2 Eliminación de Triggers de Negocio

**Acción**: Drop `TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA` y `TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE`

```sql
-- Migration: V20260525_remove_business_triggers.sql
DROP TRIGGER IF EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA ON CONTRATOS_ARRENDAMIENTOS;
DROP TRIGGER IF EXISTS TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE ON CONTRATOS_ARRENDAMIENTOS;
DROP FUNCTION IF EXISTS trg_actualizar_disponibilidad_ocupada();
DROP FUNCTION IF EXISTS trg_actualizar_disponibilidad_libre();
```

### 5.3 Normalización de Estados (Enum fuerte)

```python
# src/dominio/constantes/estados_contrato.py
class EstadoContratoArrendamiento(str, Enum):
    BORRADOR = "BORRADOR"
    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"
    RENOVADO = "RENOVADO"

    @property
    def es_terminal(self) -> bool:
        return self in {
            EstadoContratoArrendamiento.FINALIZADO,
            EstadoContratoArrendamiento.CANCELADO,
        }

    @property
    def es_activo(self) -> bool:
        return self == EstadoContratoArrendamiento.ACTIVO
```

### 5.4 Refactor de ServicioDesocupaciones

**Antes** (líneas 271-283):
```python
# El trigger TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE se encargará de liberar la propiedad.
```

**Después**:
```python
# Liberar propiedad explícitamente
propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
if propiedad:
    propiedad.disponibilidad_propiedad = 1  # DISPONIBLE
    self.repo_propiedad.actualizar(propiedad, usuario)
```

### 5.5 Cache Invalidation Strategy

```python
# Invalidación centralizada
def _invalidar_cache_propiedad(self, id_propiedad: int):
    cache_manager.invalidate("propiedades:list")
    cache_manager.invalidate("propiedades:list_paginated")
    cache_manager.invalidate(f"propiedad:{id_propiedad}")
    cache_manager.invalidate("dashboard:propiedades_tipo")
```

### 5.6 PostgreSQL Constraints Defensivos

```sql
-- 1. CHECK: DISPONIBILIDAD solo 0 o 1
ALTER TABLE PROPIEDADES
ADD CONSTRAINT chk_disponibilidad_valida
CHECK (DISPONIBILIDAD_PROPIEDAD IN (0, 1));

-- 2. Partial UNIQUE: solo 1 contrato ACTIVO por propiedad
CREATE UNIQUE INDEX uq_contrato_activo_por_propiedad
ON CONTRATOS_ARRENDAMIENTOS (ID_PROPIEDAD)
WHERE ESTADO_CONTRATO_A = 'Activo';

-- 3. Trigger de defensa (opcional, defense in depth)
CREATE OR REPLACE FUNCTION fn_defensa_disponibilidad()
RETURNS TRIGGER AS $$
BEGIN
    -- Si el trigger de defensa detecta inconsistencia, la corrige
    -- y LOGEA en AUDITORIA_CAMBIOS
    IF NEW.ESTADO_CONTRATO_A IN ('FINALIZADO', 'CANCELADO')
       AND OLD.ESTADO_CONTRATO_A = 'ACTIVO' THEN
        UPDATE PROPIEDADES
        SET DISPONIBILIDAD_PROPIEDAD = 1
        WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
          AND DISPONIBILIDAD_PROPIEDAD = 0;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. SQL AUDIT SCRIPTS — Diagnóstico de Inconsistencias Históricas

### 6.1 Propiedades OCUPADAS sin contrato ACTIVO

```sql
SELECT
    p.ID_PROPIEDAD,
    p.MATRICULA_INMOBILIARIA,
    p.DIRECCION_PROPIEDAD,
    p.DISPONIBILIDAD_PROPIEDAD,
    'OCUPADA_SIN_CONTRATO' as TIPO_INCONSISTENCIA
FROM PROPIEDADES p
WHERE p.DISPONIBILIDAD_PROPIEDAD = FALSE
  AND p.ESTADO_REGISTRO = TRUE
  AND NOT EXISTS (
      SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
      WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        AND ca.ESTADO_CONTRATO_A = 'Activo'
  );
```

### 6.2 Propiedades DISPONIBLES con contrato ACTIVO

```sql
SELECT
    p.ID_PROPIEDAD,
    p.DIRECCION_PROPIEDAD,
    ca.ID_CONTRATO_A,
    ca.ESTADO_CONTRATO_A,
    p.DISPONIBILIDAD_PROPIEDAD,
    'DISPONIBLE_CON_CONTRATO' as TIPO_INCONSISTENCIA
FROM PROPIEDADES p
INNER JOIN CONTRATOS_ARRENDAMIENTOS ca
    ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
WHERE p.DISPONIBILIDAD_PROPIEDAD = TRUE
  AND ca.ESTADO_CONTRATO_A = 'Activo';
```

### 6.3 Contratos FINALIZADOS/CANCELADOS con propiedad OCUPADA

```sql
SELECT
    ca.ID_CONTRATO_A,
    ca.ESTADO_CONTRATO_A,
    ca.FECHA_FIN_CONTRATO_A,
    p.ID_PROPIEDAD,
    p.DISPONIBILIDAD_PROPIEDAD,
    'TERMINADO_SIN_LIBERAR' as TIPO_INCONSISTENCIA
FROM CONTRATOS_ARRENDAMIENTOS ca
INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
WHERE ca.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado')
  AND p.DISPONIBILIDAD_PROPIEDAD = FALSE;
```

### 6.4 Contratos ACTIVOS sin propiedad OCUPADA

```sql
SELECT
    ca.ID_CONTRATO_A,
    ca.ESTADO_CONTRATO_A,
    ca.FECHA_INICIO_CONTRATO_A,
    p.ID_PROPIEDAD,
    p.DISPONIBILIDAD_PROPIEDAD,
    'ACTIVO_SIN_OCUPAR' as TIPO_INCONSISTENCIA
FROM CONTRATOS_ARRENDAMIENTOS ca
INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
WHERE ca.ESTADO_CONTRATO_A = 'Activo'
  AND p.DISPONIBILIDAD_PROPIEDAD = TRUE;
```

### 6.5 Propiedades con múltiples contratos ACTIVOS

```sql
SELECT
    ca.ID_PROPIEDAD,
    p.DIRECCION_PROPIEDAD,
    COUNT(*) as CONTRATOS_ACTIVOS,
    STRING_AGG(ca.ID_CONTRATO_A::TEXT, ', ') as IDS_CONTRATOS
FROM CONTRATOS_ARRENDAMIENTOS ca
INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
WHERE ca.ESTADO_CONTRATO_A = 'Activo'
GROUP BY ca.ID_PROPIEDAD, p.DIRECCION_PROPIEDAD
HAVING COUNT(*) > 1;
```

### 6.6 Resumen consolidado de inconsistencias

```sql
WITH
ocupadas_sin_contrato AS (
    SELECT p.ID_PROPIEDAD FROM PROPIEDADES p
    WHERE p.DISPONIBILIDAD_PROPIEDAD = FALSE
      AND NOT EXISTS (SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD AND ca.ESTADO_CONTRATO_A = 'Activo')
),
disponibles_con_contrato AS (
    SELECT p.ID_PROPIEDAD FROM PROPIEDADES p
    JOIN CONTRATOS_ARRENDAMIENTOS ca ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
    WHERE p.DISPONIBILIDAD_PROPIEDAD = TRUE AND ca.ESTADO_CONTRATO_A = 'Activo'
),
terminados_ocupados AS (
    SELECT p.ID_PROPIEDAD FROM CONTRATOS_ARRENDAMIENTOS ca
    JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
    WHERE ca.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado') AND p.DISPONIBILIDAD_PROPIEDAD = FALSE
),
multiples_activos AS (
    SELECT ca.ID_PROPIEDAD FROM CONTRATOS_ARRENDAMIENTOS ca
    WHERE ca.ESTADO_CONTRATO_A = 'Activo'
    GROUP BY ca.ID_PROPIEDAD HAVING COUNT(*) > 1
)
SELECT
    'OCUPADA_SIN_CONTRATO' as INCONSISTENCIA, COUNT(*) as TOTAL FROM ocupadas_sin_contrato
UNION ALL
SELECT 'DISPONIBLE_CON_CONTRATO', COUNT(*) FROM disponibles_con_contrato
UNION ALL
SELECT 'TERMINADO_SIN_LIBERAR', COUNT(*) FROM terminados_ocupados
UNION ALL
SELECT 'MULTIPLES_ACTIVOS', COUNT(*) FROM multiples_activos;
```

---

## 7. PLAN DE REMEDIACIÓN HISTÓRICA

Una vez aplicados los fixes, ejecutar en orden:

```sql
-- PASO 1: Propiedades OCUPADAS sin contrato ACTIVO → DISPONIBLE
UPDATE PROPIEDADES p
SET DISPONIBILIDAD_PROPIEDAD = TRUE,
    UPDATED_AT = CURRENT_TIMESTAMP,
    UPDATED_BY = 'DATA_REMEDIATION_2026'
WHERE p.DISPONIBILIDAD_PROPIEDAD = FALSE
  AND p.ESTADO_REGISTRO = TRUE
  AND NOT EXISTS (
      SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
      WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        AND ca.ESTADO_CONTRATO_A = 'Activo'
  );

-- PASO 2: Propiedades DISPONIBLES con contrato ACTIVO → OCUPADA
UPDATE PROPIEDADES p
SET DISPONIBILIDAD_PROPIEDAD = FALSE,
    UPDATED_AT = CURRENT_TIMESTAMP,
    UPDATED_BY = 'DATA_REMEDIATION_2026'
FROM CONTRATOS_ARRENDAMIENTOS ca
WHERE p.ID_PROPIEDAD = ca.ID_PROPIEDAD
  AND ca.ESTADO_CONTRATO_A = 'Activo'
  AND p.DISPONIBILIDAD_PROPIEDAD = TRUE;

-- PASO 3: Auditoría post-remediación (re-ejecutar queries de diagnóstico)
-- Si TOTAL = 0 en todas las categorías, la remediación fue exitosa.
```

---

## 8. EVALUACIÓN DE RIESGOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| **R01**: Trigger de BD no existe en Railway | Alta | Crítico | Ejecutar diagnosis inmediata; fix app layer como prioridad |
| **R02**: Datos históricos corruptos | Alta | Alto | Auditoría SQL previa y remediación controlada |
| **R03**: Race condition durante migración (doble escritura app+trigger) | Media | Medio | Eliminar triggers ANTES de deployar nuevo código app |
| **R04**: Cache stale post-remediación | Media | Medio | Invalidación global forzada post-deploy |
| **R05**: Rollback necesario | Baja | Alto | Todos los cambios son aditivos (no se eliminan columnas) |
| **R06**: Contratos con estados inconsistentes (Activo vs ACTIVO) | Alta | Medio | Normalización via script de migración |

---

## 9. ROADMAP TÉCNICO POR FASES

### FASE 0 — Auditoría y Línea Base

- [x] **0.1** Ejecutar queries de auditoría en Railway
- [x] **0.2** Verificar existencia de triggers en Railway (`information_schema.triggers`)
- [x] **0.3** Backup completo de BD (`pg_dump`)
- [x] **0.4** Snapshot del estado actual de contratos/propiedades (CSV export)

**Duración**: 1 día | **Responsable**: Backend | **Riesgo**: Ninguno

---

### FASE 1 — Corrección Crítica

- [x] **1.1** Agregar `_sincronizar_disponibilidad_por_estado()` en `servicio_contrato_arrendamiento.py`
- [x] **1.2** Modificar `_ejecutar_actualizacion_arrendamiento()` para detectar transiciones de estado
- [x] **1.3** Modificar `terminar_arrendamiento()` para manejar `Finalizado` además de `Cancelado`
- [x] **1.4** Modificar `finalizar_desocupacion()` para liberar propiedad desde app layer
- [x] **1.5** Reemplazar `RepositorioPropiedadSQLite` por `RepositorioPropiedadPostgres` en desocupación

**Archivos afectados**:
- `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- `src/aplicacion/servicios/servicio_desocupaciones.py`

**Duración**: 2 días | **Prioridad**: 🔴 CRÍTICA

---

### FASE 2 — Sincronización y Transaccionalidad

- [x] **2.1** Agregar `@idempotent` y transacción a `terminar_arrendamiento`
- [x] **2.2** Centralizar invalidación de caché en método privado `_invalidar_cache_propiedad`
- [x] **2.3** Agregar invalidación de caché de propiedades en todos los flujos
- [x] **2.4** Verificar transacción atómica en desocupación (ya existe, confirmar)

**Archivos afectados**:
- `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`

**Duración**: 2 días | **Prioridad**: 🟡 ALTA

---

### FASE 3 — Eliminación de Triggers y Refactor DB

- [x] **3.1** Crear migration `V20260525_01_drop_business_triggers.sql`
- [x] **3.2** Crear migration `V20260525_02_add_check_constraints.sql`
- [x] **3.3** Crear migration `V20260525_03_add_unique_index.sql`
- [x] **3.4** Ejecutar migrations en Railway
- [x] **3.5** Verificar que no haya triggers de negocio remanentes

**Archivos afectados**:
- `migraciones/sql/V20260525_01_drop_business_triggers.sql`
- `migraciones/sql/V20260525_02_add_check_constraints.sql`
- `migraciones/sql/V20260525_03_add_unique_index.sql`

**Duración**: 1 día | **Prioridad**: 🟡 ALTA

---

### FASE 4 — Normalización de Estados

- [x] **4.1** Actualizar `EstadoContrato` enum en `estados_contrato.py`
- [x] **4.2** Migrar entidad `ContratoArrendamiento` a usar enum tipado
- [x] **4.3** Actualizar repositorio para mapeo de estados
- [x] **4.4** Crear migration SQL para normalizar estados existentes en BD
- [x] **4.5** Actualizar servicios para usar el nuevo enum
- [x] **4.6** Actualizar state de Reflex para compatibilidad con enum

**Archivos afectados**:
- `src/dominio/constantes/estados_contrato.py`
- `src/dominio/entidades/contrato_arrendamiento.py`
- `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py`
- `src/aplicacion/servicios/servicio_contrato_arrendamiento.py`
- `src/presentacion_reflex/state/contratos_state.py`

**Duración**: 2 días | **Prioridad**: 🟡 MEDIA

---

### FASE 5 — Refactor de Validaciones UI → Service

- [x] **5.1** Mover validación de disponibilidad a `ServicioPropiedades`
- [x] **5.2** Mover validación de contrato activo a `ServicioPropiedades`
- [x] **5.3** Remover lógica duplicada de `propiedades_state.py` (líneas 695-706, 743-753)
- [x] **5.4** Simplificar `propiedades_state.py` (remover lógica de negocio)

**Archivos afectados**:
- `src/aplicacion/servicios/servicio_propiedades.py`
- `src/presentacion_reflex/state/propiedades_state.py`

**Duración**: 1 día | **Prioridad**: 🟡 MEDIA

---

### FASE 6 — Data Remediation

- [x] **6.1** Ejecutar script de remediación histórica en Railway
- [x] **6.2** Re-ejecutar diagnóstico post-remediación
- [x] **6.3** Generar reporte de datos corregidos

**Duración**: 1 día | **Prioridad**: 🔴 CRÍTICA

---

### FASE 7 — Testing y QA

- [ ] **7.1** Tests unitarios: `_sincronizar_disponibilidad_por_estado`
- [ ] **7.2** Tests de integración: flujo completo crear → terminar
- [ ] **7.3** Tests de integración: desocupación → propiedad liberada
- [ ] **7.4** Tests de regresión: actualización sin cambio de estado
- [ ] **7.5** QA funcional: validación manual en staging (QA-01 a QA-06)
- [ ] **7.6** Verificar cobertura de tests > 90%

**Duración**: 2 días | **Prioridad**: 🔴 CRÍTICA

---

## 10. ARCHIVOS AFECTADOS

### Backend (Python) — Modificar

| Archivo | Cambio | Riesgo | Fase |
|---------|--------|--------|------|
| `src/aplicacion/servicios/servicio_contrato_arrendamiento.py` | Nuevo método `_sincronizar_disponibilidad_por_estado` + modificar 3 métodos | Alto | 1, 2 |
| `src/aplicacion/servicios/servicio_desocupaciones.py` | Modificar `finalizar_desocupacion` + `__init__` (SQLite→Postgres) | Alto | 1 |
| `src/aplicacion/servicios/servicio_propiedades.py` | Mover validaciones de disponibilidad desde State | Medio | 5 |
| `src/aplicacion/servicios/servicio_contrato_mandato.py` | Verificar que `terminar_mandato` no requiera tocar propiedad | Bajo | 2 |
| `src/dominio/constantes/estados_contrato.py` | Refactor completo del enum `EstadoContratoArrendamiento` | Medio | 4 |
| `src/dominio/entidades/contrato_arrendamiento.py` | Cambiar `estado_contrato_a: str` → `EstadoContratoArrendamiento` | Medio | 4 |
| `src/infraestructura/persistencia/repositorio_contrato_arrendamiento_postgres.py` | Adaptar mapeo de estados al nuevo enum | Bajo | 4 |
| `dominio/repositorios/interfaces.py` | Validar compatibilidad de tipos | Bajo | 4 |

### Frontend (Reflex State) — Modificar

| Archivo | Cambio | Riesgo | Fase |
|---------|--------|--------|------|
| `src/presentacion_reflex/state/propiedades_state.py` | Remover validaciones de negocio duplicadas (líneas 695-706, 743-753) | Medio | 5 |
| `src/presentacion_reflex/state/contratos_state.py` | Validar que `toggle_estado` use correctamente el servicio | Bajo | 4 |

### Database (PostgreSQL) — Crear

| Archivo | Cambio | Riesgo | Fase |
|---------|--------|--------|------|
| `migraciones/sql/V20260525_01_drop_business_triggers.sql` | DROP triggers de negocio | Medio | 3 |
| `migraciones/sql/V20260525_02_add_check_constraints.sql` | ALTER TABLE ADD CONSTRAINT | Bajo | 3 |
| `migraciones/sql/V20260525_03_add_unique_index.sql` | CREATE UNIQUE INDEX | Bajo | 3 |

---

## 11. SERVICIOS IMPACTADOS

| Servicio | Impacto | Tipo | Fase |
|----------|---------|------|------|
| `ServicioContratoArrendamiento` | 🔴 Alto | Modificación estructural + nuevo método | 1, 2, 4 |
| `ServicioDesocupaciones` | 🔴 Alto | Fix crítico de liberación de propiedad | 1 |
| `ServicioPropiedades` | 🟡 Medio | Refactor de validaciones | 5 |
| `ServicioContratoMandato` | 🟢 Bajo | Solo verificación | 2 |
| `ServicioDashboard` | 🟡 Medio | KPIs de disponibilidad pueden cambiar post-remediación | 6 |
| `ServicioLiquidacion` | 🟢 Bajo | Impacto indirecto (estado ocupación afecta cálculos) | — |
| `ServicioRecaudo` | 🟢 Bajo | Impacto indirecto | — |
| `ServicioDocumental` | 🟢 Bajo | Certificados de paz y salvo | — |
| `ServicioNotificaciones` | 🟢 Bajo | Alertas de disponibilidad | — |

---

## 12. CAMBIOS REQUERIDOS POR CAPA

### 12.1 Backend — ServicioContratoArrendamiento

```python
# 1. NUEVO MÉTODO
def _sincronizar_disponibilidad_por_estado(
    self, contrato, estado_anterior, estado_nuevo, usuario
) -> None:
    ...

# 2. MODIFICAR _ejecutar_actualizacion_arrendamiento
#   - Capturar estado_anterior ANTES de la asignación
#   - Llamar a _sincronizar_disponibilidad_por_estado después de la asignación

# 3. MODIFICAR terminar_arrendamiento
#   - Aceptar estado destino como parámetro (default "Cancelado")
#   - Soportar "Finalizado", "Cancelado", "Inactivo"
#   - Llamar a _sincronizar_disponibilidad_por_estado

# 4. MODIFICAR crear_arrendamiento
#   - Reemplazar lógica inline de disponibilidad=0 por llamada a _sincronizar

# 5. Agregar invalidación de caché de propiedades
def _invalidar_cache_propiedades(self, id_propiedad=None):
    ...
```

### 12.2 Backend — ServicioDesocupaciones

```python
# MODIFICAR finalizar_desocupacion (después de actualizar contrato a Finalizado)
#   - Obtener propiedad por ID_PROPIEDAD del contrato
#   - Setear disponibilidad_propiedad = 1
#   - Actualizar propiedad en repositorio

# MODIFICAR __init__
#   - Cambiar RepositorioPropiedadSQLite → RepositorioPropiedadPostgres
```

### 12.3 Frontend — PropiedadesState

```python
# REMOVER en save_propiedad (líneas 695-706):
query_check_arr = "SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = %s AND ESTADO_CONTRATO_A = 'Activo'"
# REPLACED by: ServicioPropiedades.validar_disponibilidad()

# REMOVER en toggle_disponibilidad (líneas 743-753):
# REPLACED by: ServicioPropiedades.cambiar_disponibilidad()
```

---

## 13. ESTRATEGIA DE TRANSACCIÓN Y ROLLBACK

### 13.1 Estrategia Transaccional (Atómica)

```python
# Patrón a seguir en TODOS los métodos que modifican estado:
def terminar_arrendamiento(self, id_contrato, motivo, usuario):
    db = getattr(self.repo_arriendo, "db", None)
    if db is None:
        self._ejecutar_terminacion_arrendamiento(id_contrato, motivo, usuario)
        return
    with db.transaccion():
        self._ejecutar_terminacion_arrendamiento(id_contrato, motivo, usuario)
```

### 13.2 Rollback Plan

| Escenario | Acción |
|-----------|--------|
| **Hotfix**: Bug en producción post-deploy | Revertir solo los commits de Fase 1 via `git revert` + redeploy Railway |
| **Migration DB**: Error en constraints | `ALTER TABLE ... DROP CONSTRAINT IF EXISTS chk_disponibilidad_valida` |
| **Data Remediation**: Error en UPDATE | Restaurar desde `pg_dump` pre-ejecución |
| **Trigger Drop**: Error en app layer | Re-crear triggers via `restore_db_objects.py` |
| **Rollback total**: Fallo catastrófico | Restore completo de BD + `git checkout HEAD~1` + redeploy |

---

## 14. ESTRATEGIA DE TESTING

### 14.1 Tests Unitarios

```
test_servicio_contrato_arrendamiento.py:
  ✓ test_sincronizar_disponibilidad_activo_a_finalizado
  ✓ test_sincronizar_disponibilidad_activo_a_cancelado
  ✓ test_sincronizar_disponibilidad_sin_cambio_de_estado
  ✓ test_sincronizar_disponibilidad_estado_terminal_a_activo
  ✓ test_terminar_arrendamiento_con_estado_finalizado
  ✓ test_terminar_arrendamiento_con_estado_cancelado
  ✓ test_crear_arrendamiento_sincroniza_disponibilidad

test_servicio_desocupaciones.py:
  ✓ test_finalizar_desocupacion_libera_propiedad
  ✓ test_finalizar_desocupacion_sin_trigger
```

### 14.2 Tests de Integración

```
test_flujo_completo_contrato_propiedad.py:
  ✓ test_crear_contrato → propiedad_ocupada
  ✓ test_terminar_contrato → propiedad_disponible
  ✓ test_finalizar_desocupacion → propiedad_disponible
  ✓ test_actualizar_contrato_con_cambio_estado → propiedad_sincronizada
  ✓ test_actualizar_contrato_sin_cambio_estado → propiedad_no_cambia
```

### 14.3 Tests de Regresión

```
test_regresion_contratos.py:
  ✓ test_renovar_contrato_no_cambia_disponibilidad
  ✓ test_actualizar_canon_no_cambia_disponibilidad
  ✓ test_actualizar_datos_arrendatario_no_cambia_disponibilidad
```

---

## 15. PLAN DE VALIDACIÓN FUNCIONAL QA

- [ ] **QA-01: Flujo de Creación de Contrato**
  - Crear arrendamiento → propiedad OCUPADA en dashboard → DISPONIBILIDAD = 0
- [ ] **QA-02: Flujo de Terminación Directa**
  - Cancelar contrato → contrato Cancelado → propiedad DISPONIBLE
- [ ] **QA-03: Flujo de Desocupación**
  - Iniciar desocupación → completar checklist → Finalizar → contrato Finalizado → propiedad DISPONIBLE
- [ ] **QA-04: Flujo de Actualización**
  - Cambiar solo canon → disponibilidad no cambia
  - Cambiar estado a Finalizado → disponibilidad cambia a DISPONIBLE
- [ ] **QA-05: Dashboard y KPIs**
  - KPIs de disponibilidad reflejan estado correcto post-sincronización
- [ ] **QA-06: Cache**
  - Crear/terminar contrato → recargar página → datos consistentes

---

## 16. CRITERIOS DE ÉXITO (SUCCESS METRICS)

| Métrica | Target | Cómo se mide | Fase |
|---------|--------|-------------|------|
| **Consistencia**: 0 propiedades con estado inconsistente | 100% | Ejecutar queries de auditoría (Sección 6.6) | 6 |
| **Latencia**: Tiempo de sincronización contrato→propiedad | <500ms | Logs de aplicación | 2 |
| **Disponibilidad**: Propiedades correctamente clasificadas | 100% | Dashboard de KPIs | 6 |
| **Cobertura de tests**: Unitarios + Integración | >90% | `pytest --cov` | 7 |
| **Regresión**: Tests pre-existentes pasan | 100% | `pytest` suite completa | 7 |
| **Transaccionalidad**: Rollback en caso de error | Confirmado | Test de integración con inyección de fallo | 2 |
| **Cache**: Propiedades refrescadas post-sincronización | Confirmado | Verificación manual en UI | 2 |
| **Zero triggers**: 0 triggers de negocio en BD | Confirmado | `information_schema.triggers` | 3 |

---

## 17. GO / NO-GO CRITERIA

### GO Criteria (todos deben cumplirse)

- [ ] **G1** — Auditoría SQL inicial ejecutada y documentada
- [ ] **G2** — Backup completo de BD verificado
- [ ] **G3** — Todos los tests unitarios pasan en CI (pre-fix)
- [ ] **G4** — Fase 1 implementada y probada en staging
- [ ] **G5** — Validación funcional QA-01 a QA-06 superada
- [ ] **G6** — Queries de auditoría post-fix muestran 0 inconsistencias
- [ ] **G7** — Rollback script verificado
- [ ] **G8** — Aprobación de code review

### NO-GO Triggers (cualquiera detiene el deploy)

| # | Trigger | Acción |
|---|---------|--------|
| NG1 | Auditoría inicial muestra >10% de datos inconsistentes | Detener, evaluar remediación manual primero |
| NG2 | Tests de regresión fallan | Detener, corregir, re-ejecutar |
| NG3 | Falla en Railway post-deploy de triggers DROP | Rollback inmediato, re-crear triggers |
| NG4 | Error transaccional detectado en staging | Detener, revisar lógica transaccional |

---

## 18. RESUMEN DE RIESGOS OPERATIVOS POST-REMEDIACIÓN

| Riesgo | Antes | Después |
|--------|-------|---------|
| Propiedad no liberada al finalizar contrato | **Alto** (depende del trigger) | **Nulo** (app layer) |
| Doble escritura de disponibilidad | **Medio** (app + trigger) | **Nulo** (solo app) |
| Bypass de validaciones via API directa | **Alto** (validación en UI) | **Nulo** (validación en Service) |
| Inconsistencia histórica | **Alto** (sin remediación) | **Bajo** (post-remediación) |
| Estados denormalizados | **Medio** (strings) | **Bajo** (enum tipado) |
| Cache stale | **Medio** (invalidación incompleta) | **Mínimo** (invalidación centralizada) |
| Dependencia SQLite en producción | **Alto** (código heredado) | **Nulo** (Postgres puro) |

---

## 19. MATRIZ DE DEPENDENCIAS ENTRE FASES

```
Fase 0 (Auditoría)
  └── Requisito para: Fase 1, Fase 6, Fase 7

Fase 1 (Corrección Crítica)
  └── Requisito para: Fase 2, Fase 3, Fase 6
  └── Se puede deployar independientemente (hotfix)

Fase 2 (Sincronización y Transaccionalidad)
  └── Requisito para: Fase 3
  └── Depende de: Fase 1

Fase 3 (Eliminación de Triggers)
  └── Depende de: Fase 1, Fase 2
  └── Solo después de que app layer maneje toda la sincronización

Fase 4 (Normalización de Estados)
  └── Independiente de Fase 1-3 (se puede hacer en paralelo)
  └── Requisito para: Fase 5

Fase 5 (Refactor UI → Service)
  └── Depende de: Fase 4
  └── Independiente de Fase 1-3

Fase 6 (Data Remediation)
  └── Depende de: Fase 1, Fase 3
  └── Solo después de que app layer + DB estén corregidos

Fase 7 (Testing y QA)
  └── Depende de: Fase 1, Fase 4, Fase 5
  └── La validación final requiere todas las fases previas
```

---

## 20. APROBACIÓN

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| **Arquitecto** | | | |
| **Backend Lead** | | | |
| **QA Lead** | | | |
| **Product Owner** | | | |

---

*Documento generado el 2026-05-25. Próxima revisión: post-Fase 0.*
