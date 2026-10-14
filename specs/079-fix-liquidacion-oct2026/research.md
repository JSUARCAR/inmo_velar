# Research: Liquidación Propietarios Octubre 2026 Invisible

**Feature**: [spec.md](spec.md) | **Date**: 2026-10-14

Sin NEEDS CLARIFICATION abiertos: todo el Technical Context se resolvió con evidencia (reproducción en PG prod + 5 clarificaciones aceptadas). Registro de decisiones:

## 1. Acceso dual a claves del cursor dict

- Decision: `row.get("TIENE_ARRIENDO", row.get("tiene_arriendo"))` (igual para `ID_CONTRATO_M` y `DIRECCION_PROPIEDAD`) en `generar_liquidacion_propietario`.
- Rationale: `UpperCaseCursorWrapper` mayusculiza claves solo en PG; SQLite preserva el alias. Evidencia: `KeyError` reproducido en Railway PG; el mismo código pasa en mocks/SQLite.
- Alternatives considered: alias SQL en MAYÚSCULAS (`AS TIENE_ARRIENDO`) — rechazado porque el wrapper ya mayusculiza y en SQLite el alias citado cambiaría el contrato de los tests existentes que usan minúsculas.

## 2. Recarga incondicional + sync de filtro tras masiva

- Decision: siempre `yield load_liquidaciones()`, con `filter_periodo = periodo` y `current_page = 1` dentro del `async with self`.
- Rationale: antes solo recargaba en vista agrupada y conservaba el filtro anterior, por lo que una masiva generada desde otro período parecía no existir.
- Alternatives considered: recargar solo si el filtro ya coincide — rechazado porque deja el síntoma "no aparece" cuando el usuario genera para un período distinto al filtrado.

## 3. Preservar LIKE (individual) vs = (agrupada)

- Decision: sin unificar (clarificación Q3 aceptada).
- Rationale: con período completo `YYYY-MM`, `LIKE '%2026-10%'` se comporta como exacto; unificar amplía el alcance y viola refactorización incremental.
- Alternatives considered: unificar ambas a `=` — diferido a tarea separada si se demuestra divergencia real.

## 4. Concurrencia idempotente sin lock

- Decision: masivas concurrentes permitidas; UNIQUE `(ID_CONTRATO_M, PERIODO)` serializa de facto y la segunda cuenta duplicados como omitidas (clarificación Q1).
- Rationale: menor cambio, usa la restricción existente, coherente con FR-003.
- Alternatives considered: lock global o cola con reintento — rechazados por complejidad innecesaria a esta escala (~64 contratos).

## 5. Margen SC-001 y fondo sin límite

- Decision: denominador = elegibles sin liquidación previa; 5% solo para transitorios reintentables (Q2); generación en background sin límite explícito con toast final (Q5).
- Rationale: separa errores reales de omitidas/no_elegibles y evita diseñar lotes/reanudación sin evidencia de necesidad.
- Alternatives considered: 100% estricto o límite 60s — rechazados por brittle ante timeouts PG de 5s por statement.

## 6. Permiso CREAR como actor

- Decision: cualquier usuario con `check_action("Liquidaciones", "CREAR")` puede disparar la masiva (Q4).
- Rationale: coincide con el gating existente del toolbar; no amplía ni restringe permisos.

## 7. Diferidos aceptados

- CHK028 (términos de implementación en el spec: `UpperCaseCursorWrapper`, `type="month"`, UNIQUE): se conservan porque son la trazabilidad exacta del bug; el mandato de español aplica al código/UI, y estos checklists son documentos de trabajo.

## 8. Comparación Individual vs Masiva (T011)

- Verificación ejecutada en PostgreSQL con datos TEST (períodos 2099-10 y 2099-11).
- Resultados: La liquidación generada individualmente (`generar_liquidacion_mensual`) y la generada de forma masiva (`generar_liquidacion_propietario`) producen valores financieros idénticos (`canon_bruto`, `comision_monto`, `total_egresos`, `neto_a_pagar`) y asignan el estado inicial 'En Proceso'. Cero divergencias estructurales detectadas.
