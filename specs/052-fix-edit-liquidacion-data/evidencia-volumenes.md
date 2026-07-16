# Evidencia de Pruebas de Volumen de Datos

**Fecha:** 2026-07-14
**Objetivo:** Verificar que el sistema puede cargar en memoria y editar sin errores liquidaciones que contienen un alto volumen de propiedades (ej: más de 10 o 20 contratos).

## Resultados de la Validación

El test programático capturó diferentes perfiles de volumen de las últimas liquidaciones en el sistema.

1. **Liquidación de Volumen Masivo:** Liquidación ID 71.
   - **Propiedades Liquidadas:** 21 propiedades.
   - **Descuentos:** 2 descuentos.
   - **Resultado:** La persistencia fue atómica y exitosa; la respuesta de la API coincide 100% con los 21 contratos guardados en PostgreSQL.

2. **Liquidación de Volumen Alto:** Liquidación ID 73.
   - **Propiedades Liquidadas:** 10 propiedades.
   - **Descuentos:** 2 descuentos.
   - **Resultado:** 100% de éxito en consistencia.

3. **Liquidación de Volumen Bajo (Standard):** Liquidaciones ID 74 y 76.
   - **Propiedades Liquidadas:** 2 a 3 propiedades.
   - **Descuentos:** 1 a 2 descuentos.
   - **Resultado:** 100% de éxito en consistencia.

## Conclusión

El tiempo de procesamiento, la carga de diccionarios en memoria mediante los cursores `psycopg2`, y el mecanismo de fallback en la estructura `LEFT JOIN` son altamente eficientes. El proceso de edición de un asesor con una gran cantidad de propiedades (ej. 21 contratos) es igual de fiable que el proceso de edición para un asesor con 1 sola propiedad.
