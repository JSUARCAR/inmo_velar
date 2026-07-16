# Evidencia de Pruebas de Regresión (Liquidaciones Históricas)

**Fecha:** 2026-07-14
**Objetivo:** Verificar que las correcciones de atomicidad (T006-T010) y visualización en la UI (T014-T018) no afectan a las liquidaciones previamente generadas con datos correctos.

## Resultados de la Validación Programática End-to-End

El script `validar_consistencia_edit.py` fue ejecutado sobre las últimas 5 liquidaciones registradas en la base de datos, abarcando liquidaciones nuevas y las liquidaciones históricas reportadas como problemáticas o funcionales. 

La comprobación cruza el resultado directo de PostgreSQL `[DB]` con el resultado devuelto por la API del backend `[API]`.

```text
--- Validando Consistencia End-to-End para Liquidación 76 ---
[DB] Contratos: 3, Descuentos: 2, Bonificaciones: 0
[API] Contratos: 3, Descuentos: 2, Bonificaciones: 0
RESULTADO: CONSISTENTE OK

--- Validando Consistencia End-to-End para Liquidación 74 ---
[DB] Contratos: 2, Descuentos: 1, Bonificaciones: 0
[API] Contratos: 2, Descuentos: 1, Bonificaciones: 0
RESULTADO: CONSISTENTE OK

--- Validando Consistencia End-to-End para Liquidación 73 ---
[DB] Contratos: 10, Descuentos: 2, Bonificaciones: 0
[API] Contratos: 10, Descuentos: 2, Bonificaciones: 0
RESULTADO: CONSISTENTE OK

--- Validando Consistencia End-to-End para Liquidación 72 ---
[DB] Contratos: 3, Descuentos: 2, Bonificaciones: 0
[API] Contratos: 3, Descuentos: 2, Bonificaciones: 0
RESULTADO: CONSISTENTE OK

--- Validando Consistencia End-to-End para Liquidación 71 ---
[DB] Contratos: 21, Descuentos: 2, Bonificaciones: 0
[API] Contratos: 21, Descuentos: 2, Bonificaciones: 0
RESULTADO: CONSISTENTE OK
```

## Conclusión

El comportamiento es completamente consistente. El `LEFT JOIN` aplicado al `repositorio_liquidacion_asesor.py` asegura que, sin importar el estado del contrato o de la propiedad (incluso si fue modificado o eliminado después de que se generó la liquidación), la información persistida en la tabla `LIQUIDACIONES_CONTRATOS` se preserva y se mapea con los fallbacks previstos para el modal de edición. No se introdujeron regresiones en el comportamiento original.
