# ADR 002: Criterios de Elegibilidad de Liquidaciones mediante Reconstruccin de Intervalos

## Contexto
Se requiere restringir la generacin de liquidaciones a propietarios nicamente para propiedades con contratos de mandato y arrendamiento activos. Adems, la auditora histrica debe poder reconstruir este estado a la fecha de generacin.

## Decisin
Se implement la validacin en la capa de aplicacin (ServicioFinanciero) con chequeos directos en base de datos. Para la auditora (ServicioAuditoriaElegibilidad), se reconstruye el estado histrico utilizando las fechas de inicio y fin de los contratos (FECHA_INICIO_M, FECHA_FIN_M, etc.) comparadas contra la FECHA_GENERACION de cada liquidacin.

## Consecuencias
- Las consultas de auditora son ms complejas pero 100% precisas respecto al momento histrico.
- El rendimiento de generar_liquidacion_masiva mejora al filtrar tempranamente va SQL EXISTS y el JOIN en el query consolidado.

