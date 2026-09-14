# Research: Fix `integer out of range` en renovación de contratos

**Feature**: `073-fix-renovacion-integer-range` | **Fecha**: 2026-09-14

Sin `NEEDS CLARIFICATION` técnicos abiertos: el stack es conocido y la causa raíz
está verificada contra la base de datos real (ver `spec.md`, sección Hallazgo).
Este documento consolida las decisiones de diseño.

## R1 — Causa raíz del `integer out of range`

- **Decision**: El fallo lo produce la expresión
  `CAST(%s * comision_porcentaje / 10000.0 AS INTEGER)` en
  `actualizar_canon_liquidaciones_futuras`
  (`src/aplicacion/servicios/servicio_contrato_arrendamiento.py`, paso 7 de la
  renovación). PostgreSQL evalúa `integer × integer` antes de dividir; con
  canon 2.300.000 × comisión 1000 = 2.300.000.000 > 2.147.483.647 (máx. int4)
  la sentencia aborta y la transacción revierte la renovación completa.
- **Rationale**: Reproducción H1 con la expresión exacta falla; control H3 con
  canon 900.000 funciona; `H2` con `::BIGINT` retorna 230.000 correcto.
  Explica por qué solo fallan contratos de canon alto (caso índice: contrato 73).
- **Alternatives considered**:
  - Dato corrupto del contrato / fechas / IPC → descartado (muestra y tipos
    verificados; IPC 5.1–5.2 vigente; el control por magnitud aísla la causa).
  - Desbordamiento en `porcentaje_incremento=int(pct*100)` o en canon nuevo en
    Python → descartado (valores de cientos; Python int sin límite).

## R2 — Estrategia de corrección del cálculo

- **Decision**: Ensanchar el cómputo intermedio a 64 bits dentro de la misma
  consulta (castear el parámetro canon antes de multiplicar) y mantener el
  `CAST(... AS INTEGER)` final, que preserva la regla de truncamiento vigente
  (aclaración Q4) y los tipos de columna sin migración (aclaración Q1).
- **Rationale**: Cambio mínimo y atómico (~2 expresiones SQL); el resultado
  final siempre cabe en int4 para los rangos soportados; no altera ni un peso
  de la historia existente.
- **Alternatives considered**:
  - Migrar columnas a BIGINT → rechazado (aclaración Q1; riesgo mayor,
    requiere plan propio).
  - Dividir antes de multiplicar (`canon/10000.0*comision`) → rechazado:
    introduce decimales intermedios y cambia resultados por truncamiento
    respecto a la historia.

## R3 — Validación previa con mensaje operativo

- **Decision**: Validar en la capa de aplicación, antes de persistir, que cada
  valor derivado cabe en su columna destino; si excede, elevar excepción de
  dominio con campo + valor y mapearla en el estado a mensaje operativo en
  lenguaje no técnico, nunca el error crudo (aclaración Q2, FR-003). Valores
  sobre los máximos observados (canon > $10.000.000, comisión > 1500) se
  rechazan por esta vía (aclaración Q5).
- **Rationale**: Fail-fast en español, testeable sin base de datos, coherente
  con la política de excepciones de dominio y sin `except Exception` genérico.
- **Alternatives considered**: Solo mensaje genérico + log interno → rechazado
  (aclaración Q2: el operador necesita campo y valor para corregir datos).

## R4 — Alcance: patrones afines descartados

- **Decision**: Único punto a corregir en SQL: las dos expresiones de comisión /
  IVA de la propagación. Verificados y fuera de alcance:
  `servicio_financiero.py:193` (int de Python, sin límite), dashboard
  (`CANON * (comision/10000.0)`, división primero → numeric, sin overflow),
  `RECAUDO_CONCEPTOS`/`RECAUDOS`/auditoría (asignaciones directas o columna
  numeric). Renovación de mandato: mismo estándar de validación (FR-009) sin
  cambios SQL propios.
- **Rationale**: Barrido de `* comision_porcentaje`, `/ 10000` y `AS INTEGER`
  en `src/` (13 coincidencias, solo 2 riesgosas).

## R5 — Estrategia de pruebas

- **Decision**: Nuevo test de integración de propagación con magnitudes
  límite (2.300.000×1000 y 10.000.000×1500) sobre datos desechables +
  re-ejecución de suites existentes de renovación (unit/integration:
  idempotencia, atomicidad, consecutiva, concurrencia, flujo completo,
  errores) + verificación de propagación cero-inconsistencias.
- **Rationale**: Las suites existentes cubren regresión; falta el caso límite
  que reproduce el bug. Los tests de integración usan BD de prueba
  (constitución §5), nunca producción.
- **Alternatives considered**: Probar solo contra producción/staging →
  rechazado (riesgo de datos; la reproducción H1-H3 ya probó la semántica SQL
  en solo lectura).
